"""Program entry point for the shell emulator."""

import tkinter as tk

from app import ShellGUI
from shell import ShellEmulator


VFS_NAME = "demo-vfs"


def main() -> None:
    """Create the shell and start the graphical interface."""
    root = tk.Tk()
    shell = ShellEmulator(VFS_NAME)
    ShellGUI(root, shell)
    root.mainloop()


if __name__ == "__main__":
    main()