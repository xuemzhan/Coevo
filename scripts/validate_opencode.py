"""Dependency-free, fail-closed validation for Coevo's engineering baseline."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("AGENTS.md", "opencode.jsonc", "Makefile", "docs/README.md", "loop/STATE.json",
 "loop/BACKLOG.yaml", "loop/VERIFICATION.md", "loop/tool-audit.jsonl", ".opencode/plugins/loop-guard.ts",
 ".opencode/tools/loop_state.ts", ".opencode/tools/quality_gate.ts", ".opencode/tools/traceability_check.ts",
 "tests/unit", "tests/integration", "tests/security", "tests/e2e")

def strip_jsonc(text):
    out=[]; i=0; quoted=False
    while i < len(text):
        c=text[i]
        if quoted:
            out.append(c)
            if c=="\\" and i+1<len(text): out.append(text[i+1]); i+=2; continue
            if c=='"': quoted=False
            i+=1; continue
        if c=='"': quoted=True; out.append(c); i+=1; continue
        if text[i:i+2]=="//":
            i=text.find("\n",i)
            if i<0: break
            continue
        if text[i:i+2]=="/*":
            end=text.find("*/",i+2)
            if end<0: raise ValueError("unterminated comment")
            i=end+2; continue
        out.append(c); i+=1
    return "".join(out)

def validate(require_tools=False):
    failures=[]
    def check(ok,msg):
        print(("PASS " if ok else "FAIL ")+msg)
        if not ok: failures.append(msg)
    for rel in REQUIRED:
        p=ROOT/rel; check(p.exists() and (p.is_dir() or p.stat().st_size>0), "required: "+rel)
    try:
        permission=json.loads(strip_jsonc((ROOT/"opencode.jsonc").read_text(encoding="utf-8")))["permission"]
        for name in ("webfetch","websearch","external_directory"): check(permission.get(name)=="deny", "denied: "+name)
        bash=permission["bash"]; check(bash.get("*")=="ask", "bash defaults to ask")
        for cmd in ("git push*","curl *","wget *","pip install*","npm install*"): check(bash.get(cmd)=="deny", "bash denied: "+cmd)
    except Exception as exc: check(False,"config parses: "+str(exc))
    for p in (ROOT/".opencode/tools").glob("*.ts"): check("export default tool(" in p.read_text(encoding="utf-8"), "current tool API: "+p.name)
    if require_tools:
        for name in ("git","opencode","make"): check(shutil.which(name) is not None,"tool available: "+name)
    return failures

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--require-tools",action="store_true")
    failures=validate(parser.parse_args().require_tools); print(json.dumps({"ok":not failures,"failures":failures},ensure_ascii=False))
    return 0 if not failures else 2
if __name__=="__main__": raise SystemExit(main())
