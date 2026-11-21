"""Read-only wrapper for supported Unity CLI discovery commands."""
import json
import subprocess


class UnityCLIError(RuntimeError):
    """Unity CLI missing, timed out or returned an error."""


class UnityCLI:
    """Read-only facade: no arbitrary shell or Unity Editor code execution."""

    ALLOWED = frozenset({"status", "list", "commands"})

    def __init__(self, executable="unity", timeout=15, runner=None):
        if not isinstance(executable, str) or not executable.strip():
            raise ValueError("A Unity CLI executable is required")
        if timeout <= 0 or timeout > 60:
            raise ValueError("timeout must be in (0, 60] seconds")
        self.executable = executable
        self.timeout = timeout
        self.runner = runner or subprocess.run

    def query(self, command):
        if command not in self.ALLOWED:
            raise ValueError("Only read-only Unity CLI discovery is supported")
        argv = [self.executable, command, "--format", "json"]
        try:
            result = self.runner(argv, capture_output=True, text=True,
                                 timeout=self.timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise UnityCLIError(f"Unity CLI unavailable: {type(exc).__name__}") from exc
        if result.returncode:
            raise UnityCLIError(f"Unity CLI {command} exited with {result.returncode}")
        try:
            return json.loads(result.stdout)
        except (ValueError, TypeError) as exc:
            raise UnityCLIError("Unity CLI did not return JSON") from exc

    def status(self):
        return self.query("status")

    def tools(self):
        return self.query("list")

    def commands(self):
        return self.query("commands")
