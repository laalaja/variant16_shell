"""Tkinter graphical interface for the shell emulator."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from shell import ShellEmulator


class ShellGUI:
    """Display the graphical REPL."""

    def __init__(
        self,
        root: tk.Tk,
        shell: ShellEmulator,
        vfs_path: str,
        script_path: str | None,
    ) -> None:
        """Create the graphical interface."""
        self.root = root
        self.shell = shell

        self.root.title(
            f"Shell emulator - {shell.vfs_name}"
        )

        self._build_widgets()

        self._write(f"[config] vfs={vfs_path}\n")
        self._write(
            f"[config] script={script_path or '-'}\n\n"
        )

        if script_path:
            self.root.after(
                100,
                lambda: self._run_script(script_path),
            )

    def _build_widgets(self) -> None:
        """Create output and input widgets."""
        self._build_output()
        self._build_command_line()

    def _build_output(self) -> None:
        """Create the command output area."""
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

    def _build_command_line(self) -> None:
        """Create the prompt and command entry widgets."""
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

        self._execute_and_show(line)

    def _execute_and_show(self, line: str) -> bool:
        """Execute a command and display its result."""
        self._write(
            f"{self.shell.prompt()} {line}\n"
        )

        result = self.shell.execute(line)

        if result.output:
            self._write(result.output + "\n")

        if result.should_exit:
            self.root.destroy()
            return False

        return not result.is_error

    def _run_script(self, script_path: str) -> None:
        """Execute startup script until the first error."""
        path = Path(script_path)

        try:
            lines = path.read_text(
                encoding="utf-8"
            ).splitlines()
        except OSError as error:
            self._write(
                f"Startup script error: {error}\n"
            )
            return

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            if not self._execute_and_show(line):
                self._write(
                    "Startup script stopped "
                    f"at line {line_number}\n"
                )
                break

    def _write(self, text: str) -> None:
        """Append text to the output widget."""
        self.output.config(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")
