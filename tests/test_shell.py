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
    """Test parsing and shell commands."""

    def setUp(self) -> None:
        """Create a shell before every test."""
        root = {
            "type": "dir",
            "children": {
                "hello.txt": {
                    "type": "file",
                    "encoding": "text",
                    "content": "one\ntwo\nthree\nfour",
                },
                "home": {
                    "type": "dir",
                    "children": {
                        "docs": {
                            "type": "dir",
                            "children": {},
                        },
                    },
                },
            },
        }
        self.shell = ShellEmulator(
            VirtualFileSystem("demo-vfs", root)
        )

    def test_parse(self) -> None:
        """Parser should split command and arguments."""
        command, args = self.shell.parse("cd home")
        self.assertEqual(command, "cd")
        self.assertEqual(args, ["home"])

    def test_ls(self) -> None:
        """ls should list the current directory."""
        result = self.shell.execute("ls")
        self.assertEqual(result.output, "hello.txt\nhome")

    def test_cd(self) -> None:
        """cd should change the current directory."""
        result = self.shell.execute("cd home/docs")
        self.assertFalse(result.is_error)
        self.assertEqual(self.shell.cwd, "/home/docs")

    def test_cd_parent(self) -> None:
        """cd .. should move one level up."""
        self.shell.execute("cd /home/docs")
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.cwd, "/home")

    def test_head(self) -> None:
        """head should display requested first lines."""
        result = self.shell.execute("head -n 2 hello.txt")
        self.assertEqual(result.output, "one\ntwo")

    def test_tac(self) -> None:
        """tac should reverse file lines."""
        result = self.shell.execute("tac hello.txt")
        self.assertEqual(result.output, "four\nthree\ntwo\none")

    def test_cal(self) -> None:
        """cal should display a requested month."""
        result = self.shell.execute("cal 9 2026")
        self.assertIn("September 2026", result.output)

    def test_unknown_command(self) -> None:
        """Unknown commands should return an error."""
        result = self.shell.execute("mkdir test")
        self.assertTrue(result.is_error)
        self.assertIn("Unknown command", result.output)

    def test_exit(self) -> None:
        """exit should request application termination."""
        result = self.shell.execute("exit")
        self.assertTrue(result.should_exit)


if __name__ == "__main__":
    unittest.main()
