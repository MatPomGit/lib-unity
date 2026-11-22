"""Offline Unity CLI adapter tests. Never run a real Editor."""
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lib_unity.client import UnityCLI, UnityCLIError


class UnityClientTests(unittest.TestCase):
    def test_status_uses_argument_vector_and_json(self):
        calls = []
        def fake(argv, **kwargs):
            calls.append((argv, kwargs))
            return SimpleNamespace(returncode=0, stdout=json.dumps({"editors": []}))
        result = UnityCLI(runner=fake).status()
        self.assertEqual(result, {"editors": []})
        self.assertEqual(calls[0][0], ["unity", "status", "--format", "json"])
        self.assertEqual(calls[0][1]["timeout"], 15)
        self.assertFalse(calls[0][1]["check"])

    def test_tool_listing(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=0, stdout='{"tools":[]}'))
        self.assertEqual(client.tools(), {"tools": []})

    def test_rejects_mutating_and_unknown_commands(self):
        client = UnityCLI(runner=lambda *a, **k: self.fail("runner invoked"))
        for cmd in ("command", "eval", "install", "open", "test", "build", ""):
            with self.subTest(cmd=cmd), self.assertRaises(ValueError):
                client.query(cmd)

    def test_nonzero_return_code(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=6, stdout=""))
        with self.assertRaises(UnityCLIError):
            client.status()

    def test_failed_json_envelope_exposes_stable_error_code(self):
        payload = {"success": False, "errors": [
            {"code": "STATUS_NO_INSTANCES", "message": "No active Editor"}]}
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=12, stdout=json.dumps(payload)))
        with self.assertRaises(UnityCLIError) as caught:
            client.status()
        self.assertEqual(caught.exception.code, "STATUS_NO_INSTANCES")

    def test_failed_envelope_does_not_report_pass_on_exit_zero(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=0, stdout='{"success": false, "errors": []}'))
        with self.assertRaises(UnityCLIError):
            client.tools()

    def test_successful_json_envelope_preserved(self):
        payload = {"success": True, "command": "status", "data": {"editors": []}}
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=json.dumps(payload)))
        self.assertEqual(client.status(), payload)

    def test_invalid_success_type_rejected(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=0, stdout='{"success": "false"}'))
        with self.assertRaises(UnityCLIError):
            client.commands()

    def test_nonzero_exit_even_when_envelope_success(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=6, stdout='{"success": true, "data": {}}'))
        with self.assertRaises(UnityCLIError):
            client.status()

    def test_missing_binary(self):
        def missing(*args, **kwargs):
            raise FileNotFoundError("unity")
        with self.assertRaises(UnityCLIError):
            UnityCLI(runner=missing).status()

    def test_timeout(self):
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired("unity", timeout=1)
        with self.assertRaises(UnityCLIError):
            UnityCLI(runner=timeout).status()

    def test_invalid_json(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=0, stdout="not json"))
        with self.assertRaises(UnityCLIError):
            client.tools()


    def test_unhashable_and_nonstring_commands_are_rejected(self):
        client = UnityCLI(runner=lambda *a, **k: self.fail("runner invoked"))
        for command in ([], {}, None, 3, True):
            with self.subTest(command=repr(command)), self.assertRaises(ValueError):
                client.query(command)

    def test_injected_runner_oversized_output_is_rejected(self):
        client = UnityCLI(runner=lambda *a, **k: SimpleNamespace(
            returncode=0, stdout="x" * (UnityCLI.MAX_OUTPUT_BYTES + 1)))
        with self.assertRaisesRegex(UnityCLIError, "exceeds"):
            client.status()

    def test_bounded_subprocess_accepts_small_json(self):
        process = mock.Mock()
        process.stdout = io.BytesIO(b'{"editors":[]}')
        process.poll.return_value = 0
        process.wait.return_value = 0
        process.returncode = 0
        with mock.patch("lib_unity.client.subprocess.Popen", return_value=process) as popen:
            self.assertEqual(UnityCLI().status(), {"editors": []})
        self.assertFalse(popen.call_args.kwargs["shell"])
        self.assertIs(popen.call_args.kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(popen.call_args.args[0], ["unity", "status", "--format", "json"])

    def test_bounded_subprocess_rejects_oversized_stream(self):
        process = mock.Mock()
        process.stdout = io.BytesIO(b"x" * (UnityCLI.MAX_OUTPUT_BYTES + 1))
        process.poll.return_value = None
        process.wait.return_value = -9
        process.returncode = -9
        with mock.patch("lib_unity.client.subprocess.Popen", return_value=process):
            with self.assertRaisesRegex(UnityCLIError, "exceeds"):
                UnityCLI().status()
        process.kill.assert_called()

    def test_bounded_subprocess_rejects_invalid_utf8(self):
        process = mock.Mock()
        process.stdout = io.BytesIO(b"\\xff")
        process.poll.return_value = 0
        process.wait.return_value = 0
        process.returncode = 0
        with mock.patch("lib_unity.client.subprocess.Popen", return_value=process):
            with self.assertRaises(UnityCLIError):
                UnityCLI().status()

    def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            UnityCLI(timeout=0)


if __name__ == "__main__":
    unittest.main()
