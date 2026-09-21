"""In-memory virtual file system loaded from JSON."""

import base64
import json
from pathlib import Path


class VFSError(Exception):
    """Raised when a virtual file system operation fails."""


def _normalize(cwd: str, path: str) -> list[str]:
    """Return normalized VFS path components."""
    if path.startswith("/"):
        parts: list[str] = []
    else:
        parts = [part for part in cwd.split("/") if part]

    for part in path.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return parts


class VirtualFileSystem:
    """Represent a JSON-backed VFS whose changes stay in memory."""

    def __init__(self, name: str, root: dict) -> None:
        """Create a VFS from its name and root node."""
        self.name = name
        self.root = root

    @classmethod
    def from_json(cls, file_path: str) -> "VirtualFileSystem":
        """Load a virtual file system from a JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise VFSError(f"VFS file not found: {file_path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VFSError(f"Cannot load VFS: {exc}") from exc

        if "name" not in data or "root" not in data:
            raise VFSError("Invalid VFS format: name/root are required")
        if data["root"].get("type") != "dir":
            raise VFSError("Invalid VFS format: root must be a directory")
        return cls(str(data["name"]), data["root"])

    def resolve(self, path: str, cwd: str) -> dict:
        """Resolve a VFS path and return the target node."""
        node = self.root
        for part in _normalize(cwd, path):
            if node.get("type") != "dir":
                raise VFSError(f"Not a directory: {part}")
            children = node.get("children", {})
            if part not in children:
                raise VFSError(f"No such file or directory: {path}")
            node = children[part]
        return node

    def list_dir(self, path: str, cwd: str) -> list[str]:
        """List directory entries or return a single file name."""
        target = path or "."
        node = self.resolve(target, cwd)
        if node.get("type") == "file":
            return [target.rstrip("/").split("/")[-1]]
        return sorted(node.get("children", {}).keys())

    def change_dir(self, path: str, cwd: str) -> str:
        """Validate and return the new current directory."""
        node = self.resolve(path, cwd)
        if node.get("type") != "dir":
            raise VFSError(f"Not a directory: {path}")
        parts = _normalize(cwd, path)
        return "/" + "/".join(parts) if parts else "/"

    def read_text(self, path: str, cwd: str) -> str:
        """Read a text file from the VFS."""
        node = self.resolve(path, cwd)
        if node.get("type") != "file":
            raise VFSError(f"Is a directory: {path}")
        encoding = node.get("encoding", "text")
        content = node.get("content", "")
        if encoding == "text":
            return str(content)
        if encoding == "base64":
            try:
                raw = base64.b64decode(content)
                return raw.decode("utf-8")
            except (ValueError, UnicodeDecodeError) as exc:
                raise VFSError(f"Binary file cannot be shown: {path}") \
                    from exc
        raise VFSError(f"Unsupported encoding: {encoding}")

    def make_dir(self, path: str, cwd: str) -> None:
        """Create one directory in memory."""
        parts = _normalize(cwd, path)
        if not parts:
            raise VFSError("Cannot create the root directory")
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1])
        parent = self.resolve(parent_path or "/", "/")
        if parent.get("type") != "dir":
            raise VFSError(f"Parent is not a directory: {path}")
        children = parent.setdefault("children", {})
        if name in children:
            raise VFSError(f"File exists: {path}")
        children[name] = {"type": "dir", "children": {}}
