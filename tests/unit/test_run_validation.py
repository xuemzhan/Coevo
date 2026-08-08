"""OPTIMIZE-14: tests for the locked validation-report script (run_validation.py)."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "run_validation", ROOT / "scripts" / "run_validation.py"
)
run_validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_validation)


class StripJsoncTests(unittest.TestCase):
    def test_removes_line_and_block_comments_keeps_strings(self):
        src = (
            '{\n'
            '  // line comment\n'
            '  "a": "http://x", /* block */ "b": 1\n'
            '}\n'
        )
        out = run_validation.strip_jsonc(src)
        self.assertIn('"a": "http://x"', out)
        self.assertNotIn("line comment", out)
        self.assertNotIn("block", out)

    def test_keeps_slash_inside_string(self):
        out = run_validation.strip_jsonc('{"url": "a//b"}')
        self.assertIn('"a//b"', out)


class MetricsTests(unittest.TestCase):
    def test_backlog_status_counts(self):
        text = (
            "version: \"1.0\"\n"
            "items:\n"
            "  - id: A\n"
            "    status: done\n"
            "  - id: B\n"
            "    status: ready\n"
            "  - id: C\n"
            "    status: \"blocked\"\n"
        )
        items, counts = run_validation._backlog_status_counts(text)
        self.assertEqual(3, items)
        self.assertEqual({"done": 1, "ready": 1, "blocked": 1}, counts)

    def test_backlog_status_counts_ignores_status_like_strings(self):
        text = (
            "items:\n"
            "  - id: A\n"
            "    title: 'contains status: not-a-field'\n"
            "    status: done\n"
            "  - id: B\n"
            "    status: ready\n"
            "    note: |\n"
            "      indented text with status: fake at deeper level\n"
            "    status: done\n"
        )
        items, counts = run_validation._backlog_status_counts(text)
        self.assertEqual(2, items)
        self.assertEqual({"done": 2, "ready": 1}, counts)

    def test_backlog_status_counts_rejects_malformed_status(self):
        with self.assertRaises(ValueError):
            run_validation._backlog_status_counts(
                "items:\n  - id: A\n    status:\n"
            )

    def test_collect_extra_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "opencode.jsonc").write_text(
                '{\n'
                '  // comment\n'
                '  "permission": {\n'
                '    "bash": {"deny": true},\n'
                '    "skill": {"review": "allow", "other": "deny"},\n'
                '    "task": {"x": "allow"}\n'
                '  }\n'
                '}\n',
                encoding="utf-8",
            )
            (root / "loop").mkdir()
            (root / "loop" / "BACKLOG.yaml").write_text(
                'version: "1.0"\nitems:\n  - id: A\n    status: done\n'
                '  - id: B\n    status: done\n',
                encoding="utf-8",
            )
            (root / "loop" / "tool-audit.jsonl").write_text(
                '{"ts": "2026-08-01T00:00:00Z"}\n{"ts": "2026-08-02T00:00:00Z"}\n',
                encoding="utf-8",
            )
            with mock.patch.object(run_validation, "ROOT", root):
                metrics = run_validation.collect_extra_metrics()
        self.assertEqual(["bash", "skill", "task"], metrics["opencode_jsonc"]["permission_top_keys"])
        self.assertEqual(["deny"], metrics["opencode_jsonc"]["bash_subkeys"])
        self.assertEqual(["review"], metrics["opencode_jsonc"]["skill_allow"])
        self.assertEqual(["x"], metrics["opencode_jsonc"]["task_allow"])
        self.assertEqual(2, metrics["backlog"]["items"])
        self.assertEqual({"done": 2}, metrics["backlog"]["status_counts"])
        self.assertEqual(2, metrics["audit"]["lines"])

    def test_render_text_contains_key_sections(self):
        metrics = {
            "root": "C:/repo",
            "files": {"expected": 1, "missing": ["x"], "missing_count": 1},
            "backlog": {"items": 2, "status_counts": {"done": 2}},
            "audit": {"lines": 3},
            "opencode_jsonc": {"permission_top_keys": [], "bash_subkeys": [],
                               "skill_allow": [], "task_allow": []},
            "org_policy": {"path": "C:/x", "exists": False},
            "timestamp": "2026-08-07T00:00:00Z",
            "duration_ms": 1,
        }
        text = run_validation.render_text(metrics, "validator out", 0)
        self.assertIn("validate_opencode.py", text)
        self.assertIn("{'done': 2}", text)
        self.assertIn("C:/repo", text)
        self.assertIn("validator out", text)


if __name__ == "__main__":
    unittest.main()
