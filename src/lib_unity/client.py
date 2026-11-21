"""Read-only wrapper for supported Unity CLI discovery commands."""
import json
import subprocess


class UnityCLIError(RuntimeError):
    """Unity CLI unavailable or reported a failed operation."""

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


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
        try:
            parsed = json.loads(result.stdout)
        except (ValueError, TypeError) as exc:
            raise UnityCLIError(
                f"Unity CLI {command} returned invalid JSON (exit {result.returncode})"
            ) from exc
        if not isinstance(parsed, (dict, list)):
            raise UnityCLIError("Unity CLI JSON response must be an object or list")
        if isinstance(parsed, dict) and "success" in parsed:
            if parsed["success"] is False:
                errors = parsed.get("errors")
                first = errors[0] if isinstance(errors, list) and errors else {}
                code = first.get("code") if isinstance(first, dict) else None
                raise UnityCLIError(
                    f"Unity CLI {command} reported {code or 'UNKNOWN_ERROR'} "
                    f"(exit {result.returncode})", code=code
                )
            if parsed["success"] is not True:
                raise UnityCLIError("Unity CLI JSON success must be a boolean")
        if result.returncode:
            raise UnityCLIError(f"Unity CLI {command} exited with {result.returncode}")
        return parsed

    def status(self):
        return self.query("status")

    def tools(self):
        return self.query("list")

    def commands(self):
        return self.query("commands")
