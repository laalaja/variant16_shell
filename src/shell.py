"""Command parsing and execution for the shell emulator."""

import calendar
from dataclasses import dataclass
from datetime import date

from vfs import VFSError, VirtualFileSystem


@dataclass
class CommandResult:
    """Represent the result of a command."""

    output: str = ""
    is_error: bool = False
    should_exit: bool = False


class ShellEmulator:
    """Execute commands against a virtual file system."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        """Create the shell."""
        self.vfs = vfs
        self.cwd = "/"
        self.handlers = {
            "ls": self._ls,
            "cd": self._cd,
            "cal": self._cal,
            "head": self._head,
            "tac": self._tac,
            "exit": self._exit,
        }

    @property
    def vfs_name(self) -> str:
        """Return the VFS name."""
        return self.vfs.name

    def parse(self, line: str) -> tuple[str, list[str]]:
        """Split a line into command and arguments."""
        parts = line.strip().split()
        if not parts:
            return "", []
        return parts[0], parts[1:]

    def execute(self, line: str) -> CommandResult:
        """Execute one command."""
        command, args = self.parse(line)
        if not command:
            return CommandResult()

        handler = self.handlers.get(command)
        if handler is None:
            return CommandResult(
                f"Unknown command: {command}",
                is_error=True,
            )
        return handler(args)

    def prompt(self) -> str:
        """Return the command prompt."""
        return f"{self.vfs_name}:{self.cwd}$"

    def _ls(self, args: list[str]) -> CommandResult:
        """List directory contents."""
        if len(args) > 1:
            return self._usage("ls [PATH]")

        path = args[0] if args else "."
        try:
            items = self.vfs.list_dir(path, self.cwd)
        except VFSError as error:
            return self._error(error)
        return CommandResult("\n".join(items))

    def _cd(self, args: list[str]) -> CommandResult:
        """Change the current directory."""
        if len(args) != 1:
            return self._usage("cd PATH")

        try:
            self.cwd = self.vfs.change_dir(args[0], self.cwd)
        except VFSError as error:
            return self._error(error)
        return CommandResult()

    def _cal(self, args: list[str]) -> CommandResult:
        """Display a month or year calendar."""
        try:
            text = self._calendar_text(args)
        except (ValueError, calendar.IllegalMonthError):
            return CommandResult(
                "Invalid calendar arguments",
                is_error=True,
            )
        return CommandResult(text.rstrip())

    @staticmethod
    def _calendar_text(args: list[str]) -> str:
        """Build calendar output from command arguments."""
        if not args:
            today = date.today()
            return calendar.month(today.year, today.month)
        if len(args) == 1:
            return calendar.calendar(int(args[0]))
        if len(args) == 2:
            month = int(args[0])
            year = int(args[1])
            return calendar.month(year, month)
        raise ValueError

    def _head(self, args: list[str]) -> CommandResult:
        """Display the first lines of a file."""
        parsed = self._parse_head_arguments(args)
        if isinstance(parsed, CommandResult):
            return parsed

        count, path = parsed
        try:
            text = self.vfs.read_text(path, self.cwd)
        except VFSError as error:
            return self._error(error)

        return CommandResult("\n".join(text.splitlines()[:count]))

    def _parse_head_arguments(
        self,
        args: list[str],
    ) -> tuple[int, str] | CommandResult:
        """Parse head command arguments."""
        if len(args) == 1:
            return 10, args[0]

        if len(args) != 3 or args[0] != "-n":
            return self._usage("head [-n COUNT] FILE")

        try:
            count = int(args[1])
        except ValueError:
            return self._usage("head [-n COUNT] FILE")

        if count < 0:
            return CommandResult(
                "COUNT must be non-negative",
                is_error=True,
            )
        return count, args[2]

    def _tac(self, args: list[str]) -> CommandResult:
        """Display file lines in reverse order."""
        if len(args) != 1:
            return self._usage("tac FILE")

        try:
            text = self.vfs.read_text(args[0], self.cwd)
        except VFSError as error:
            return self._error(error)

        lines = reversed(text.splitlines())
        return CommandResult("\n".join(lines))

    def _exit(self, args: list[str]) -> CommandResult:
        """Request application termination."""
        if args:
            return self._usage("exit")
        return CommandResult(should_exit=True)

    @staticmethod
    def _error(error: Exception) -> CommandResult:
        """Convert an exception to a command error result."""
        return CommandResult(str(error), is_error=True)

    @staticmethod
    def _usage(text: str) -> CommandResult:
        """Return an invalid-arguments error."""
        return CommandResult(f"Usage: {text}", is_error=True)
