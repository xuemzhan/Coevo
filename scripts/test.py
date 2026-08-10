"""Unified offline test entry point (REVIEW2-1).

The repository intentionally keeps suites in separate directories because
security, integration and E2E tests have different toolchain requirements.
This script is the single discoverable entry point for those suites and
fails closed when a selected suite discovers zero tests, so a misconfigured
discovery can never be reported as "all green".

Usage::

    python scripts/test.py --suite unit
    python scripts/test.py --suite integration
    python scripts/test.py --suite security
    python scripts/test.py --suite e2e
    python scripts/test.py --suite win7
    python scripts/test.py --suite all
    python scripts/test.py --suite unit --json

Exit codes: 0 = pass (discovered > 0), 1 = test failures/errors,
3 = zero tests discovered (fail-closed), 64 = usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUITE_PATTERNS = {
    "unit": "test_*.py",
    "integration": "*test*.py",
    "security": "test_*.py",
    "e2e": "test_*.py",
    "win7": "test_*.py",
}
SUITES = ("unit", "integration", "security", "e2e", "win7")
NO_TESTS_EXIT = 3
USAGE_EXIT = 64


def suite_dir(root: Path, suite: str) -> Path:
    if suite not in SUITE_PATTERNS:
        raise SystemExit(f"unknown suite: {suite!r} (choose from {', '.join(SUITES)})")
    return root / "tests" / suite


def _discover(root: Path, suite: str, result: unittest.TestResult) -> int:
    """Load every matching test file; count discovered tests, fail closed."""

    directory = suite_dir(root, suite)
    if not directory.is_dir():
        return 0
    loader = unittest.TestLoader()
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "tests"))
    sys.path.insert(0, str(root / "src"))
    discovered = 0
    for test_file in sorted(directory.glob(SUITE_PATTERNS[suite])):
        relative = test_file.relative_to(root)
        module_name = ".".join(relative.with_suffix("").parts)
        if module_name.startswith("tests."):
            module_name = module_name[len("tests."):]
        try:
            loaded = loader.loadTestsFromName(module_name)
        except Exception as exc:  # noqa: BLE001 - fail closed on load errors
            result.errors.append((None, f"{module_name}: {type(exc).__name__}: {exc}"))
            continue
        discovered += loaded.countTestCases()
        loaded.run(result)
    return discovered


def run_suite(root: Path, suite: str) -> dict[str, object]:
    started = time.monotonic()
    result = unittest.TestResult()
    discovered = _discover(root, suite, result)
    duration_ms = int((time.monotonic() - started) * 1000)
    if discovered == 0:
        return {
            "suite": suite,
            "discovered": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration_ms": duration_ms,
            "exit_code": NO_TESTS_EXIT,
            "ok": False,
            "reason": "no tests discovered; fail closed",
        }
    for test, trace in result.failures + result.errors:
        print("=" * 70, file=sys.stderr)
        print(f"FAILED/ERROR: {test}", file=sys.stderr)
        print(trace, file=sys.stderr)
    passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    failed = len(result.failures) + len(result.errors)
    exit_code = 1 if failed else 0
    return {
        "suite": suite,
        "discovered": result.testsRun,
        "passed": passed,
        "failed": failed,
        "skipped": len(result.skipped),
        "duration_ms": duration_ms,
        "exit_code": exit_code,
        "ok": exit_code == 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Unified offline test entry point")
    parser.add_argument(
        "--suite",
        required=True,
        choices=(*SUITES, "all"),
        help="test suite to run; 'all' runs every suite sequentially",
    )
    parser.add_argument("--json", action="store_true", help="print a JSON summary")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    suites = SUITES if args.suite == "all" else (args.suite,)
    summaries = [run_suite(args.root.resolve(), suite) for suite in suites]
    total = {
        "discovered": sum(int(s["discovered"]) for s in summaries),
        "passed": sum(int(s["passed"]) for s in summaries),
        "failed": sum(int(s["failed"]) for s in summaries),
        "skipped": sum(int(s["skipped"]) for s in summaries),
        "duration_ms": sum(int(s["duration_ms"]) for s in summaries),
    }
    worst = max(int(s["exit_code"]) for s in summaries) if summaries else USAGE_EXIT
    report = {
        "ok": worst == 0 and total["discovered"] > 0,
        "exit_code": worst,
        "suites": summaries,
        **total,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(
            f"discovered={total['discovered']} passed={total['passed']} "
            f"failed={total['failed']} skipped={total['skipped']} "
            f"duration_ms={total['duration_ms']}"
        )
        for summary in summaries:
            print(
                f"  [{summary['suite']}] discovered={summary['discovered']} "
                f"passed={summary['passed']} failed={summary['failed']} "
                f"skipped={summary['skipped']} exit={summary['exit_code']}"
            )
        if worst == NO_TESTS_EXIT:
            print("no tests discovered; fail closed", file=sys.stderr)
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
