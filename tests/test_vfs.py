"""Tests for the JSON virtual file system."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from vfs import VirtualFileSystem


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class VFSTests(unittest.TestCase):
    """Test loading and using virtual file systems."""

    def setUp(self) -> None:
        """Load the demonstration VFS."""
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"
        self.vfs = VirtualFileSystem.from_json(str(path))

    def test_load_demo_vfs(self) -> None:
        """Demo VFS should load from JSON."""
        self.assertEqual(self.vfs.name, "demo-vfs")

    def test_nested_directories_exist(self) -> None:
        """Demo VFS should contain nested directories."""
        node = self.vfs.get_node("/home/student/docs")
        self.assertIn("notes.txt", node["children"])

    def test_list_dir(self) -> None:
        """VFS should list directory contents."""
        items = self.vfs.list_dir("/", "/")
        self.assertIn("home", items)
        self.assertIn("hello.txt", items)

    def test_change_dir(self) -> None:
        """VFS should resolve nested directories."""
        path = self.vfs.change_dir("student/docs", "/home")
        self.assertEqual(path, "/home/student/docs")

    def test_read_text(self) -> None:
        """VFS should read text files."""
        text = self.vfs.read_text(
            "notes.txt",
            "/home/student/docs",
        )
        self.assertIn("line 1", text)

    def test_changes_are_only_in_memory(self) -> None:
        """Changing loaded VFS must not change JSON."""
        self.vfs.root["children"]["temporary"] = {
            "type": "dir",
            "children": {},
        }
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"
        reloaded = VirtualFileSystem.from_json(str(path))
        self.assertNotIn("temporary", reloaded.root["children"])


if __name__ == "__main__":
    unittest.main()
