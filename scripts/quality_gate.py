"""Zero-download, fail-closed quality gate with a signed final audit seal."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, sys
from pathlib import Path
from audit_log import append_record
from audit_seal import seal, verify_seal
ROOT=Path(__file__).resolve().parents[1]; VERIFICATION=ROOT/"loop/VERIFICATION.md"
TARGETS={
 "fmt":[[sys.executable,"-m","compileall","-q","-f","scripts","src","tests"]],
 "lint":[[sys.executable,"scripts/validate_opencode.py"],[sys.executable,"scripts/traceability_check.py"],[sys.executable,"scripts/audit_log.py","verify"],[sys.executable,"scripts/audit_seal.py","verify","--allow-tail"]],
 "test":[[sys.executable,"-m","unittest","discover","-s","tests/unit","-v"],[sys.executable,"-m","unittest","discover","-s","tests/integration","-p","*test.py","-v"]],
 "test-security":[[sys.executable,"-m","unittest","discover","-s","tests/security","-v"],["node","tests/security/path_policy_test.mjs"]],
 "test-e2e":[[sys.executable,"-m","unittest","discover","-s","tests/e2e","-v"]]}
def commands(target): return [c for n in ("fmt","lint","test","test-security","test-e2e") for c in TARGETS[n]] if target=="quality" else TARGETS[target]
def fingerprint(argvs): return hashlib.sha256(json.dumps(argvs,separators=(",",":")).encode()).hexdigest()[:16]
def run(target):
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
        process=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace"); output.append("$ "+" ".join(argv)+"\n"+process.stdout+process.stderr)
        if process.returncode: rc=process.returncode; break
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
    parser=argparse.ArgumentParser(); parser.add_argument("--target",required=True,choices=[*TARGETS,"quality"]); return run(parser.parse_args().target)
if __name__=="__main__": raise SystemExit(main())
