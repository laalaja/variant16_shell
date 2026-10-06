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
    """Test loading virtual file systems."""

    def test_load_demo_vfs(self) -> None:
        """Demo VFS should load from JSON."""
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"

        vfs = VirtualFileSystem.from_json(str(path))

        self.assertEqual(vfs.name, "demo-vfs")

    def test_nested_directories_exist(self) -> None:
        """Demo VFS should contain nested directories."""
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"

        vfs = VirtualFileSystem.from_json(str(path))

        home = vfs.root["children"]["home"]
        student = home["children"]["student"]
        docs = student["children"]["docs"]

        self.assertIn(
            "notes.txt",
            docs["children"],
        )

    def test_changes_are_only_in_memory(self) -> None:
        """Changing loaded VFS must not change JSON."""
        path = PROJECT_ROOT / "fixtures" / "vfs_demo.json"

        first = VirtualFileSystem.from_json(str(path))

        first.root["children"]["temporary"] = {
            "type": "dir",
            "children": {},
        }

        second = VirtualFileSystem.from_json(str(path))

        self.assertNotIn(
            "temporary",
            second.root["children"],
        )


if __name__ == "__main__":
    unittest.main()