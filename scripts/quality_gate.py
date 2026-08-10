"""Zero-download, fail-closed quality gate with a signed final audit seal.

The gate is serialized by an exclusive lock (``loop/.quality-gate.lock``):
a concurrent invocation waits briefly for the lock and then fails with a
clear error instead of interleaving VERIFICATION.md writes or racing the
audit seal. Run one gate at a time (the test suites are not parallel-safe).

All child processes are captured with a UTF-8 environment so their output
round-trips into VERIFICATION.md without mojibake on Windows consoles
(QUALITY-GATE-ENCODING-1).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from audit_log import append_record, exclusive_lock
from audit_seal import seal, verify_seal

ROOT = Path(
    os.environ.get("COEVO_REPO_ROOT", Path(__file__).resolve().parents[1])
)
VERIFICATION = ROOT / "loop" / "VERIFICATION.md"
os.environ.setdefault("COEVO_REPO_ROOT", str(ROOT))
GATE_LOCK=ROOT/"loop/.quality-gate.lock"
CONTROL=os.environ.get("COEVO_CONTROL_ARCHIVE",str(ROOT/".tools"/"control"/"control.pyz"))
CHILD_TIMEOUT_SECS=2400


def control(module, *args):
    return [sys.executable, CONTROL, module, *args]


def gate_env():
    """Child-process environment that forces UTF-8 stdout/stderr capture.

    Without ``PYTHONIOENCODING``/``PYTHONUTF8``, Python children on a
    Windows console emit GBK bytes, which the gate captures with
    ``errors="replace"`` and writes into VERIFICATION.md as irreversible
    replacement characters (QUALITY-GATE-ENCODING-1).
    """
    env=os.environ.copy()
    env["PYTHONIOENCODING"]="utf-8"
    env["PYTHONUTF8"]="1"
    return env


def go_test_argv():
    """Resolve the locked Go executable and return the offline Go test argv.

    GO-MIGRATE slice: `go test ./...` runs inside the `go/` module; the
    quality gate keeps the toolchain fully offline (GOPROXY=off) and only
    stdlib is permitted (no third-party Go modules).
    """
    lock = json.loads(
        (ROOT / "docs" / "dependencies" / "toolchain-lock.json").read_text(
            encoding="utf-8"
        )
    )
    go_tool = lock["tools"]["go"]["executable"]["path"]
    return [go_tool, "test", "./..."]
TARGETS = {
    "fmt": [
        [sys.executable, "-m", "compileall", "-q", "-f", "scripts", "src", "tests"]
    ],
    "lint": [
        [sys.executable, str(ROOT / "scripts" / "validate_opencode.py")],
        control("traceability_check"),
        control("audit_log", "verify"),
        [sys.executable, str(ROOT / "scripts" / "audit_seal.py"), "verify", "--allow-tail"],
        [sys.executable, str(ROOT / "scripts" / "archive_records.py"), "--check"],
        [sys.executable, str(ROOT / "scripts" / "secret_scan.py")],
    ],
    "test": [
        [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "unit"],
        [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "integration"],
        go_test_argv(),
    ],
    "test-security": [
        [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "security"],
        [
            os.environ.get(
                "COEVO_NODE_PATH",
                str(ROOT / ".tools" / "node" / "24.14.0" / "node.exe"),
            ),
            "tests/security/path_policy_test.mjs",
        ],
    ],
    "test-e2e": [
        [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "e2e"]
    ],
    "test-win7": [
        [sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "win7"]
    ],
}
# ARCH-REVIEW-7: fast tier for iteration loops (compileall + lint + unit);
# full `quality` stays the release/closure gate (fmt+lint+test+security+e2e).
# REVIEW2-1: every stage goes through the unified `scripts/test.py` entry,
# which fails closed on zero-test discovery.
TARGETS["fast"] = (
    TARGETS["fmt"]
    + TARGETS["lint"]
    + [[sys.executable, str(ROOT / "scripts" / "test.py"), "--suite", "unit"]]
)
GO_TEST_ARGV = TARGETS["test"][-1]
# ARCH-REVIEW-9: the Win7 compatibility subset is part of the full quality
# gate so the compat profile cannot silently rot.


def commands(target):
    if target == "quality":
        return [
            command
            for name in (
                "fmt",
                "lint",
                "test",
                "test-security",
                "test-e2e",
                "test-win7",
            )
            for command in TARGETS[name]
        ]
    return TARGETS[target]


def fingerprint(argvs):
    return hashlib.sha256(
        json.dumps(argvs, separators=(",", ":")).encode()
    ).hexdigest()[:16]

def _trim_records_to_policy(verification: Path = VERIFICATION) -> str:
    """Self-maintain loop-record capacity after the gate appended VERIFICATION.

    The gate grows ``VERIFICATION.md`` on every run; without self-trimming the
    lint stage's ``archive_records --check`` would force a manual ``--apply``
    once the file exceeds the policy cap. The generic archive tool is reused
    (audit is excluded by RECORDS-ARCHIVE-3), so the audit chain is never
    touched. Failures are isolated: a trim problem never takes the gate down
    and is caught by the next lint ``--check``.

    Returns a short human-readable note when records were archived, else "".
    """
    try:
        process = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "archive_records.py"), "--apply"],
            cwd=ROOT,
            env=gate_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        combined = (process.stdout + process.stderr).strip()
        if process.returncode != 0:
            return f"trim failed (exit={process.returncode}): {combined[:300]}"
        if "-> wrote" in combined or "[verification] archive" in combined or "[decisions] archive" in combined:
            return combined.replace("\n", "; ")[:500]
        return ""
    except Exception as exc:  # noqa: BLE001 - never take the gate down on trim failure
        return f"trim error: {type(exc).__name__}: {exc}"

def run(target):
    try:
        with exclusive_lock(GATE_LOCK):
            return _run_locked(target)
    except OSError as exc:
        raise RuntimeError(
            "quality gate is already running in another process "
            f"({GATE_LOCK}): {exc}"
        ) from exc

def _run_locked(target):
    argvs = commands(target)
    fp = fingerprint(argvs)
    started = time.monotonic()
    ts = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
    timeout_sec = STAGE_TIMEOUTS.get(target, CHILD_TIMEOUT_SECS)
    # Phase A: immutable test execution + machine-readable results artifact.
    results, rc = _run_stages(target, argvs, timeout_sec)
    total_ms = int((time.monotonic() - started) * 1000)
    artifact = _write_results_json(target, fp, rc, results, ts, total_ms)
    output = [stage.output for stage in results]
    if artifact.startswith("results artifact failed"):
        output.append(artifact+"\n")
    # Phase B: governance recording only after all stages finished.
    results_json = (
        Path(artifact)
        if not artifact.startswith("results artifact failed")
        else None
    )
    rc=_record_gate_result(
        target, fp, rc, output, ts, results_json=results_json
    )
    print(json.dumps({"ok":rc==0,"exit_code":rc,"fingerprint":fp})); return rc


@dataclass(frozen=True)
class StageResult:
    """Per-stage result collected during Phase A (REVIEW2-2)."""

    argv: tuple[str, ...]
    exit_code: int
    duration_ms: int
    output: str
    discovered: int | None = None
    passed: int | None = None
    failed: int | None = None
    skipped: int | None = None


_TEST_COUNTS_RE = re.compile(
    r"discovered=(\d+) passed=(\d+) failed=(\d+) skipped=(\d+)"
)


def _parse_test_counts(output: str) -> tuple[int, int, int, int] | None:
    """Parse the unified test-entry summary line (ENG-OPTIMIZE-1)."""

    match = _TEST_COUNTS_RE.search(output)
    if match is None:
        return None
    return tuple(int(group) for group in match.groups())


STAGE_TIMEOUTS = {
    "fmt": 600,
    "lint": 600,
    "test": 2400,
    "test-security": 1800,
    "test-e2e": 2400,
    "test-win7": 600,
    "fast": 1800,
    "quality": 2400,
}
GATE_RESULTS_DIR = ROOT / "loop" / "runtime" / "gate-results"


def _run_one(argv, timeout_sec):
    """Run one stage command and return a StageResult (no recording)."""

    started=time.monotonic()
    cwd=ROOT
    env=gate_env()
    if argv==GO_TEST_ARGV:
        cwd=ROOT/"go"
        env["GOPROXY"]="off"
    try:
        process=subprocess.run(
            argv, cwd=cwd, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout_sec,
        )
        combined=process.stdout+process.stderr
        counts=_parse_test_counts(combined)
        return StageResult(
            argv=tuple(argv),
            exit_code=process.returncode,
            duration_ms=int((time.monotonic()-started)*1000),
            output=combined,
            discovered=counts[0] if counts else None,
            passed=counts[1] if counts else None,
            failed=counts[2] if counts else None,
            skipped=counts[3] if counts else None,
        )
    except subprocess.TimeoutExpired as exc:
        return StageResult(
            argv=tuple(argv),
            exit_code=13,
            duration_ms=int((time.monotonic()-started)*1000),
            output=f"[gate] stage timed out after {timeout_sec}s ({exc})\n",
        )


def _run_stages(target, argvs, timeout_sec):
    """Phase A: run every stage; the gate performs no governance recording here."""

    results=[]; rc=0
    try:
        seal()
        if verify_seal()!="fully-sealed":
            raise RuntimeError("preflight audit seal is incomplete")
        results.append(StageResult(
            argv=("preflight",), exit_code=0, duration_ms=0,
            output="preflight audit seal: fully-sealed\n",
        ))
    except Exception as exc:  # noqa: BLE001 - preflight seal failure stops the gate
        rc=14
        results.append(StageResult(
            argv=("preflight",), exit_code=14, duration_ms=0,
            output="preflight audit seal failed: "+str(exc)+"\n",
        ))
    for index,argv in enumerate(argvs,1):
        if rc: break
        # Stages between the preflight seal and the final seal append gate
        # audit records (and some tests exercise the real chain), leaving an
        # unsealed tail. The e2e stage's fail-fast preflight (AVAIL-1)
        # requires a fully-sealed audit chain, so re-seal before every stage
        # to keep the invariant each stage observes (sealing is idempotent and
        # does not append records).
        try:
            seal()
            if verify_seal()!="fully-sealed":
                raise RuntimeError("stage audit seal is incomplete")
        except Exception as exc:  # noqa: BLE001 - seal failure must stop the gate
            rc=14
            results.append(StageResult(
                argv=argv, exit_code=14, duration_ms=0,
                output="stage audit seal failed: "+str(exc)+"\n",
            ))
            break
        result=_run_one(argv,timeout_sec)
        results.append(result)
        print(
            f"[gate] stage {index}/{len(argvs)}: exit={result.exit_code} "
            f"duration_ms={result.duration_ms}",
            flush=True,
        )
        if result.exit_code:
            # Bounded, documented retry: e2e crypto tests may hit transient
            # GmSSL helper launch contention (GCP-E-LAUNCH; see
            # src/coevo/crypto/gmssl_provider.py). Retry once and record it.
            if any("tests/e2e" in str(part) for part in argv) and "GCP-E-LAUNCH" in result.output:
                retried=_run_one(argv,timeout_sec)
                results.append(StageResult(
                    argv=tuple(argv)+("(retry)",),
                    exit_code=retried.exit_code,
                    duration_ms=retried.duration_ms,
                    output=(
                        "\n[gate] e2e failed with transient GCP-E-LAUNCH; "
                        "retried once (bounded)\n" + retried.output
                    ),
                    discovered=retried.discovered,
                    passed=retried.passed,
                    failed=retried.failed,
                    skipped=retried.skipped,
                ))
                result=retried
            rc=result.exit_code
            if rc: break
    return results,rc


def _write_results_json(target, fp, rc, results, ts, total_ms):
    """Phase A artifact: machine-readable gate results under loop/runtime/."""

    try:
        GATE_RESULTS_DIR.mkdir(parents=True,exist_ok=True)
        payload={
            "schema_version":"1.0",
            "target":target,
            "fingerprint":fp,
            "exit_code":rc,
            "ok":rc==0,
            "started_at":ts,
            "duration_ms":total_ms,
            "stages":[
                {
                    "argv":list(stage.argv),
                    "exit_code":stage.exit_code,
                    "duration_ms":stage.duration_ms,
                    "output_tail":stage.output[-2000:],
                    "discovered":stage.discovered,
                    "passed":stage.passed,
                    "failed":stage.failed,
                    "skipped":stage.skipped,
                }
                for stage in results
            ],
            "totals":{
                "discovered":sum(s.discovered or 0 for s in results),
                "passed":sum(s.passed or 0 for s in results),
                "failed":sum(s.failed or 0 for s in results),
                "skipped":sum(s.skipped or 0 for s in results),
            },
        }
        path=GATE_RESULTS_DIR/f"{target}-{ts.replace(':','-')}.json"
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        return str(path)
    except Exception as exc:  # noqa: BLE001 - artifact failure never takes the gate down
        return f"results artifact failed: {type(exc).__name__}: {exc}"


def _verification_body_from_json(results_json: Path) -> str:
    """Build the VERIFICATION section body from the Phase A results JSON."""

    payload = json.loads(results_json.read_text(encoding="utf-8"))
    parts: list[str] = []
    for stage in payload.get("stages", []):
        parts.append("$ " + " ".join(stage.get("argv") or []) + "\n")
        parts.append(stage.get("output_tail") or "")
        counts = [
            stage.get(key)
            for key in ("discovered", "passed", "failed", "skipped")
        ]
        if any(count is not None for count in counts):
            parts.append(
                f"[gate] counts: discovered={stage.get('discovered')} "
                f"passed={stage.get('passed')} failed={stage.get('failed')} "
                f"skipped={stage.get('skipped')}\n"
            )
    parts.append(
        f"[gate] totals: {json.dumps(payload.get('totals', {}), sort_keys=True)}\n"
    )
    return "".join(parts)


def _record_gate_result(
    target,
    fp,
    rc,
    output,
    ts,
    *,
    results_json: Path | None = None,
    verification: Path = VERIFICATION,
):
    """Phase B: audit append, final seal, VERIFICATION write and records trim.

    VERIFICATION is derived from the Phase A results JSON when available
    (artifact/record consistency, ENG-OPTIMIZE-2); in-memory output is the
    fail-open fallback.
    """

    tail: list[str] = []
    append_record({"ts":ts,"actor":"quality_gate","tool":"quality_gate","target":target,"fingerprint":fp,"exit_code":rc})
    if rc==0:
        try:
            seal()
            if verify_seal()!="fully-sealed":
                raise RuntimeError("final audit seal is incomplete")
            tail.append("audit seal: fully-sealed\n")
        except Exception as exc:  # noqa: BLE001 - seal failure must fail the gate
            rc=14
            tail.append("audit seal failed: "+str(exc)+"\n")
    if results_json is not None and Path(results_json).is_file():
        try:
            body = _verification_body_from_json(Path(results_json)) + "".join(tail)
        except Exception as exc:  # noqa: BLE001 - fall back to in-memory output
            body = "".join(output) + (
                f"\n[gate] results JSON read failed: "
                f"{type(exc).__name__}: {exc}\n"
            ) + "".join(tail)
    else:
        body = "".join(output) + "".join(tail)
    with verification.open("a",encoding="utf-8") as stream:
        stream.write(f"\n## {ts} — target=`{target}` fingerprint=`{fp}`\n- exit_code: `{rc}`\n```text\n{body[-8000:]}\n```\n")
    trim_note = _trim_records_to_policy(verification)
    if trim_note:
        with verification.open("a",encoding="utf-8") as stream:
            stream.write(f"\n[gate] records self-trim: {trim_note}\n")
    return rc
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--target",required=True,choices=[*TARGETS,"quality"])
    try:
        return run(parser.parse_args().target)
    except RuntimeError as exc:
        print(json.dumps({"ok":False,"exit_code":15,"error":str(exc)},ensure_ascii=True))
        return 15
if __name__=="__main__": raise SystemExit(main())
