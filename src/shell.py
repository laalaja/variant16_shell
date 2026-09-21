"""Command execution logic for the UNIX-like shell emulator."""

import calendar
from dataclasses import dataclass
from datetime import datetime

from vfs import VFSError, VirtualFileSystem


@dataclass
class CommandResult:
    """Represent the result of a command execution."""

    output: str = ""
    is_error: bool = False
    should_exit: bool = False


class ShellEmulator:
    """Execute supported shell commands against an in-memory VFS."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        """Create a shell working at the VFS root."""
        self.vfs = vfs
        self.cwd = "/"
        self.handlers = {
            "ls": self._ls,
            "cd": self._cd,
            "cal": self._cal,
            "head": self._head,
            "tac": self._tac,
            "mkdir": self._mkdir,
            "exit": self._exit,
        }

    def parse(self, line: str) -> tuple[str, list[str]]:
        """Split input into a command and arguments by spaces."""
        parts = line.strip().split()
        if not parts:
            return "", []
        return parts[0], parts[1:]

    def execute(self, line: str) -> CommandResult:
        """Parse and execute one command line."""
        command, args = self.parse(line)
        if not command:
            return CommandResult()
        handler = self.handlers.get(command)
        if handler is None:
            return CommandResult(
                f"Unknown command: {command}",
                is_error=True,
            )
        try:
            return handler(args)
        except VFSError as exc:
            return CommandResult(str(exc), is_error=True)
        except ValueError as exc:
            return CommandResult(str(exc), is_error=True)

    def prompt(self) -> str:
        """Return the prompt displayed in the GUI."""
        return f"{self.vfs.name}:{self.cwd}$"

    def _ls(self, args: list[str]) -> CommandResult:
        """Implement ls [PATH]."""
        if len(args) > 1:
            return self._usage("ls [PATH]")
        path = args[0] if args else "."
        return CommandResult("\n".join(self.vfs.list_dir(path, self.cwd)))

    def _cd(self, args: list[str]) -> CommandResult:
        """Implement cd PATH."""
        if len(args) != 1:
            return self._usage("cd PATH")
        self.cwd = self.vfs.change_dir(args[0], self.cwd)
        return CommandResult()

    def _cal(self, args: list[str]) -> CommandResult:
        """Implement cal, cal YEAR, and cal MONTH YEAR."""
        now = datetime.now()
        if not args:
            return CommandResult(calendar.month(now.year, now.month))
        if len(args) == 1:
            year = self._positive_int(args[0], "year")
            return CommandResult(calendar.calendar(year))
        if len(args) == 2:
            month = self._positive_int(args[0], "month")
            year = self._positive_int(args[1], "year")
            if month > 12:
                raise ValueError("month must be from 1 to 12")
            return CommandResult(calendar.month(year, month))
        return self._usage("cal [YEAR] | cal MONTH YEAR")

    def _head(self, args: list[str]) -> CommandResult:
        """Implement head [-n N] FILE."""
        count, path = self._head_args(args)
        if path is None:
            return self._usage("head [-n N] FILE")
        text = self.vfs.read_text(path, self.cwd)
        return CommandResult("\n".join(text.splitlines()[:count]))

    def _tac(self, args: list[str]) -> CommandResult:
        """Implement tac FILE."""
        if len(args) != 1:
            return self._usage("tac FILE")
        text = self.vfs.read_text(args[0], self.cwd)
        return CommandResult("\n".join(reversed(text.splitlines())))

    def _mkdir(self, args: list[str]) -> CommandResult:
        """Implement mkdir DIRECTORY."""
        if len(args) != 1:
            return self._usage("mkdir DIRECTORY")
        self.vfs.make_dir(args[0], self.cwd)
        return CommandResult()

    def _exit(self, args: list[str]) -> CommandResult:
        """Implement exit."""
        if args:
            return self._usage("exit")
        return CommandResult(should_exit=True)

    def _head_args(self, args: list[str]) -> tuple[int, str | None]:
        """Parse arguments accepted by head."""
        default_count = 10
        if len(args) == 1:
            return default_count, args[0]
        if len(args) == 3 and args[0] == "-n":
            count = self._positive_int(args[1], "line count")
            return count, args[2]
        return default_count, None

    @staticmethod
    def _positive_int(value: str, name: str) -> int:
        """Parse a positive integer command argument."""
        try:
            number = int(value)
        except ValueError as exc:
            raise ValueError(f"{name} must be an integer") from exc
        if number <= 0:
            raise ValueError(f"{name} must be positive")
        return number

    @staticmethod
    def _usage(text: str) -> CommandResult:
        """Return a standard invalid-arguments error."""
        return CommandResult(f"Usage: {text}", is_error=True)
