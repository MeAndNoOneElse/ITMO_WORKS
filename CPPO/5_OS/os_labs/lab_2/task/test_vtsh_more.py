import os
import subprocess
import tempfile
import time
import unittest

VTSH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "build", "bin", "vtsh",
)

TIMEOUT = 15


def run(script, timeout=TIMEOUT, env=None):
    """Запускает vtsh, подаёт script на stdin, возвращает CompletedProcess."""
    return subprocess.run(
        [VTSH],
        input=script,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


class TestVtshMore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(VTSH) or not os.access(VTSH, os.X_OK):
            raise unittest.SkipTest(f"vtsh не найден или не исполняем: {VTSH}")

    # ------------------------------------------------------------------
    # Базовые команды
    # ------------------------------------------------------------------

    def test_echo_single_word(self):
        res = run("/bin/echo hello\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "hello\n")

    def test_echo_multiple_words(self):
        res = run("/bin/echo hello world from vtsh\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "hello world from vtsh\n")

    def test_echo_with_tabs(self):
        res = run("/bin/echo\thello\tworld\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "hello world\n")

    def test_multiple_commands_newline(self):
        res = run("/bin/echo first\n/bin/echo second\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "first\nsecond\n")

    def test_true_returns_zero(self):
        res = run("true\n")
        self.assertEqual(res.returncode, 0)

    def test_false_returns_one(self):
        res = run("false\n")
        self.assertEqual(res.returncode, 1)

    def test_cat_passthrough(self):
        res = run("/bin/echo hello | /usr/bin/cat\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "hello\n")

    def test_wc_l_counts_lines(self):
        res = run("/bin/echo -e 'line1\\nline2\\nline3' | /usr/bin/wc -l\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "3")

    def test_command_not_found(self):
        res = run("/bin/nonexistent-command-xyz\n")
        self.assertEqual(res.returncode, 127)

    def test_not_executable(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".sh") as f:
            f.write("#!/bin/sh\necho hi\n")
            path = f.name
        try:
            os.chmod(path, 0o644)
            res = run(f"{path}\n")
            self.assertEqual(res.returncode, 126)
        finally:
            os.unlink(path)

    # ------------------------------------------------------------------
    # Конвейеры |
    # ------------------------------------------------------------------

    def test_pipe_two_commands(self):
        res = run("/bin/echo hello-pipe | /bin/cat\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "hello-pipe\n")

    def test_pipe_three_commands(self):
        res = run("/bin/echo a b c d | /bin/cat | /usr/bin/wc -w\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "4")

    def test_pipe_four_commands(self):
        res = run("/bin/echo a b c d | /bin/cat | /bin/cat | /usr/bin/wc -w\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "4")

    def test_pipe_with_many_arguments(self):
        res = run("/bin/echo one two three four five | /usr/bin/wc -w\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "5")

    def test_pipe_cat_no_args(self):
        res = run("/bin/echo just-cat | /bin/cat\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "just-cat\n")

    def test_pipe_wc_c_counts_chars(self):
        res = run("/bin/echo abc | /bin/cat | /usr/bin/wc -c\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "4")

    def test_pipe_preserves_spaces(self):
        res = run("/bin/echo  spaced  out  | /bin/cat\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "spaced out\n")

    def test_pipe_first_command_fails(self):
        # Статус конвейера — статус последней команды (как в bash).
        # Первая команда не найдена, но последняя (cat) выполняется успешно.
        res = run("/bin/nonexistent | /bin/cat\n")
        self.assertEqual(res.returncode, 0)  # статус последней команды (cat)
        self.assertIn("nonexistent", res.stderr)  # но ошибка есть в stderr

    def test_pipe_last_command_fails(self):
        res = run("/bin/echo ok | /bin/nonexistent\n")
        self.assertEqual(res.returncode, 127)

    # ------------------------------------------------------------------
    # Фоновый режим &
    # ------------------------------------------------------------------

    def test_background_continues_immediately(self):
        start = time.time()
        res = run("sleep 0.3 &\n/bin/echo after\n")
        elapsed = time.time() - start
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "after\n")
        self.assertLess(elapsed, 0.5)  # не ждал sleep 0.3

    def test_background_done_message(self):
        # Нужно подождать, пока фоновая задача завершится, прежде чем оболочка выйдет
        res = run("sleep 0.1 &\nsleep 0.3\n")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Done", res.stderr)

    def test_multiple_background_tasks(self):
        res = run("sleep 0.1 &\nsleep 0.1 &\nsleep 0.3\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stderr.count("Done"), 2)

    def test_background_task_gets_pid(self):
        res = run("sleep 0.1 &\n")
        self.assertEqual(res.returncode, 0)
        # Проверяем формат [id] pid в stderr
        import re
        match = re.search(r'\[\d+\] \d+', res.stderr)
        self.assertIsNotNone(match, f"ожидался формат [id] pid в stderr: {res.stderr!r}")

    def test_background_with_different_commands(self):
        res = run("/bin/echo bg1 &\n/bin/echo bg2 &\nsleep 0.3\n")
        self.assertEqual(res.returncode, 0)
        self.assertIn("bg1", res.stdout)
        self.assertIn("bg2", res.stdout)

    def test_background_simple_command_afterwards(self):
        res = run("sleep 0.2 &\n/bin/echo done\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "done\n")

    # ------------------------------------------------------------------
    # Граничные случаи
    # ------------------------------------------------------------------

    def test_long_pipeline(self):
        # конвейер из 7 звеньев
        cmd = " | ".join(["/bin/cat"] * 7)
        res = run(f"/bin/echo test | {cmd}\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "test\n")

    def test_command_with_many_arguments(self):
        args = " ".join(f"arg{i}" for i in range(20))
        res = run(f"/bin/echo {args}\n")
        self.assertEqual(res.returncode, 0)
        for i in range(20):
            self.assertIn(f"arg{i}", res.stdout)

    def test_pipeline_with_arguments_in_each_command(self):
        res = run("/bin/echo hello world | /bin/cat | /usr/bin/wc -w\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "2")

    # ------------------------------------------------------------------
    # Тестовые файлы из папки test/
    # ------------------------------------------------------------------

    def test_no_exec_python_126(self):
        """Скрипт без прав +x должен вернуть код 126."""
        res = run("./test/no_exec.py\n")
        self.assertEqual(res.returncode, 126)

    def test_no_exec_via_python3_0(self):
        """Скрипт через python3 должен работать и вернуть код 0."""
        res = run("python3 test/no_exec.py\n")
        self.assertEqual(res.returncode, 0)
        self.assertIn("Hello from Python script!", res.stdout)

    def test_pipe_grep_search(self):
        """Конвейер с grep ищет строки со словом 'search'."""
        res = run("cat test/search.txt | /bin/grep -i search\n")
        self.assertEqual(res.returncode, 0)
        self.assertIn("search", res.stdout.lower())

    def test_pipe_grep_wc_l(self):
        """Конвейер с grep и wc -l считает строки со словом 'search'."""
        res = run("cat test/search.txt | /bin/grep -i search | /usr/bin/wc -l\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "4")

    # ------------------------------------------------------------------
    # Оставшиеся сценарии из методички (ещё не покрытые выше)
    # ------------------------------------------------------------------

    def test_empty_line_and_eof(self):
        """Пустая строка и EOF не завершают оболочку."""
        res = run("\n\n\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "")
        # EOF без команд
        res = run("")
        self.assertEqual(res.returncode, 0)

    def test_env_variable_passed(self):
        """Переменная окружения передаётся в дочерний процесс."""
        env = dict(os.environ, MY_TEST_VAR="secret_value")
        res = run("/usr/bin/env\n", env=env)
        self.assertEqual(res.returncode, 0)
        self.assertIn("MY_TEST_VAR=secret_value", res.stdout)

    def test_syntax_error_does_not_kill_shell(self):
        """Синтаксическая ошибка не убивает оболочку."""
        res = run("||| invalid command\n/bin/echo alive\n")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "alive\n")

    def test_cd_changes_directory(self):
        """После cd новые команды выполняются в указанной директории."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            res = run(f"cd {d}\n/bin/pwd\n")
            self.assertEqual(res.returncode, 0)
            self.assertEqual(res.stdout.strip(), d)

    def test_fsize_resource_limit(self):
        """Ограничение размера файла через fsize работает."""
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.bin")
            res = run(f"fsize 4096\n"
                      f"dd if=/dev/zero of={out} bs=1024 count=100\n"
                      f"exit\n")
            self.assertNotEqual(res.returncode, 0)  # dd не дописал
            self.assertLessEqual(os.path.getsize(out), 4096)
            # Оболочка продолжает работу
            res = run(f"fsize 4096\n"
                      f"dd if=/dev/zero of={out} bs=1024 count=100\n"
                      f"fsize off\n"
                      f"dd if=/dev/zero of={out} bs=1024 count=100\n"
                      f"/bin/echo alive\n")
            self.assertIn("alive", res.stdout)
            self.assertEqual(os.path.getsize(out), 100 * 1024)


if __name__ == "__main__":
    unittest.main()
