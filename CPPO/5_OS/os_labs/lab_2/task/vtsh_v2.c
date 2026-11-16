/*
 * Вариант: конвейер |, фон &, встроенные cd / exit / fsize, измерение времени.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX_JOBS 64
#define MAX_PIPES 64

typedef enum { OP_NONE, OP_PIPE } op_t;

typedef struct {
    char **argv;
    size_t argc;
} cmd_t;

typedef struct {
    cmd_t *cmds;
    op_t *ops;
    size_t n;
    int background;
    char *buf;
} plan_t;

typedef struct {
    int id;
    pid_t pid;
    char *text;
} job_t;

static job_t g_jobs[MAX_JOBS];
static int g_next_job_id = 1;

static int g_status = 0;
static int g_should_exit = 0;
static int g_fsize_set = 0;
static rlim_t g_fsize = 0;

static void *xrealloc(void *p, size_t n) {
    void *r = realloc(p, n);
    if (!r) { perror("vtsh: out of memory"); exit(1); }
    return r;
}

static char *xstrdup(const char *s) {
    char *r = strdup(s);
    if (!r) { perror("vtsh: out of memory"); exit(1); }
    return r;
}

static void syntax(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    fprintf(stderr, "vtsh: syntax error: ");
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
}

static int decode_status(int st) {
    if (WIFEXITED(st)) return WEXITSTATUS(st);
    if (WIFSIGNALED(st)) {
        int s = WTERMSIG(st);
        fprintf(stderr, "vtsh: terminated by signal %d (%s)\n", s, strsignal(s));
        return 128 + s;
    }
    return 1;
}

/* ---------- parser ---------- */

static void cmd_push(cmd_t *c, char *word) {
    c->argv = xrealloc(c->argv, (c->argc + 2) * sizeof(char *));
    c->argv[c->argc++] = word;
    c->argv[c->argc] = NULL;
}

static void plan_add(plan_t *p, cmd_t *c, op_t op) {
    p->cmds = xrealloc(p->cmds, (p->n + 1) * sizeof(cmd_t));
    p->ops = xrealloc(p->ops, (p->n + 1) * sizeof(op_t));
    p->cmds[p->n] = *c;
    p->ops[p->n] = op;
    p->n++;
    *c = (cmd_t){0};
}

static void plan_free(plan_t *p) {
    for (size_t i = 0; i < p->n; i++)
        free(p->cmds[i].argv);
    free(p->cmds);
    free(p->ops);
    free(p->buf);
    memset(p, 0, sizeof *p);
}

static char *buf_put(char *buf, size_t *pos, size_t cap, const char *s, size_t len) {
    if (*pos + len + 1 > cap) {
        cap = (*pos + len + 1) * 2;
        buf = xrealloc(buf, cap);
    }
    memcpy(buf + *pos, s, len);
    buf[*pos + len] = '\0';
    char *r = buf + *pos;
    *pos += len + 1;
    return r;
}

static int parse(const char *line, plan_t *p) {
    memset(p, 0, sizeof *p);
    size_t cap = strlen(line) * 2 + 1;
    char *buf = xrealloc(NULL, cap);
    size_t pos = 0;

    char **toks = NULL;
    size_t nt = 0;
    const char *s = line;

    while (*s) {
        while (*s == ' ' || *s == '\t') s++;
        if (!*s) break;

        if (s[0] == '|') {
            toks = xrealloc(toks, (nt + 1) * sizeof(char *));
            toks[nt++] = buf_put(buf, &pos, cap, "|", 1);
            s += 1;
        } else if (s[0] == '&') {
            toks = xrealloc(toks, (nt + 1) * sizeof(char *));
            toks[nt++] = buf_put(buf, &pos, cap, "&", 1);
            s += 1;
        } else {
            const char *start = s;
            while (*s && *s != ' ' && *s != '\t' && *s != '|' && *s != '&')
                s++;
            toks = xrealloc(toks, (nt + 1) * sizeof(char *));
            toks[nt++] = buf_put(buf, &pos, cap, start, (size_t)(s - start));
        }
    }
    p->buf = buf;

    if (nt == 0) {
        free(toks);
        free(buf);
        return 1;
    }

    int rc = -1;
    cmd_t cur = {0};
    op_t pending = OP_NONE;
    int saw_op = 0;

    if (nt > 0 && strcmp(toks[nt - 1], "&") == 0) {
        p->background = 1;
        nt--;
    }

    for (size_t i = 0; i < nt; i++) {
        const char *t = toks[i];
        if (!strcmp(t, "|")) {
            if (cur.argc == 0) { syntax("unexpected '|'"); goto out; }
            plan_add(p, &cur, pending);
            pending = OP_PIPE;
            saw_op = 1;
        } else if (!strcmp(t, "&")) {
            syntax("'&' is allowed only at the end of a single simple command");
            goto out;
        } else {
            cmd_push(&cur, toks[i]);
        }
    }

    if (cur.argc > 0)
        plan_add(p, &cur, pending);

    if (p->n == 0) {
        syntax("empty command");
        goto out;
    }
    if (p->background && saw_op) {
        syntax("'&' cannot be applied to a chain of commands");
        goto out;
    }
    rc = 0;

out:
    free(toks);
    free(cur.argv);
    if (rc != 0) plan_free(p);
    return rc;
}

/* ---------- process manager ---------- */

static int find_free_job(void) {
    for (int i = 0; i < MAX_JOBS; i++)
        if (g_jobs[i].pid == 0) return i;
    return -1;
}

static void add_job(int slot, pid_t pid, const char *text) {
    g_jobs[slot].id = g_next_job_id++;
    g_jobs[slot].pid = pid;
    g_jobs[slot].text = xstrdup(text);
    fprintf(stderr, "[%d] %d\n", g_jobs[slot].id, (int)pid);
}

static void reap_jobs(void) {
    int st;
    pid_t pid;
    while ((pid = waitpid(-1, &st, WNOHANG)) > 0) {
        for (int i = 0; i < MAX_JOBS; i++) {
            if (g_jobs[i].pid != pid) continue;
            if (WIFSIGNALED(st))
                fprintf(stderr, "[%d] Terminated by signal %d (%s)  %s\n",
                        g_jobs[i].id, WTERMSIG(st), strsignal(WTERMSIG(st)), g_jobs[i].text);
            else
                fprintf(stderr, "[%d] Done (exit %d)  %s\n",
                        g_jobs[i].id, WIFEXITED(st) ? WEXITSTATUS(st) : -1, g_jobs[i].text);
            free(g_jobs[i].text);
            g_jobs[i] = (job_t){0};
            break;
        }
    }
}

static void shutdown_jobs(void) {
    for (int i = 0; i < MAX_JOBS; i++) {
        if (g_jobs[i].pid == 0) continue;
        kill(g_jobs[i].pid, SIGTERM);
        while (waitpid(g_jobs[i].pid, NULL, 0) < 0 && errno == EINTR)
            ;
        free(g_jobs[i].text);
        g_jobs[i] = (job_t){0};
    }
}

/* ---------- builtins ---------- */

static int is_builtin(const char *n) {
    return !strcmp(n, "cd") || !strcmp(n, "exit") || !strcmp(n, "fsize");
}

static int builtin_cd(cmd_t *c) {
    const char *dir;
    if (c->argc > 2) {
        fprintf(stderr, "vtsh: cd: too many arguments\n");
        return 1;
    }
    dir = (c->argc == 2) ? c->argv[1] : getenv("HOME");
    if (!dir) {
        fprintf(stderr, "vtsh: cd: HOME not set\n");
        return 1;
    }
    if (chdir(dir) < 0) {
        fprintf(stderr, "vtsh: cd: %s: %s\n", dir, strerror(errno));
        return 1;
    }
    return 0;
}

static int builtin_exit(cmd_t *c) {
    int code = g_status;
    if (c->argc > 2) {
        fprintf(stderr, "vtsh: exit: too many arguments\n");
        return 1;
    }
    if (c->argc == 2) {
        char *end;
        long v = strtol(c->argv[1], &end, 10);
        if (*end || end == c->argv[1]) {
            fprintf(stderr, "vtsh: exit: numeric argument required\n");
            return 2;
        }
        code = (int)(v & 0xFF);
    }
    g_should_exit = 1;
    return code;
}

static int builtin_fsize(cmd_t *c) {
    if (c->argc == 1) {
        if (g_fsize_set)
            printf("fsize: %llu bytes\n", (unsigned long long)g_fsize);
        else
            printf("fsize: off\n");
        return 0;
    }
    if (c->argc != 2) {
        fprintf(stderr, "vtsh: usage: fsize [bytes|off]\n");
        return 2;
    }
    if (!strcmp(c->argv[1], "off")) {
        g_fsize_set = 0;
        return 0;
    }
    char *end;
    errno = 0;
    unsigned long long v = strtoull(c->argv[1], &end, 10);
    if (errno || *end || end == c->argv[1] || c->argv[1][0] == '-') {
        fprintf(stderr, "vtsh: fsize: invalid value '%s'\n", c->argv[1]);
        return 2;
    }
    g_fsize = (rlim_t)v;
    g_fsize_set = 1;
    return 0;
}

/* ---------- executor ---------- */

/* run_cmds — запуск одной команды или конвейера.
 * Объединяет run_external и run_pipeline из исходной версии.
 * child_setup встроен напрямую.
 */
static int run_cmds(cmd_t *cmds, size_t n, int bg) {
    if (n == 0) return 0;
    if (n - 1 > MAX_PIPES - 1) {
        fprintf(stderr, "vtsh: too many pipeline stages\n");
        return 1;
    }

    int pipes[MAX_PIPES - 1][2];
    pid_t pids[MAX_PIPES];

    for (size_t i = 0; i + 1 < n; i++)
        if (pipe(pipes[i]) < 0) { perror("vtsh: pipe"); return 1; }

    for (size_t i = 0; i < n; i++) {
        pid_t pid = fork();
        if (pid < 0) { perror("vtsh: fork"); return 1; }
        if (pid == 0) {
            /* ребёнок: сигналы, фон, перенаправления stdin на /dev/null */
            struct sigaction sa;
            memset(&sa, 0, sizeof sa);
            sa.sa_handler = SIG_DFL;
            sigemptyset(&sa.sa_mask);
            sigaction(SIGINT, &sa, NULL);

            if (bg) {
                setpgid(0, 0);
                int fd = open("/dev/null", O_RDONLY);
                if (fd >= 0) {
                    dup2(fd, STDIN_FILENO);
                    if (fd != STDIN_FILENO) close(fd);
                }
            }

            if (i > 0)      dup2(pipes[i - 1][0], STDIN_FILENO);
            if (i + 1 < n)  dup2(pipes[i][1], STDOUT_FILENO);
            for (size_t j = 0; j + 1 < n; j++) {
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            /* RLIMIT_FSIZE */
            if (g_fsize_set) {
                struct rlimit rl;
                if (getrlimit(RLIMIT_FSIZE, &rl) < 0) { perror("vtsh: getrlimit"); _exit(126); }
                if (rl.rlim_max != RLIM_INFINITY && g_fsize > rl.rlim_max) {
                    fprintf(stderr, "vtsh: FSIZE limit %llu exceeds hard limit %llu\n",
                            (unsigned long long)g_fsize, (unsigned long long)rl.rlim_max);
                    _exit(126);
                }
                rl.rlim_cur = g_fsize;
                rl.rlim_max = g_fsize;
                if (setrlimit(RLIMIT_FSIZE, &rl) < 0) { perror("vtsh: setrlimit(FSIZE)"); _exit(126); }
            }

            execvp(cmds[i].argv[0], cmds[i].argv);
            fprintf(stderr, "vtsh: %s: %s\n", cmds[i].argv[0], strerror(errno));
            _exit(errno == ENOENT ? 127 : 126);
        }
        pids[i] = pid;
    }

    /* родитель закрывает свои концы pipe'ов */
    for (size_t i = 0; i + 1 < n; i++) {
        close(pipes[i][0]);
        close(pipes[i][1]);
    }

    if (bg) {
        int slot = find_free_job();
        if (slot < 0) {
            fprintf(stderr, "vtsh: too many background jobs\n");
            return 1;
        }
        setpgid(pids[0], pids[0]);
        add_job(slot, pids[0], cmds[0].argv[0]);
        return 0;
    }

    struct timespec ts_start, ts_end;
    clock_gettime(CLOCK_MONOTONIC, &ts_start);

    int status = 0;
    for (size_t i = 0; i < n; i++) {
        int st;
        if (waitpid(pids[i], &st, 0) < 0) { perror("vtsh: waitpid"); return 1; }
        if (i + 1 == n) status = decode_status(st);
    }
    clock_gettime(CLOCK_MONOTONIC, &ts_end);
    double elapsed = (ts_end.tv_sec - ts_start.tv_sec) +
                     (ts_end.tv_nsec - ts_start.tv_nsec) / 1e9;
    if (n == 1)
        fprintf(stderr, "vtsh: [%s] %.6f s\n", cmds[0].argv[0], elapsed);
    else
        fprintf(stderr, "vtsh: [pipeline] %.6f s\n", elapsed);

    return status;
}

static int run_command(cmd_t *c, int bg) {
    if (is_builtin(c->argv[0])) {
        if (bg) {
            fprintf(stderr, "vtsh: builtin '%s' cannot run in background\n", c->argv[0]);
            return 1;
        }
        if (!strcmp(c->argv[0], "cd")) return builtin_cd(c);
        if (!strcmp(c->argv[0], "exit")) return builtin_exit(c);
        return builtin_fsize(c);
    }
    return run_cmds(c, 1, bg);
}

static void execute(plan_t *p) {
    int status = g_status;
    size_t i = 0;
    while (i < p->n) {
        if (i + 1 < p->n && p->ops[i + 1] == OP_PIPE) {
            size_t start = i;
            while (i + 1 < p->n && p->ops[i + 1] == OP_PIPE) i++;
            size_t end = i;
            status = run_cmds(&p->cmds[start], end - start + 1, p->background);
            g_status = status;
            i++;
        } else {
            status = run_command(&p->cmds[i], p->background);
            g_status = status;
            i++;
        }
        if (g_should_exit) return;
    }
}

/* ---------- main ---------- */

int main(void) {
    int interactive = isatty(STDIN_FILENO);

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);

    char *line = NULL;
    size_t cap = 0;

    while (!g_should_exit) {
        reap_jobs();
        if (interactive) {
            fputs("vtsh> ", stdout);
            fflush(stdout);
        }

        ssize_t n = getline(&line, &cap, stdin);
        if (n < 0) {
            if (interactive) putchar('\n');
            break;
        }
        while (n > 0 && (line[n - 1] == '\n' || line[n - 1] == '\r'))
            line[--n] = '\0';

        plan_t plan;
        int r = parse(line, &plan);
        if (r == 0) {
            execute(&plan);
            plan_free(&plan);
        } else if (r < 0) {
            g_status = 2;
        }
        reap_jobs();
    }

    shutdown_jobs();
    free(line);
    return g_status;
}
