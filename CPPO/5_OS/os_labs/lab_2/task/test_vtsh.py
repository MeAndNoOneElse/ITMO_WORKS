import os
import subprocess
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VTSH = os.path.join(ROOT, "build", "bin", "vtsh")


def run(script, env=None, timeout=10):
    """Запускает vtsh (без shell=True!), подаёт script в stdin."""
    return subprocess.run([VTSH], input=script, capture_output=True,
                          text=True, timeout=timeout, env=env)


class BasicTests(unittest.TestCase):
    def test_empty_line_and_eof(self):
        r = run("\n\n   \n")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_absolute_path_and_args(self):
        r = run("/bin/echo hello world\n")
        self.assertEqual(r.stdout, "hello world\n")

    def test_extra_spaces(self):
        r = run("   /bin/echo    a     b   \n")
        self.assertEqual(r.stdout, "a b\n")

    def test_env_passed(self):
        env = dict(os.environ, VTSH_TEST_VAR="42")
        r = run("env\n", env=env)
        self.assertIn("VTSH_TEST_VAR=42", r.stdout)

    def test_not_found_is_127(self):
        r = run("/no/such/program\nexit\n")
        self.assertEqual(r.returncode, 127)

    def test_not_executable_is_126(self):
        with tempfile.NamedTemporaryFile() as f:  # файл без права +x
            r = run(f"{f.name}\nexit\n")
        self.assertEqual(r.returncode, 126)

    def test_exit_status_propagates(self):
        self.assertEqual(run("false\nexit\n").returncode, 1)
        self.assertEqual(run("true\nexit\n").returncode, 0)
        self.assertEqual(run("exit 7\n").returncode, 7)

    def test_syntax_error_does_not_kill_shell(self):
        r = run("|| echo x\n/bin/echo alive\n")
        self.assertIn("syntax error", r.stderr)
        self.assertEqual(r.stdout, "alive\n")

    def test_cd(self):
        with tempfile.TemporaryDirectory() as d:
            d = os.path.realpath(d)
            r = run(f"cd {d}\n/bin/pwd\n")
            self.assertEqual(r.stdout.strip(), d)


class LogicTests(unittest.TestCase):
    def test_or_skips_after_success(self):
        r = run("true || echo not-run\n")
        self.assertEqual(r.stdout, "")

    def test_or_runs_after_failure(self):
        r = run("false || echo fallback\n")
        self.assertEqual(r.stdout, "fallback\n")

    def test_seq(self):
        r = run("false ; echo no ; echo yes\n")
        self.assertEqual(r.stdout, "no\nyes\n")

    def test_chain_false_false_echo(self):
        r = run("false || false || echo recovered\n")
        self.assertEqual(r.stdout, "recovered\n")

    def test_lazy_skipped_keeps_status(self):
        # true || x || echo y  -> статус остаётся 0, y не печатается
        r = run("true || echo x || echo y\n")
        self.assertEqual(r.stdout, "")

    def test_incomplete_or(self):
        r = run("true ||\n")
        self.assertIn("syntax error", r.stderr)


class BackgroundTests(unittest.TestCase):
    def test_bg_does_not_block(self):
        t = time.time()
        r = run("sleep 2 &\n/bin/echo next\n")
        self.assertEqual(r.stdout, "next\n")
        self.assertLess(time.time() - t, 1.5)  # shell не ждал sleep 2

    def test_bg_reaped(self):
        r = run("sleep 0.1 &\nsleep 0.5\n/bin/echo x\n")
        self.assertIn("Done", r.stderr)  # завершившаяся задача собрана

    def test_bg_on_chain_is_error(self):
        r = run("true || true &\n")
        self.assertIn("syntax error", r.stderr)


class FsizeTests(unittest.TestCase):
    def test_fsize_limits_file(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.bin")
            r = run(f"fsize 4096\n"
                    f"dd if=/dev/zero of={out} bs=1024 count=100\n"
                    f"exit\n")
            self.assertLessEqual(os.path.getsize(out), 4096)
            self.assertNotEqual(r.returncode, 0)  # dd не дописал

    def test_shell_survives_and_off_works(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.bin")
            r = run(f"fsize 4096\n"
                    f"dd if=/dev/zero of={out} bs=1024 count=100\n"
                    f"fsize off\n"
                    f"dd if=/dev/zero of={out} bs=1024 count=100\n"
                    f"/bin/echo alive\n")
            self.assertIn("alive", r.stdout)
            self.assertEqual(os.path.getsize(out), 100 * 1024)

    def test_invalid_fsize(self):
        r = run("fsize abc\n/bin/echo alive\n")
        self.assertIn("invalid", r.stderr)
        self.assertIn("alive", r.stdout)


if __name__ == "__main__":
    unittest.main()
