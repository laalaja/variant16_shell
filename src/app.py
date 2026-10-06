"""Tkinter graphical interface for the shell emulator."""

import tkinter as tk
from tkinter import ttk

from shell import ShellEmulator


class ShellGUI:
    """Display the graphical REPL."""

    def __init__(
        self,
        root: tk.Tk,
        shell: ShellEmulator,
    ) -> None:
        """Create the graphical interface."""
        self.root = root
        self.shell = shell

        self.root.title(
            f"Shell emulator - {shell.vfs_name}"
        )

        self._build_widgets()

    def _build_widgets(self) -> None:
        """Create output and input widgets."""
        self.output = tk.Text(
            self.root,
            width=90,
            height=28,
            state="disabled",
        )
        self.output.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8,
        )

        frame = ttk.Frame(self.root)
        frame.pack(
            fill="x",
            padx=8,
            pady=(0, 8),
        )

        self.prompt_label = ttk.Label(
            frame,
            text=self.shell.prompt(),
        )
        self.prompt_label.pack(side="left")

        self.entry = ttk.Entry(frame)
        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
        )

        self.entry.bind(
            "<Return>",
            self._on_enter,
        )

        self.entry.focus_set()

    def _on_enter(self, _event: object = None) -> None:
        """Execute the entered command."""
        line = self.entry.get()
        self.entry.delete(0, "end")

        self._write(
            f"{self.shell.prompt()} {line}\n"
        )

        result = self.shell.execute(line)

        if result.output:
            self._write(result.output + "\n")

        if result.should_exit:
            self.root.destroy()

    def _write(self, text: str) -> None:
        """Append text to the output widget."""
        self.output.config(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")