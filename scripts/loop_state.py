"""Transactional loop state updater using a write-ahead journal and recovery."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, sys, uuid
from pathlib import Path
from audit_log import append_record, exclusive_lock

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/"loop/STATE.json"; AUDIT=ROOT/"loop/tool-audit.jsonl"; JOURNAL=ROOT/"loop/STATE.transaction.json"; LOCK=ROOT/"loop/STATE.lock"
ALLOWED={"phase","status","current_story","current_item","failed_verifications","last_failure_fingerprint","last_verified_commit","blocking_issue"}
PHASES={"ready","discover","plan","implement","verify","review","record","decide"}
STATUSES={"ready","in-progress","blocked","security-blocked","decision-required","done","mvp-complete"}

def now(): return dt.datetime.now(dt.UTC).isoformat().replace("+00:00","Z")
def digest(value): return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def write_json_atomic(path,value):
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("w",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    os.replace(tmp,path)

class StateStore:
    def __init__(self,state=STATE,audit=AUDIT,journal=JOURNAL,lock=LOCK,append_fn=append_record):
        self.state=Path(state); self.audit=Path(audit); self.journal=Path(journal); self.lock=Path(lock); self.append=append_fn
    def _events(self,tx):
        found=set()
        if self.audit.exists():
            for raw in self.audit.read_text(encoding="utf-8").splitlines():
                try: item=json.loads(raw)
                except json.JSONDecodeError: continue
                if item.get("transaction_id")==tx: found.add(item.get("event"))
        return found
    def _recover_locked(self):
        if not self.journal.exists(): return
        tx=json.loads(self.journal.read_text(encoding="utf-8")); current=json.loads(self.state.read_text(encoding="utf-8")); events=self._events(tx["transaction_id"])
        current_hash=digest(current)
        if current_hash==tx["new_hash"]:
            if "committed" not in events: self.append({"ts":now(),"actor":"loop_state","tool":"loop_state","transaction_id":tx["transaction_id"],"event":"committed","result":"recovered"},self.audit)
        elif current_hash==tx["old_hash"]:
            if "prepared" in events and "aborted" not in events: self.append({"ts":now(),"actor":"loop_state","tool":"loop_state","transaction_id":tx["transaction_id"],"event":"aborted","result":"recovered"},self.audit)
        else: raise RuntimeError("state does not match either side of pending transaction")
        self.journal.unlink()
    def update(self,fields):
        unknown=set(fields)-ALLOWED
        if unknown: raise ValueError("unsupported state fields: "+", ".join(sorted(unknown)))
        if "phase" in fields and fields["phase"] not in PHASES: raise ValueError("invalid phase")
        if "status" in fields and fields["status"] not in STATUSES: raise ValueError("invalid status")
        if "failed_verifications" in fields and (type(fields["failed_verifications"]) is not int or fields["failed_verifications"]<0): raise ValueError("invalid failed_verifications")
        with exclusive_lock(self.lock):
            self._recover_locked()
            old=json.loads(self.state.read_text(encoding="utf-8")); new={**old,**fields,"updated_at":now()}
            if new.get("failed_verifications",0)>=3: new["status"]="blocked"; new["blocking_issue"]="same verification failure reached threshold"
            txid=str(uuid.uuid4()); tx={"schema_version":"1.0","transaction_id":txid,"old_hash":digest(old),"new_hash":digest(new),"old_state":old,"new_state":new}
            write_json_atomic(self.journal,tx)
            self.append({"ts":now(),"actor":"loop_state","tool":"loop_state","transaction_id":txid,"event":"prepared","fields":fields,"old_hash":tx["old_hash"],"new_hash":tx["new_hash"],"result":"ok"},self.audit)
            write_json_atomic(self.state,new)
            self.append({"ts":now(),"actor":"loop_state","tool":"loop_state","transaction_id":txid,"event":"committed","new_hash":tx["new_hash"],"result":"ok"},self.audit)
            self.journal.unlink(); return new

def main():
    parser=argparse.ArgumentParser(); source=parser.add_mutually_exclusive_group(required=True); source.add_argument("--args-file"); source.add_argument("--stdin",action="store_true")
    args=parser.parse_args(); raw=sys.stdin.read() if args.stdin else Path(args.args_file).read_text(encoding="utf-8")
    try:
        fields=json.loads(raw)
        if not isinstance(fields,dict): raise ValueError("payload must be a JSON object")
        print(json.dumps(StateStore().update(fields),ensure_ascii=False)); return 0
    except (ValueError,json.JSONDecodeError,RuntimeError) as exc: print(str(exc),file=sys.stderr); return 30
if __name__=="__main__": raise SystemExit(main())
