"""Program entry point for the shell emulator."""

import argparse
import tkinter as tk

from app import ShellGUI
from shell import ShellEmulator
from vfs import VFSError, VirtualFileSystem


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--vfs",
        required=True,
        help="Path to the virtual file system",
    )

    parser.add_argument(
        "--script",
        help="Path to the startup script",
    )

    return parser.parse_args()


def main() -> None:
    """Start the shell emulator."""
    args = parse_arguments()

    try:
        vfs = VirtualFileSystem.from_json(
            args.vfs
        )
    except VFSError as error:
        print(f"VFS error: {error}")
        return

    shell = ShellEmulator(vfs)

    root = tk.Tk()

    ShellGUI(
        root,
        shell,
        args.vfs,
        args.script,
    )

    root.mainloop()


if __name__ == "__main__":
    main()