"""Validate every code/test path for active traceability rows."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; MATRIX=ROOT/"docs/traceability/requirements-test-matrix.md"
ACTIVE={"in-progress","done"}
def paths(cell): return re.findall(r"`([^`]+)`",cell.replace("<br>",";"))
def safe_path(value):
    candidate=Path(value)
    if candidate.is_absolute() or ".." in candidate.parts: raise ValueError("unsafe traceability path: "+value)
    resolved=(ROOT/candidate).resolve()
    if ROOT.resolve() not in (resolved,*resolved.parents): raise ValueError("traceability path escapes root: "+value)
    return resolved
def parse(text):
    rows=[]
    for raw in text.splitlines():
        if not raw.startswith("|"): continue
        cells=[cell.strip() for cell in raw.strip("|").split("|")]
        if len(cells)<8 or cells[0] in {"故事","---"} or set(cells[0])<={"-"," "}: continue
        rows.append({"story":cells[0],"ac":cells[1],"title":cells[2],"code":paths(cells[3]),"tests":paths(cells[4]),"status":cells[6]})
    return rows
def check(story=None,active_only=True):
    result=[]; missing=0
    for row in parse(MATRIX.read_text(encoding="utf-8")):
        if story and row["story"]!=story: continue
        if active_only and row["status"] not in ACTIVE: continue
        evidence=[]
        for kind,values in (("code",row["code"]),("test",row["tests"])):
            if not values: evidence.append({"kind":kind,"path":None,"exists":False}); missing+=1
            for value in values:
                try: exists=safe_path(value).exists()
                except ValueError: exists=False
                evidence.append({"kind":kind,"path":value,"exists":exists})
                if not exists: missing+=1
        result.append({**row,"evidence":evidence,"kind":"covered" if all(x["exists"] for x in evidence) else "missing"})
    return {"checked":len(result),"missing":missing,"items":result}
def main(argv=None):
    parser=argparse.ArgumentParser(); parser.add_argument("--story"); parser.add_argument("--all-statuses",action="store_true"); args=parser.parse_args(argv)
    summary=check(args.story,not args.all_statuses); print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0 if summary["checked"] and not summary["missing"] else 10
if __name__=="__main__": raise SystemExit(main())
