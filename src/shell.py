"""Command parsing and execution for the REPL prototype."""

from dataclasses import dataclass

from vfs import VirtualFileSystem

@dataclass
class CommandResult:
    """Represent the result of a command."""

    output: str = ""
    is_error: bool = False
    should_exit: bool = False

class ShellEmulator:
    """Implement the first REPL prototype."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        """Create the shell."""
        self.vfs = vfs
        self.handlers = {
            "ls": self._ls,
            "cd": self._cd,
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
        return f"{self.vfs_name}:/$"

    def _ls(self, args: list[str]) -> CommandResult:
        """Implement the ls stub."""
        if len(args) > 1:
            return self._usage("ls [PATH]")

        text = "Command: ls"
        if args:
            text += f"\nArguments: {' '.join(args)}"

        return CommandResult(text)

    def _cd(self, args: list[str]) -> CommandResult:
        """Implement the cd stub."""
        if len(args) != 1:
            return self._usage("cd PATH")

        return CommandResult(
            "Command: cd\n"
            f"Arguments: {' '.join(args)}"
        )

    def _exit(self, args: list[str]) -> CommandResult:
        """Implement exit."""
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