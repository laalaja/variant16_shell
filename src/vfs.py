"""Virtual file system loaded from JSON."""

import base64
import json
from pathlib import Path


class VFSError(Exception):
    """Raised when the VFS cannot be loaded."""


class VirtualFileSystem:
    """Represent a virtual file system stored in memory."""

    def __init__(self, name: str, root: dict) -> None:
        """Create a VFS from its name and root node."""
        self.name = name
        self.root = root

    @classmethod
    def from_json(cls, file_path: str) -> "VirtualFileSystem":
        """Load a VFS from a JSON file."""
        path = Path(file_path)

        if not path.exists():
            raise VFSError(
                f"VFS file not found: {file_path}"
            )

        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (OSError, json.JSONDecodeError) as error:
            raise VFSError(
                f"Cannot load VFS: {error}"
            ) from error

        cls._validate(data)

        return cls(
            str(data["name"]),
            data["root"],
        )

    @staticmethod
    def _validate(data: dict) -> None:
        """Validate the basic VFS structure."""
        if "name" not in data or "root" not in data:
            raise VFSError(
                "Invalid VFS: name and root are required"
            )

        root = data["root"]

        if root.get("type") != "dir":
            raise VFSError(
                "Invalid VFS: root must be a directory"
            )

        VirtualFileSystem._validate_node(root)

    @staticmethod
    def _validate_node(node: dict) -> None:
        """Validate one VFS node recursively."""
        node_type = node.get("type")

        if node_type == "dir":
            children = node.get("children", {})

            if not isinstance(children, dict):
                raise VFSError(
                    "Invalid VFS: children must be an object"
                )

            for child in children.values():
                VirtualFileSystem._validate_node(child)

            return

        if node_type == "file":
            VirtualFileSystem._validate_file(node)
            return

        raise VFSError(
            f"Invalid VFS node type: {node_type}"
        )

    @staticmethod
    def _validate_file(node: dict) -> None:
        """Validate file content and encoding."""
        encoding = node.get("encoding", "text")
        content = node.get("content", "")

        if encoding == "text":
            return

        if encoding == "base64":
            try:
                base64.b64decode(
                    content,
                    validate=True,
                )
            except (ValueError, TypeError) as error:
                raise VFSError(
                    "Invalid base64 file content"
                ) from error
            return

        raise VFSError(
            f"Unsupported encoding: {encoding}"
        )