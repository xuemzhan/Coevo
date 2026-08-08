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
import argparse, datetime as dt, hashlib, json, os, subprocess, sys
from pathlib import Path
from audit_log import append_record, exclusive_lock
from audit_seal import seal, verify_seal
ROOT=Path(os.environ.get("COEVO_REPO_ROOT",Path(__file__).resolve().parents[1])); VERIFICATION=ROOT/"loop/VERIFICATION.md"; os.environ.setdefault("COEVO_REPO_ROOT",str(ROOT))
GATE_LOCK=ROOT/"loop/.quality-gate.lock"
CONTROL=os.environ.get("COEVO_CONTROL_ARCHIVE",str(ROOT/".tools"/"control"/"control.pyz"))
CHILD_TIMEOUT_SECS=2400
def control(module,*args): return [sys.executable,CONTROL,module,*args]
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
    lock=json.loads((ROOT/"docs"/"dependencies"/"toolchain-lock.json").read_text(encoding="utf-8"))
    go_tool=lock["tools"]["go"]["executable"]["path"]
    return [go_tool,"test","./..."]
TARGETS={
 "fmt":[[sys.executable,"-m","compileall","-q","-f","scripts","src","tests"]],
 "lint":[[sys.executable,str(ROOT/"scripts"/"validate_opencode.py")],control("traceability_check"),control("audit_log","verify"),[sys.executable,str(ROOT/"scripts"/"audit_seal.py"),"verify","--allow-tail"],[sys.executable,str(ROOT/"scripts"/"archive_records.py"),"--check"],[sys.executable,str(ROOT/"scripts"/"secret_scan.py")]],
 "test":[[sys.executable,"-m","unittest","discover","-s","tests/unit","-v"],[sys.executable,"-m","unittest","discover","-s","tests/integration","-p","*test*.py","-v"],go_test_argv()],
 "test-security":[[sys.executable,"-m","unittest","discover","-s","tests/security","-v"],[os.environ.get("COEVO_NODE_PATH",str(ROOT/".tools"/"node"/"24.14.0"/"node.exe")),"tests/security/path_policy_test.mjs"]],
 "test-e2e":[[sys.executable,"-m","unittest","discover","-s","tests/e2e","-v"]]}
GO_TEST_ARGV=TARGETS["test"][-1]
def commands(target): return [c for n in ("fmt","lint","test","test-security","test-e2e") for c in TARGETS[n]] if target=="quality" else TARGETS[target]
def fingerprint(argvs): return hashlib.sha256(json.dumps(argvs,separators=(",",":")).encode()).hexdigest()[:16]
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
    argvs=commands(target); fp=fingerprint(argvs); output=[]; rc=0
    try:
        seal()
        if verify_seal()!="fully-sealed": raise RuntimeError("preflight audit seal is incomplete")
        output.append("preflight audit seal: fully-sealed\n")
    except Exception as exc:
        rc=14
        output.append("preflight audit seal failed: "+str(exc)+"\n")
    for argv in argvs:
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
            output.append("stage audit seal failed: "+str(exc)+"\n")
            break
        cwd=ROOT
        env=gate_env()
        if argv==GO_TEST_ARGV:
            cwd=ROOT/"go"
            env["GOPROXY"]="off"
        try:
            process=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=CHILD_TIMEOUT_SECS)
        except subprocess.TimeoutExpired as exc:
            rc=13
            output.append("$ "+" ".join(argv)+"\n[gate] stage timed out after "
                          f"{CHILD_TIMEOUT_SECS}s ({exc})\n")
            break
        combined=process.stdout+process.stderr
        output.append("$ "+" ".join(argv)+"\n"+combined)
        if process.returncode:
            # Bounded, documented retry: e2e crypto tests may hit transient
            # GmSSL helper launch contention (GCP-E-LAUNCH; see
            # src/coevo/crypto/gmssl_provider.py). Retry once and record it.
            if any("tests/e2e" in str(part) for part in argv) and "GCP-E-LAUNCH" in combined:
                try:
                    retried=subprocess.run(argv,cwd=ROOT,env=gate_env(),capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=CHILD_TIMEOUT_SECS)
                except subprocess.TimeoutExpired as exc:
                    rc=13
                    output.append("\n[gate] e2e retry timed out after "
                                  f"{CHILD_TIMEOUT_SECS}s ({exc})\n")
                    break
                output.append("\n[gate] e2e failed with transient GCP-E-LAUNCH; retried once (bounded)\n$ "+" ".join(argv)+"\n"+retried.stdout+retried.stderr)
                process=retried
            rc=process.returncode
            if rc: break
    ts=dt.datetime.now(dt.UTC).isoformat().replace("+00:00","Z"); append_record({"ts":ts,"actor":"quality_gate","tool":"quality_gate","target":target,"fingerprint":fp,"exit_code":rc})
    if rc==0:
        try:
            seal()
            if verify_seal()!="fully-sealed": raise RuntimeError("final audit seal is incomplete")
            output.append("audit seal: fully-sealed\n")
        except Exception as exc: rc=14; output.append("audit seal failed: "+str(exc)+"\n")
    with VERIFICATION.open("a",encoding="utf-8") as stream: stream.write(f"\n## {ts} — target=`{target}` fingerprint=`{fp}`\n- exit_code: `{rc}`\n```text\n{''.join(output)[-8000:]}\n```\n")
    print(json.dumps({"ok":rc==0,"exit_code":rc,"fingerprint":fp})); return rc
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--target",required=True,choices=[*TARGETS,"quality"])
    try:
        return run(parser.parse_args().target)
    except RuntimeError as exc:
        print(json.dumps({"ok":False,"exit_code":15,"error":str(exc)},ensure_ascii=True))
        return 15
if __name__=="__main__": raise SystemExit(main())
