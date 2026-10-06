"""Tests for the first REPL prototype."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from shell import ShellEmulator


class ShellTests(unittest.TestCase):
    """Test command parsing and REPL commands."""

    def setUp(self) -> None:
        """Create a shell before every test."""
        self.shell = ShellEmulator("demo-vfs")

    def test_parse(self) -> None:
        """Parser should split command and arguments."""
        command, args = self.shell.parse("cd home")

        self.assertEqual(command, "cd")
        self.assertEqual(args, ["home"])

    def test_ls_stub(self) -> None:
        """ls should work as a stub."""
        result = self.shell.execute("ls")

        self.assertEqual(result.output, "Command: ls")
        self.assertFalse(result.is_error)

    def test_cd_stub(self) -> None:
        """cd should display its argument."""
        result = self.shell.execute("cd home")

        self.assertIn("home", result.output)
        self.assertFalse(result.is_error)

    def test_invalid_command(self) -> None:
        """Unknown command should return an error."""
        result = self.shell.execute("unknown")

        self.assertTrue(result.is_error)

    def test_invalid_cd_arguments(self) -> None:
        """cd without a path should return an error."""
        result = self.shell.execute("cd")

        self.assertTrue(result.is_error)

    def test_exit(self) -> None:
        """exit should request application termination."""
        result = self.shell.execute("exit")

        self.assertTrue(result.should_exit)


if __name__ == "__main__":
    unittest.main()