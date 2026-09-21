"""Tkinter graphical interface for the shell emulator."""

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from shell import ShellEmulator


class ShellGUI:
    """Display shell input and output in a simple Tkinter window."""

    def __init__(
        self,
        root: tk.Tk,
        shell: ShellEmulator,
        vfs_path: str,
        script_path: str | None,
    ) -> None:
        """Create widgets and optionally schedule a startup script."""
        self.root = root
        self.shell = shell
        self.script_path = script_path
        self.root.title(f"Shell emulator - {shell.vfs.name}")
        self._build_widgets()
        self._write(f"[config] vfs={vfs_path}\n")
        self._write(f"[config] script={script_path or '-'}\n\n")
        if script_path:
            self.root.after(100, self._run_startup_script)

    def _build_widgets(self) -> None:
        """Build the terminal-like text area and command entry."""
        self.output = tk.Text(
            self.root,
            width=90,
            height=28,
            state="disabled",
        )
        self.output.pack(fill="both", expand=True, padx=8, pady=8)

        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=8, pady=(0, 8))
        self.prompt_label = ttk.Label(frame, text=self.shell.prompt())
        self.prompt_label.pack(side="left")
        self.entry = ttk.Entry(frame)
        self.entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _on_enter(self, _event: object = None) -> None:
        """Execute the command entered by the user."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self._execute_and_show(line)

    def _execute_and_show(self, line: str) -> bool:
        """Run one command, show the dialogue, and return success."""
        self._write(f"{self.shell.prompt()} {line}\n")
        result = self.shell.execute(line)
        if result.output:
            self._write(result.output + "\n")
        self.prompt_label.config(text=self.shell.prompt())
        if result.should_exit:
            self.root.after(50, self.root.destroy)
        return not result.is_error

    def _run_startup_script(self) -> None:
        """Run startup commands and stop at the first error."""
        try:
            lines = Path(self.script_path).read_text(
                encoding="utf-8",
            ).splitlines()
        except OSError as exc:
            self._write(f"Startup script error: {exc}\n")
            return

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            if not self._execute_and_show(line):
                self._write(
                    "Startup script stopped at line "
                    f"{line_number}.\n"
                )
                break

    def _write(self, text: str) -> None:
        """Append text to the read-only output widget."""
        self.output.config(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")
