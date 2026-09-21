"""Program entry point for variant 16 shell emulator."""

import argparse
from pathlib import Path
import sys
import tkinter as tk

from app import ShellGUI
from shell import ShellEmulator
from vfs import VFSError, VirtualFileSystem


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="GUI UNIX-like shell emulator",
    )
    parser.add_argument(
        "--vfs",
        required=True,
        help="path to a JSON VFS file",
    )
    parser.add_argument(
        "--script",
        help="path to a startup script",
    )
    return parser


def validate_script(path: str | None) -> str | None:
    """Validate startup script path if one was supplied."""
    if path is None:
        return None
    if not Path(path).is_file():
        raise ValueError(f"Startup script not found: {path}")
    return path


def main() -> int:
    """Load configuration, VFS, and start the GUI."""
    args = build_parser().parse_args()
    try:
        script_path = validate_script(args.script)
        vfs = VirtualFileSystem.from_json(args.vfs)
    except (VFSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    root = tk.Tk()
    shell = ShellEmulator(vfs)
    ShellGUI(root, shell, args.vfs, script_path)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
