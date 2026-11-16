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

#define MAX_JOBS 64   /* максимум фоновых задач одновременно */
#define MAX_PIPES 64  /* максимум звеньев в конвейере */


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

static int g_status = 0;       /* код последней команды (для exit без аргументов) */
static int g_should_exit = 0;  /* флаг выхода (ставит builtin exit) */

static int g_fsize_set = 0;
static rlim_t g_fsize = 0;     /* лимит RLIMIT_FSIZE (команда fsize) */

/* Вспомогательные функции*/

/*
 * xrealloc — безопасный realloc: при ошибке памяти выводит ошибку и завершает программу.
 * Используется вместо обычного realloc, чтобы не проверять результат вручную.
 */
static void *xrealloc(void *p, size_t n) {
    void *r = realloc(p, n);
    if (!r) { perror("vtsh: out of memory"); exit(1); }
    return r;
}

/*
 * xstrdup — безопасный strdup: копирует строку в кучу, при ошибке памяти — завершает программу.
 */
static char *xstrdup(const char *s) {
    char *r = strdup(s);
    if (!r) { perror("vtsh: out of memory"); exit(1); }
    return r;
}

/*
 * syntax — выводит сообщение об ошибке синтаксиса в stderr.
 * Пример вызова: syntax("unexpected '|'");
 * Вывод: vtsh: syntax error: unexpected '|'
 */
static void syntax(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    fprintf(stderr, "vtsh: syntax error: ");
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
}

/*
 * decode_status — переводит «сырой» статус waitpid во внутренний код:
 *   код выхода (0–255) или 128 + номер сигнала.
 */
static int decode_status(int st) {
    if (WIFEXITED(st)) return WEXITSTATUS(st);   /* нормальный код выхода */
    if (WIFSIGNALED(st)) {
        int s = WTERMSIG(st);
        fprintf(stderr, "vtsh: terminated by signal %d (%s)\n", s, strsignal(s));
        return 128 + s; /* 128 + номер сигнала */
    }
    return 1;
}

/* Парсер*/

static void cmd_push(cmd_t *c, char *word) {
    c->argv = xrealloc(c->argv, (c->argc + 2) * sizeof(char *)); /* расширяет argv */
    c->argv[c->argc++] = word; /* сохраняет слово и увеличивает счётчик */
    c->argv[c->argc] = NULL; /* терминатор NULL для execvp */
}

static void plan_add(plan_t *p, cmd_t *c, op_t op) {
    p->cmds = xrealloc(p->cmds, (p->n + 1) * sizeof(cmd_t)); /* расширяет команды */
    p->ops = xrealloc(p->ops, (p->n + 1) * sizeof(op_t)); /* расширяет операторы */
    p->cmds[p->n] = *c; /* копирует команду в план */
    p->ops[p->n] = op; /* запоминает оператор перед ней */
    p->n++; /* увеличивает счётчик команд */
    *c = (cmd_t){0}; /* очищает исходную команду */
}

static void plan_free(plan_t *p) {
    for (size_t i = 0; i < p->n; i++)
        free(p->cmds[i].argv); /* освобождает argv каждой команды */
    free(p->cmds); /* массив команд */
    free(p->ops); /* массив операторов */
    free(p->buf); /* общий буфер строк */
    memset(p, 0, sizeof *p); /* обнуляет структуру */
}

/* Копирует строку в общий буфер buf, возвращает указатель на неё внутри buf */
static char *buf_put(char *buf, size_t *pos, size_t cap, const char *s, size_t len) {
    if (*pos + len + 1 > cap) { /* если места не хватает */
        cap = (*pos + len + 1) * 2; /* удваивает ёмкость */
        buf = xrealloc(buf, cap); /* перевыделяет буфер */
    }
    memcpy(buf + *pos, s, len); /* копирует строку в буфер */
    buf[*pos + len] = '\0'; /* ставит завершающий ноль */
    char *r = buf + *pos; /* запоминает адрес строки */
    *pos += len + 1; /* сдвигает курсор в буфере */
    return r; /* возвращает указатель на строку */
}

/*
 * parse — ручной токенизатор. Один проход по строке, без предобработки.
 * Распознаёт слова, оператор | (конвейер) и & (фон, только в конце).
 * Возврат: 0 — план готов, 1 — пустая строка, -1 — ошибка.
 */
static int parse(const char *line, plan_t *p) {
    memset(p, 0, sizeof *p); /* обнуляет план */
    size_t cap = strlen(line) * 2 + 1; /* начальный размер буфера */
    char *buf = xrealloc(NULL, cap); /* выделяет буфер */
    size_t pos = 0; /* текущая позиция в буфере */

    char **toks = NULL; /* массив указателей на токены */
    size_t nt = 0; /* число токенов */
    const char *s = line; /* указатель на текущий символ */

    while (*s) { /* проходит по строке */
        while (*s == ' ' || *s == '\t') s++; /* пропускает пробелы и табы */
        if (!*s) break; /* конец строки */

        if (s[0] == '|') { /* найден оператор | */
            toks = xrealloc(toks, (nt + 1) * sizeof(char *)); /* расширяет массив токенов */
            toks[nt++] = buf_put(buf, &pos, cap, "|", 1); /* добавляет "|" как токен */
            s += 1; /* переходит за символ */
        } else if (s[0] == '&') { /* найден оператор & */
            toks = xrealloc(toks, (nt + 1) * sizeof(char *));
            toks[nt++] = buf_put(buf, &pos, cap, "&", 1);
            s += 1;
        } else { /* обычное слово */
            const char *start = s; /* начало слова */
            while (*s && *s != ' ' && *s != '\t' && *s != '|' && *s != '&') /* читает слово до разделителя */
                s++;
            toks = xrealloc(toks, (nt + 1) * sizeof(char *));
            toks[nt++] = buf_put(buf, &pos, cap, start, (size_t)(s - start)); /* добавляет слово как токен */
        }
    }
    p->buf = buf; /* сохраняет буфер в плане */

    if (nt == 0) { /* нет токенов — пустая строка */
        free(toks);
        free(buf);
        return 1; /* не ошибка */
    }

    int rc = -1;
    cmd_t cur = {0}; /* текущая собираемая команда */
    op_t pending = OP_NONE; /* оператор перед следующей командой */
    int saw_op = 0; /* был ли хоть один оператор */

    /* '&' допускается только последним токеном */
    if (nt > 0 && strcmp(toks[nt - 1], "&") == 0) {
        p->background = 1; /* флаг фонового выполнения */
        nt--; /* убирает "&" из токенов */
    }

    for (size_t i = 0; i < nt; i++) { /* проходит по токенам */
        const char *t = toks[i]; /* текущий токен */
        if (!strcmp(t, "|")) { /* оператор конвейера */
            if (cur.argc == 0) { syntax("unexpected '|'"); goto out; } /* ошибка: | в начале */
            plan_add(p, &cur, pending); /* добавляет команду в план */
            pending = OP_PIPE; /* следующий оператор — | */
            saw_op = 1;
        } else if (!strcmp(t, "&")) { /* & не в конце — ошибка */
            syntax("'&' is allowed only at the end of a single simple command");
            goto out;
        } else { /* обычное слово */
            cmd_push(&cur, toks[i]); /* добавляет слово в команду */
        }
    }

    if (cur.argc > 0)
        plan_add(p, &cur, pending); /* добавляет последнюю команду */

    if (p->n == 0) { /* нет команд — ошибка */
        syntax("empty command");
        goto out;
    }
    /* '&' не может быть с цепочкой команд (с оператором |) */
    if (p->background && saw_op) {
        syntax("'&' cannot be applied to a chain of commands");
        goto out;
    }
    rc = 0; /* успех */

out:
    free(toks); /* освобождает массив токенов */
    free(cur.argv); /* освобождает argv текущей команды */
    if (rc != 0) plan_free(p); /* очищает план при ошибке */
    return rc;
}

/* Менеджер фоновых задач */

static int find_free_job(void) { /* ищет свободный слот в таблице */
    for (int i = 0; i < MAX_JOBS; i++)
        if (g_jobs[i].pid == 0) return i; /* слот свободен, если pid == 0 */
    return -1; /* нет свободных слотов */
}

static void add_job(int slot, pid_t pid, const char *text) { /* добавляет задачу в таблицу */
    g_jobs[slot].id = g_next_job_id++; /* выдаёт порядковый номер */
    g_jobs[slot].pid = pid; /* запоминает PID */
    g_jobs[slot].text = xstrdup(text); /* копирует текст команды */
    fprintf(stderr, "[%d] %d\n", g_jobs[slot].id, (int)pid); /* выводит [id] pid */
}

/* reap_jobs — неблокирующий сбор завершённых фоновых задач (WNOHANG).
 * Вызывается в main() до и после обработки каждой строки, чтобы
 * завершённые фоновые задачи не оставались зомби. */
static void reap_jobs(void) {
    int st;
    pid_t pid;
    while ((pid = waitpid(-1, &st, WNOHANG)) > 0) { /* собирает завершённых детей без блокировки */
        for (int i = 0; i < MAX_JOBS; i++) {
            if (g_jobs[i].pid != pid) continue; /* ищет задачу по PID */
            if (WIFSIGNALED(st)) { /* процесс убит сигналом */
                fprintf(stderr, "[%d] Terminated by signal %d (%s)  %s\n",
                        g_jobs[i].id, WTERMSIG(st), strsignal(WTERMSIG(st)), g_jobs[i].text);
            } else {
                fprintf(stderr, "[%d] Done (exit %d)  %s\n",
                        g_jobs[i].id, WIFEXITED(st) ? WEXITSTATUS(st) : -1, g_jobs[i].text);
            }
            free(g_jobs[i].text); /* освобождает текст задачи */
            g_jobs[i] = (job_t){0}; /* освобождает слот */
            break;
        }
    }
}

/* shutdown_jobs — при выходе посылает SIGTERM всем фоновым задачам
 * и ждёт их, чтобы не оставить «сирот». */
static void shutdown_jobs(void) {
    for (int i = 0; i < MAX_JOBS; i++) {
        if (g_jobs[i].pid == 0) continue; /* пропускает свободные слоты */
        kill(g_jobs[i].pid, SIGTERM); /* посылает сигнал завершения */
        while (waitpid(g_jobs[i].pid, NULL, 0) < 0 && errno == EINTR) /* ждёт завершения */
            ;
        free(g_jobs[i].text); /* освобождает текст */
        g_jobs[i] = (job_t){0}; /* очищает слот */
    }
}

/* Встроенные команды (builtins)*/

static int is_builtin(const char *n) { /* проверяет, встроенная ли команда */
    return !strcmp(n, "cd") || !strcmp(n, "exit") || !strcmp(n, "fsize");
}

static int builtin_cd(cmd_t *c) { /* команда cd: смена директории */
    const char *dir;
    if (c->argc > 2) {
        fprintf(stderr, "vtsh: cd: too many arguments\n");
        return 1;
    }
    dir = (c->argc == 2) ? c->argv[1] : getenv("HOME"); /* аргумент или $HOME */
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

static int builtin_exit(cmd_t *c) { /* команда exit: завершение оболочки */
    int code = g_status; /* код по умолчанию — последний статус */
    if (c->argc > 2) {
        fprintf(stderr, "vtsh: exit: too many arguments\n");
        return 1;
    }
    if (c->argc == 2) { /* указан код выхода */
        char *end;
        long v = strtol(c->argv[1], &end, 10); /* парсит число */
        if (*end || end == c->argv[1]) { /* не число */
            fprintf(stderr, "vtsh: exit: numeric argument required\n");
            return 2;
        }
        code = (int)(v & 0xFF); /* обрезает до байта */
    }
    g_should_exit = 1; /* флаг выхода из main */
    return code;
}

static int builtin_fsize(cmd_t *c) { /* команда fsize: лимит файла */
    if (c->argc == 1) { /* без аргументов — показать */
        if (g_fsize_set)
            printf("fsize: %llu bytes\n", (unsigned long long)g_fsize);
        else
            printf("fsize: off\n");
        return 0;
    }
    if (c->argc != 2) { /* неверное число аргументов */
        fprintf(stderr, "vtsh: usage: fsize [bytes|off]\n");
        return 2;
    }
    if (!strcmp(c->argv[1], "off")) { /* снять лимит */
        g_fsize_set = 0;
        return 0;
    }
    char *end;
    errno = 0;
    unsigned long long v = strtoull(c->argv[1], &end, 10); /* парсит число байт */
    if (errno || *end || end == c->argv[1] || c->argv[1][0] == '-') { /* невалидное значение */
        fprintf(stderr, "vtsh: fsize: invalid value '%s'\n", c->argv[1]);
        return 2;
    }
    g_fsize = (rlim_t)v; /* устанавливает лимит */
    g_fsize_set = 1;
    return 0;
}

/* Исполнитель*/

static int run_cmds(cmd_t *cmds, size_t n, int bg) {
    if (n == 0) return 0; /* ничего не делать */
    if (n - 1 > MAX_PIPES - 1) { /* слишком много звеньев */
        fprintf(stderr, "vtsh: too many pipeline stages\n");
        return 1;
    }

    int pipes[MAX_PIPES - 1][2]; /* каналы для конвейера */
    pid_t pids[MAX_PIPES]; /* PID детей */

    /* Создаём все pipe'ы ДО fork'ов, чтобы дети унаследовали дескрипторы */
    for (size_t i = 0; i + 1 < n; i++)
        if (pipe(pipes[i]) < 0) { perror("vtsh: pipe"); return 1; } /* создаёт канал */

    for (size_t i = 0; i < n; i++) { /* создаёт каждого ребёнка */
        pid_t pid = fork(); /* клонирует процесс */
        if (pid < 0) { perror("vtsh: fork"); return 1; } /* ошибка fork */
        if (pid == 0) {
            /*создание ребёнка (до execvp)  */
            struct sigaction sa;
            memset(&sa, 0, sizeof sa);
            sa.sa_handler = SIG_DFL;
            sigemptyset(&sa.sa_mask);
            sigaction(SIGINT, &sa, NULL); /* сброс SIGINT в поведение по умолчанию */

            if (bg) { /* фоновый режим */
                setpgid(0, 0); /* своя группа процессов */
                int fd = open("/dev/null", O_RDONLY); /* stdin из /dev/null */
                if (fd >= 0) {
                    dup2(fd, STDIN_FILENO); /* перенаправляет stdin */
                    if (fd != STDIN_FILENO) close(fd);
                }
            }

            /* Соединяем stdin/stdout с соседними pipe'ами (для конвейера) */
            if (i > 0)      dup2(pipes[i - 1][0], STDIN_FILENO); /* читает из предыдущего pipe */
            if (i + 1 < n)  dup2(pipes[i][1], STDOUT_FILENO); /* пишет в следующий pipe */
            for (size_t j = 0; j + 1 < n; j++) { /* закрывает все концы pipe */
                close(pipes[j][0]);
                close(pipes[j][1]);
            }

            /* RLIMIT_FSIZE (команда fsize) */
            if (g_fsize_set) { /* если установлен лимит */
                struct rlimit rl;
                if (getrlimit(RLIMIT_FSIZE, &rl) < 0) { perror("vtsh: getrlimit"); _exit(126); }
                if (rl.rlim_max != RLIM_INFINITY && g_fsize > rl.rlim_max) { /* превышает hard limit */
                    fprintf(stderr, "vtsh: FSIZE limit %llu exceeds hard limit %llu\n",
                            (unsigned long long)g_fsize, (unsigned long long)rl.rlim_max);
                    _exit(126);
                }
                rl.rlim_cur = g_fsize; /* soft limit */
                rl.rlim_max = g_fsize; /* hard limit = soft */
                if (setrlimit(RLIMIT_FSIZE, &rl) < 0) { perror("vtsh: setrlimit(FSIZE)"); _exit(126); }
            }

            execvp(cmds[i].argv[0], cmds[i].argv); /* запускает программу */
            fprintf(stderr, "vtsh: %s: %s\n", cmds[i].argv[0], strerror(errno)); /* ошибка execvp */
            _exit(errno == ENOENT ? 127 : 126); /* код 127 или 126 */
        }
        pids[i] = pid; /* запоминает PID ребёнка */
    }

    /*  КОД РОДИТЕЛЯ: закрываем все свои концы pipe'ов  */
    for (size_t i = 0; i + 1 < n; i++) {
        close(pipes[i][0]); /* закрывает чтение */
        close(pipes[i][1]); /* закрывает запись */
    }

    if (bg) { /* фоновый режим */
        setpgid(pids[0], pids[0]); /* своя группа процессов */
        int slot = find_free_job(); /* ищет свободный слот */
        if (slot < 0) {
            fprintf(stderr, "vtsh: too many background jobs\n");
            return 1;
        }
        add_job(slot, pids[0], cmds[0].argv[0]); /* добавляет задачу в таблицу */
        return 0; /* не ждёт завершения */
    }

    /* Измеряем время выполнения (требование Части 1 задания) */
    struct timespec ts_start, ts_end;
    clock_gettime(CLOCK_MONOTONIC, &ts_start); /* начало замера */

    int status = 0;
    for (size_t i = 0; i < n; i++) { /* ждёт всех детей */
        int st;
        if (waitpid(pids[i], &st, 0) < 0) { perror("vtsh: waitpid"); return 1; } /* ждёт ребёнка */
        if (i + 1 == n) status = decode_status(st); /* статус последнего */
    }
    clock_gettime(CLOCK_MONOTONIC, &ts_end); /* конец замера */
    double elapsed = (ts_end.tv_sec - ts_start.tv_sec) +
                     (ts_end.tv_nsec - ts_start.tv_nsec) / 1e9; /* вычисляет время */
    if (n == 1)
        fprintf(stderr, "vtsh: [%s] %.6f s\n", cmds[0].argv[0], elapsed); /* время одной команды */
    else
        fprintf(stderr, "vtsh: [pipeline] %.6f s\n", elapsed); /* время конвейера */

    return status;
}

static int run_command(cmd_t *c, int bg) { /* запускает одну команду */
    if (is_builtin(c->argv[0])) { /* встроенная команда? */
        if (bg) { /* builtin не может быть в фоне */
            fprintf(stderr, "vtsh: builtin '%s' cannot run in background\n", c->argv[0]);
            return 1;
        }
        if (!strcmp(c->argv[0], "cd")) return builtin_cd(c); /* cd */
        if (!strcmp(c->argv[0], "exit")) return builtin_exit(c); /* exit */
        return builtin_fsize(c); /* fsize */
    }
    return run_cmds(c, 1, bg); /* внешняя команда */
}

/*
 * execute — обход плана выполнения.
 * Если за командой следует | — собирает все звенья конвейера и вызывает run_cmds.
 * Иначе — запускает отдельную команду через run_command.
 */
static void execute(plan_t *p) {
    int status = g_status;
    size_t i = 0;
    while (i < p->n) { /* проходит по командам плана */
        if (i + 1 < p->n && p->ops[i + 1] == OP_PIPE) { /* за командой следует | */
            size_t start = i; /* начало конвейера */
            while (i + 1 < p->n && p->ops[i + 1] == OP_PIPE) i++; /* находит кон конвейера */
            size_t end = i; /* конец конвейера */
            status = run_cmds(&p->cmds[start], end - start + 1, p->background); /* запускает конвейер */
            g_status = status; /* запоминает статус */
            i++;
        } else { /* отдельная команда */
            status = run_command(&p->cmds[i], p->background); /* запускает команду */
            g_status = status; /* запоминает статус */
            i++;
        }
        if (g_should_exit) return; /* если exit — прекращаем выполнение */
    }
}

/* REPL*/

int main(void) { /* точка входа */
    int interactive = isatty(STDIN_FILENO); /* интерактивный режим? */

    /* Ctrl+C не должен убивать оболочку (дети сбросят в SIG_DFL в run_cmds) */
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = SIG_IGN; /* игнорирует SIGINT */
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL); /* устанавливает обработчик */

    char *line = NULL; /* буфер для строки */
    size_t cap = 0; /* ёмкость буфера */

    while (!g_should_exit) { /* основной цикл REPL */
        reap_jobs(); /* собирает завершённые фоновые задачи */
        if (interactive) { /* если терминал */
            fputs("vtsh> ", stdout); /* приглашение */
            fflush(stdout); /* сбрасывает буфер */
        }

        ssize_t n = getline(&line, &cap, stdin); /* читает строку */
        if (n < 0) { /* EOF или ошибка */
            if (interactive) putchar('\n');
            break; /* выходит из цикла */
        }
        while (n > 0 && (line[n - 1] == '\n' || line[n - 1] == '\r')) /* убирает символы новой строки */
            line[--n] = '\0';

        plan_t plan;
        int r = parse(line, &plan); /* парсит строку в план */
        if (r == 0) { /* успешно */
            execute(&plan); /* выполняет план */
            plan_free(&plan); /* освобождает память плана */
        } else if (r < 0) { /* ошибка синтаксиса */
            g_status = 2; /* код ошибки, не убиваем shell */
        }
        reap_jobs(); /* собирает фоновые задачи после строки */
    }

    shutdown_jobs(); /* завершает все фоновые задачи при выходе */
    free(line); /* освобождает буфер getline */
    return g_status; /* возвращает код последней команды */
}