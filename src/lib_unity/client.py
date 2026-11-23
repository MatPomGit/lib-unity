"""Read-only wrapper for supported Unity CLI discovery commands."""
import json
import subprocess
import threading


class UnityCLIError(RuntimeError):
    """Unity CLI unavailable or reported a failed operation."""

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class UnityCLI:
    """Read-only facade: no arbitrary shell or Unity Editor code execution."""

    ALLOWED = frozenset({"status", "list", "commands"})
    MAX_OUTPUT_BYTES = 1024 * 1024

    def __init__(self, executable="unity", timeout=15, runner=None):
        if not isinstance(executable, str) or not executable.strip():
            raise ValueError("A Unity CLI executable is required")
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 60:
            raise ValueError("timeout must be in (0, 60] seconds")
        self.executable = executable
        self.timeout = timeout
        # The injected runner is used for isolated tests only.
        self.runner = runner

    def _run_bounded(self, argv):
        """Bound captured stdout and kill a slow or overproducing CLI."""
        process = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, shell=False,
        )
        expired = threading.Event()

        def stop_process():
            if process.poll() is None:
                expired.set()
                process.kill()

        timer = threading.Timer(self.timeout, stop_process)
        timer.daemon = True
        timer.start()
        try:
            # read() cannot allocate beyond this bound even if CLI streams endlessly.
            raw = process.stdout.read(self.MAX_OUTPUT_BYTES + 1)
            if len(raw) > self.MAX_OUTPUT_BYTES:
                if process.poll() is None:
                    process.kill()
                process.wait()
                raise UnityCLIError("Unity CLI JSON output exceeds 1 MiB limit")
            process.wait()
            if expired.is_set():
                raise subprocess.TimeoutExpired(argv, self.timeout)
            return subprocess.CompletedProcess(
                argv, process.returncode, raw.decode("utf-8")
            )
        finally:
            timer.cancel()
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()

    def query(self, command):
        if not isinstance(command, str) or command not in self.ALLOWED:
            raise ValueError("Only read-only Unity CLI discovery is supported")
        argv = [self.executable, command, "--format", "json"]
        try:
            if self.runner is None:
                result = self._run_bounded(argv)
            else:
                result = self.runner(
                    argv, capture_output=True, text=True,
                    timeout=self.timeout, check=False,
                )
            # Keep injected test runners under the same response contract.
            if not isinstance(result.stdout, str) or (
                len(result.stdout.encode("utf-8")) > self.MAX_OUTPUT_BYTES
            ):
                raise UnityCLIError("Unity CLI JSON output exceeds 1 MiB limit")
        except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
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
