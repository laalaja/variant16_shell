"""Tests for shell commands."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from shell import ShellEmulator
from vfs import VirtualFileSystem


class ShellTests(unittest.TestCase):
    """Test command parsing and execution."""

    @staticmethod
    def _make_shell() -> ShellEmulator:
        """Create a fresh shell for a test."""
        vfs = VirtualFileSystem(
            "demo-vfs",
            {
                "type": "dir",
                "children": {
                    "docs": {
                        "type": "dir",
                        "children": {
                            "notes.txt": {
                                "type": "file",
                                "encoding": "text",
                                "content": "one\ntwo\nthree",
                            },
                        },
                    },
                },
            },
        )

        return ShellEmulator(vfs)

    def test_parse(self) -> None:
        """Parser should split command and arguments."""
        shell = self._make_shell()
        command, args = shell.parse("head -n 2 file.txt")

        self.assertEqual(command, "head")
        self.assertEqual(args, ["-n", "2", "file.txt"])

    def test_ls_and_cd(self) -> None:
        """ls and cd should navigate the VFS."""
        shell = self._make_shell()
        self.assertEqual(shell.execute("ls").output, "docs")

        result = shell.execute("cd docs")

        self.assertFalse(result.is_error)
        self.assertEqual(shell.cwd, "/docs")
        self.assertEqual(
            shell.execute("ls").output,
            "notes.txt",
        )

    def test_head(self) -> None:
        """head should show the requested first lines."""
        shell = self._make_shell()
        result = shell.execute("head -n 2 docs/notes.txt")

        self.assertEqual(result.output, "one\ntwo")
        self.assertFalse(result.is_error)

    def test_tac(self) -> None:
        """tac should reverse file lines."""
        shell = self._make_shell()
        result = shell.execute("tac docs/notes.txt")

        self.assertEqual(result.output, "three\ntwo\none")
        self.assertFalse(result.is_error)

    def test_cal(self) -> None:
        """cal should display the selected month."""
        shell = self._make_shell()
        result = shell.execute("cal 9 2026")

        self.assertIn("September 2026", result.output)
        self.assertFalse(result.is_error)

    def test_mkdir(self) -> None:
        """mkdir should create a usable directory."""
        shell = self._make_shell()
        result = shell.execute("mkdir projects")

        self.assertFalse(result.is_error)
        self.assertEqual(result.output, "")
        self.assertIn("projects", shell.execute("ls").output)
        self.assertFalse(
            shell.execute("cd projects").is_error
        )

    def test_mkdir_in_current_directory(self) -> None:
        """mkdir should respect the current directory."""
        shell = self._make_shell()
        shell.execute("cd docs")
        result = shell.execute("mkdir drafts")

        self.assertFalse(result.is_error)
        self.assertIn("drafts", shell.execute("ls").output)

    def test_mkdir_existing_name_is_error(self) -> None:
        """mkdir should reject an existing entry."""
        shell = self._make_shell()
        result = shell.execute("mkdir docs")

        self.assertTrue(result.is_error)
        self.assertIn("File exists", result.output)

    def test_invalid_mkdir_arguments(self) -> None:
        """mkdir should accept exactly one argument."""
        shell = self._make_shell()
        no_name = shell.execute("mkdir")
        two_names = shell.execute("mkdir one two")

        self.assertTrue(no_name.is_error)
        self.assertTrue(two_names.is_error)
        self.assertEqual(no_name.output, "Usage: mkdir DIRECTORY")

    def test_invalid_command(self) -> None:
        """Unknown command should return an error."""
        shell = self._make_shell()
        result = shell.execute("unknown")

        self.assertTrue(result.is_error)

    def test_exit(self) -> None:
        """exit should request application termination."""
        shell = self._make_shell()
        result = shell.execute("exit")

        self.assertTrue(result.should_exit)


if __name__ == "__main__":
    unittest.main()
