"""Offline Unity CLI adapter tests. Never run a real Editor."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
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

    def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            UnityCLI(timeout=0)


if __name__ == "__main__":
    unittest.main()
