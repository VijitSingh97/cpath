"""Exercise the command without reading or changing the real clipboard."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

COMMAND = Path(__file__).resolve().parents[1] / "bin" / "cpath"


class CpathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mock_bin = self.root / "bin"
        self.mock_bin.mkdir()
        self.clipboard = self.root / "clipboard"
        self.clipboard.write_text("unchanged")
        self.args = self.root / "args"
        self.file = self.root / "file with spaces.txt"
        self.file.touch()
        self.env = {
            "PATH": str(self.mock_bin),
            "CPATH_OS": "Darwin",
            "CPATH_CLIPBOARD": str(self.clipboard),
            "CPATH_ARGS": str(self.args),
        }
        (self.mock_bin / "realpath").symlink_to(shutil.which("realpath"))
        self.mock("uname", 'printf "%s\\n" "$CPATH_OS"')
        for backend in ("pbcopy", "wl-copy", "xclip", "xsel"):
            self.mock(backend, '[ "${CPATH_FAIL:-0}" = 0 ] || exit 7\n'
                      'printf "%s\\n" "$@" > "$CPATH_ARGS"\n'
                      '/bin/cat > "$CPATH_CLIPBOARD"')

    def mock(self, name, body):
        path = self.mock_bin / name
        path.write_text("#!/bin/sh\n" + body + "\n")
        path.chmod(0o755)

    def run_command(self, *args, **env):
        return subprocess.run([str(COMMAND), *map(str, args)],
                              cwd=self.root, env={**self.env, **env},
                              text=True, capture_output=True)

    def assert_copied(self, result, expected):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"copied: {expected}\n")
        self.assertEqual(self.clipboard.read_text(), str(expected))

    def test_macos_spaces_directory_symlink_and_leading_dash(self):
        link = self.root / "link"
        link.symlink_to(self.file)
        dash = self.root / "-file"
        dash.touch()
        for argument, expected in ((self.file.name, self.file),
                                   (self.root, self.root), (link, self.file),
                                   ("-file", dash)):
            with self.subTest(argument=argument):
                self.assert_copied(self.run_command(argument), expected.resolve())

    def test_missing_file_and_broken_symlink_preserve_clipboard(self):
        broken = self.root / "broken"
        broken.symlink_to(self.root / "missing")
        for path in (self.root / "missing", broken):
            result = self.run_command(path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("file doesn't exist", result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(self.clipboard.read_text(), "unchanged")

    def test_linux_clipboard_selection(self):
        cases = (("wayland-0", ":0", ""), ("", ":0", "-selection\nclipboard\n"))
        for wayland, display, args in cases:
            result = self.run_command(self.file, CPATH_OS="Linux",
                                      WAYLAND_DISPLAY=wayland, DISPLAY=display)
            self.assert_copied(result, self.file.resolve())
            self.assertEqual(self.args.read_text(), args or "\n")
        (self.mock_bin / "xclip").unlink()
        self.assert_copied(self.run_command(self.file, CPATH_OS="Linux", DISPLAY=":0"),
                           self.file.resolve())
        self.assertEqual(self.args.read_text(), "--clipboard\n--input\n")
        (self.mock_bin / "wl-copy").unlink()
        self.assert_copied(self.run_command(self.file, CPATH_OS="Linux",
                                           WAYLAND_DISPLAY="wayland-0", DISPLAY=":0"),
                           self.file.resolve())

    def test_headless_and_unsupported_systems(self):
        for system, error in (("Linux", "no desktop clipboard"),
                              ("FreeBSD", "supported on macOS and Linux")):
            result = self.run_command(self.file, CPATH_OS=system)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(error, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(self.clipboard.read_text(), "unchanged")

    def test_clipboard_and_realpath_failures_never_report_success(self):
        result = self.run_command(self.file, CPATH_FAIL="1")
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.clipboard.read_text(), "unchanged")
        (self.mock_bin / "realpath").unlink()
        self.mock("realpath", "exit 2")
        result = self.run_command(self.file)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.clipboard.read_text(), "unchanged")

    def test_usage_help_and_version(self):
        for args in ((), (self.file, self.file)):
            result = self.run_command(*args)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Usage: cpath FILE", result.stderr)
        for option, output in (("--help", "Usage: cpath FILE"),
                               ("--version", "cpath 0.0.1")):
            result = self.run_command(option)
            self.assertEqual(result.returncode, 0)
            self.assertIn(output, result.stdout)
        self.assertEqual(self.clipboard.read_text(), "unchanged")


if __name__ == "__main__":
    unittest.main()
