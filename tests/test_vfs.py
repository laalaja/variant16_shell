"""Tests for the JSON virtual file system."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from vfs import VFSError, VirtualFileSystem


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class VFSTests(unittest.TestCase):
    """Test loading and using virtual file systems."""

    def setUp(self) -> None:
        """Create a small VFS for operation tests."""
        self.vfs = VirtualFileSystem(
            "test-vfs",
            {
                "type": "dir",
                "children": {
                    "home": {
                        "type": "dir",
                        "children": {
                            "note.txt": {
                                "type": "file",
                                "encoding": "text",
                                "content": "first\nsecond",
                            },
                        },
                    },
                },
            },
        )

    def test_load_demo_vfs(self) -> None:
        """Demo VFS should load from JSON."""
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"

        vfs = VirtualFileSystem.from_json(str(path))

        self.assertEqual(vfs.name, "demo-vfs")

    def test_resolve_relative_path(self) -> None:
        """Relative paths should be normalized against cwd."""
        path = self.vfs.resolve_path("../home", "/home")

        self.assertEqual(path, "/home")

    def test_list_and_change_directory(self) -> None:
        """Directories should support listing and navigation."""
        self.assertEqual(self.vfs.list_dir("/", "/"), ["home"])
        self.assertEqual(
            self.vfs.change_dir("home", "/"),
            "/home",
        )

    def test_read_text(self) -> None:
        """Text files should be readable."""
        text = self.vfs.read_text("note.txt", "/home")

        self.assertEqual(text, "first\nsecond")

    def test_make_dir(self) -> None:
        """make_dir should add an empty directory."""
        self.vfs.make_dir("projects", "/home")

        projects = self.vfs.get_node("/home/projects")
        self.assertEqual(
            projects,
            {"type": "dir", "children": {}},
        )

    def test_make_dir_with_absolute_path(self) -> None:
        """make_dir should support an absolute path."""
        self.vfs.make_dir("/archive", "/home")

        self.assertIn("archive", self.vfs.list_dir("/", "/"))

    def test_make_dir_requires_existing_parent(self) -> None:
        """make_dir should not create missing parent directories."""
        with self.assertRaises(VFSError):
            self.vfs.make_dir("missing/child", "/")

    def test_make_dir_rejects_existing_name(self) -> None:
        """make_dir should not overwrite an existing node."""
        with self.assertRaises(VFSError):
            self.vfs.make_dir("home", "/")

    def test_make_dir_rejects_root(self) -> None:
        """make_dir should not recreate the VFS root."""
        with self.assertRaises(VFSError):
            self.vfs.make_dir("/", "/")

    def test_changes_are_only_in_memory(self) -> None:
        """Changing loaded VFS must not change JSON."""
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"
        first = VirtualFileSystem.from_json(str(path))

        first.make_dir("temporary", "/")
        second = VirtualFileSystem.from_json(str(path))

        self.assertNotIn(
            "temporary",
            second.root["children"],
        )


if __name__ == "__main__":
    unittest.main()
