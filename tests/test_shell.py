"""Unit tests for the shell and VFS logic."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from shell import ShellEmulator  # noqa: E402
from vfs import VirtualFileSystem  # noqa: E402


class ShellTests(unittest.TestCase):
    """Check the commands required by variant 16."""

    def setUp(self) -> None:
        """Create an in-memory shell backed by a temporary JSON file."""
        data = {
            "name": "test-vfs",
            "root": {
                "type": "dir",
                "children": {
                    "docs": {
                        "type": "dir",
                        "children": {
                            "a.txt": {
                                "type": "file",
                                "encoding": "text",
                                "content": "one\ntwo\nthree",
                            }
                        },
                    }
                },
            },
        }
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            delete=False,
        )
        json.dump(data, handle)
        handle.close()
        self.temp_path = Path(handle.name)
        self.shell = ShellEmulator(
            VirtualFileSystem.from_json(str(self.temp_path))
        )

    def tearDown(self) -> None:
        """Remove the temporary VFS file."""
        self.temp_path.unlink(missing_ok=True)

    def test_simple_parser(self) -> None:
        """The parser must split command and arguments by spaces."""
        command, args = self.shell.parse("head -n 2 docs/a.txt")
        self.assertEqual(command, "head")
        self.assertEqual(args, ["-n", "2", "docs/a.txt"])

    def test_ls_and_cd(self) -> None:
        """ls and cd must navigate the virtual file system."""
        self.assertEqual(self.shell.execute("ls").output, "docs")
        self.assertFalse(self.shell.execute("cd docs").is_error)
        self.assertEqual(self.shell.cwd, "/docs")
        self.assertEqual(self.shell.execute("ls").output, "a.txt")

    def test_head(self) -> None:
        """head must output the requested number of first lines."""
        result = self.shell.execute("head -n 2 docs/a.txt")
        self.assertEqual(result.output, "one\ntwo")

    def test_tac(self) -> None:
        """tac must output file lines in reverse order."""
        result = self.shell.execute("tac docs/a.txt")
        self.assertEqual(result.output, "three\ntwo\none")

    def test_mkdir_changes_memory_only(self) -> None:
        """mkdir must create a directory in the in-memory structure."""
        result = self.shell.execute("mkdir new")
        self.assertFalse(result.is_error)
        self.assertIn("new", self.shell.execute("ls").output)

    def test_unknown_command_is_error(self) -> None:
        """Unknown commands must produce an execution error."""
        result = self.shell.execute("wat")
        self.assertTrue(result.is_error)
        self.assertIn("Unknown command", result.output)


if __name__ == "__main__":
    unittest.main()
