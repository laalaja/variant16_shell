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
    """Execute shell commands against an in-memory VFS."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        """Create the shell at the VFS root."""
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
            return CommandResult(str(error), is_error=True)

        return CommandResult("\n".join(items))

    def _cd(self, args: list[str]) -> CommandResult:
        """Change the current directory."""
        if len(args) != 1:
            return self._usage("cd PATH")

        try:
            self.cwd = self.vfs.change_dir(args[0], self.cwd)
        except VFSError as error:
            return CommandResult(str(error), is_error=True)

        return CommandResult()

    def _cal(self, args: list[str]) -> CommandResult:
        """Display a calendar."""
        try:
            if not args:
                today = date.today()
                text = calendar.month(today.year, today.month)
            elif len(args) == 1:
                year = int(args[0])
                text = calendar.calendar(year)
            elif len(args) == 2:
                month = int(args[0])
                year = int(args[1])
                text = calendar.month(year, month)
            else:
                return self._usage("cal [MONTH] [YEAR]")
        except (ValueError, calendar.IllegalMonthError):
            return CommandResult(
                "Invalid calendar arguments",
                is_error=True,
            )

        return CommandResult(text.rstrip())

    def _head(self, args: list[str]) -> CommandResult:
        """Display the first lines of a file."""
        count = 10

        if len(args) == 1:
            path = args[0]
        elif len(args) == 3 and args[0] == "-n":
            try:
                count = int(args[1])
            except ValueError:
                return self._usage("head [-n COUNT] FILE")

            path = args[2]
        else:
            return self._usage("head [-n COUNT] FILE")

        if count < 0:
            return CommandResult(
                "COUNT must be non-negative",
                is_error=True,
            )

        try:
            text = self.vfs.read_text(path, self.cwd)
        except VFSError as error:
            return CommandResult(str(error), is_error=True)

        lines = text.splitlines()[:count]

        return CommandResult("\n".join(lines))

    def _tac(self, args: list[str]) -> CommandResult:
        """Display file lines in reverse order."""
        if len(args) != 1:
            return self._usage("tac FILE")

        try:
            text = self.vfs.read_text(args[0], self.cwd)
        except VFSError as error:
            return CommandResult(str(error), is_error=True)

        lines = reversed(text.splitlines())

        return CommandResult("\n".join(lines))

    def _mkdir(self, args: list[str]) -> CommandResult:
        """Create one directory in the VFS."""
        if len(args) != 1:
            return self._usage("mkdir DIRECTORY")

        try:
            self.vfs.make_dir(args[0], self.cwd)
        except VFSError as error:
            return CommandResult(str(error), is_error=True)

        return CommandResult()

    def _exit(self, args: list[str]) -> CommandResult:
        """Request application termination."""
        if args:
            return self._usage("exit")

        return CommandResult(should_exit=True)

    @staticmethod
    def _usage(text: str) -> CommandResult:
        """Return an invalid-arguments error."""
        return CommandResult(
            f"Usage: {text}",
            is_error=True,
        )
