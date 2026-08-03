"""Append-only audit helpers and legacy-prefix checkpoint verification."""
from __future__ import annotations
import contextlib, hashlib, json, os
from pathlib import Path

ROOT=Path(os.environ.get("COEVO_REPO_ROOT",Path(__file__).resolve().parents[1]))
DEFAULT_AUDIT=ROOT/"loop/tool-audit.jsonl"
DEFAULT_CHECKPOINT=ROOT/"loop/audit-checkpoint.json"

@contextlib.contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0,os.SEEK_END)
        if stream.tell()==0: stream.write(b"0"); stream.flush()
        stream.seek(0)
        if os.name=="nt":
            import msvcrt; msvcrt.locking(stream.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl; fcntl.flock(stream.fileno(),fcntl.LOCK_EX)
        try: yield
        finally:
            stream.seek(0)
            if os.name=="nt": msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else: fcntl.flock(stream.fileno(),fcntl.LOCK_UN)

def canonical(entry: dict) -> bytes:
    return json.dumps(entry,sort_keys=True,separators=(",",":")).encode("utf-8")

def append_record(entry: dict,audit_path: Path=DEFAULT_AUDIT) -> dict:
    with exclusive_lock(audit_path.with_suffix(".lock")):
        lines=audit_path.read_bytes().splitlines() if audit_path.exists() else []
        item=dict(entry); item["prev_hash"]=hashlib.sha256(lines[-1]).hexdigest() if lines else "0"*64
        item["record_hash"]=hashlib.sha256(canonical(item)).hexdigest()
        raw=json.dumps(item,ensure_ascii=False,sort_keys=True).encode("utf-8")+b"\n"
        with audit_path.open("ab") as stream: stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        return item

def create_legacy_checkpoint(audit_path: Path=DEFAULT_AUDIT,checkpoint_path: Path=DEFAULT_CHECKPOINT) -> dict:
    raw=audit_path.read_bytes(); lines=raw.splitlines(keepends=True)
    first_chained=next((i for i,line in enumerate(lines) if "record_hash" in json.loads(line)),len(lines))
    prefix=b"".join(lines[:first_chained])
    item={"schema_version":"1.0","algorithm":"sha256","legacy_line_count":first_chained,
          "legacy_byte_count":len(prefix),"legacy_sha256":hashlib.sha256(prefix).hexdigest(),
          "first_chained_line":first_chained+1}
    item["checkpoint_hash"]=hashlib.sha256(canonical(item)).hexdigest()
    rendered=json.dumps(item,ensure_ascii=False,indent=2)+"\n"
    if checkpoint_path.exists():
        existing=json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if existing!=item: raise ValueError("existing audit checkpoint does not match legacy prefix")
        return existing
    tmp=checkpoint_path.with_suffix(".json.tmp"); tmp.write_text(rendered,encoding="utf-8")
    with tmp.open("r+b") as stream: os.fsync(stream.fileno())
    os.replace(tmp,checkpoint_path)
    append_record({"actor":"audit_migration","tool":"audit_checkpoint","result":"ok","checkpoint_hash":item["checkpoint_hash"]},audit_path)
    return item

def verify(audit_path: Path=DEFAULT_AUDIT,checkpoint_path: Path=DEFAULT_CHECKPOINT) -> list[str]:
    errors=[]
    try: checkpoint=json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except Exception as exc: return [f"checkpoint unreadable: {exc}"]
    expected=dict(checkpoint); supplied=expected.pop("checkpoint_hash",None)
    if hashlib.sha256(canonical(expected)).hexdigest()!=supplied: errors.append("checkpoint hash mismatch")
    raw=audit_path.read_bytes()
    if raw and not raw.endswith(b"\n"): errors.append("audit has a truncated final line")
    keep=raw.splitlines(keepends=True); plain=raw.splitlines(); count=checkpoint.get("legacy_line_count",0)
    prefix=b"".join(keep[:count])
    if len(prefix)!=checkpoint.get("legacy_byte_count") or hashlib.sha256(prefix).hexdigest()!=checkpoint.get("legacy_sha256"): errors.append("legacy prefix mismatch")
    transactions=set()
    for index,line in enumerate(plain[count:],start=count):
        try: item=json.loads(line)
        except Exception as exc: errors.append(f"line {index+1} invalid JSON: {exc}"); continue
        record_hash=item.pop("record_hash",None); prev_hash=item.get("prev_hash")
        if record_hash!=hashlib.sha256(canonical(item)).hexdigest(): errors.append(f"line {index+1} record hash mismatch")
        expected_prev=hashlib.sha256(plain[index-1]).hexdigest() if index else "0"*64
        if prev_hash!=expected_prev: errors.append(f"line {index+1} previous hash mismatch")
        tx=item.get("transaction_id")
        marker=(tx,item.get("event"))
        if tx and marker in transactions: errors.append(f"line {index+1} duplicate transaction event")
        transactions.add(marker)
    return errors

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument("action",choices=["checkpoint","verify"]); args=parser.parse_args()
    if args.action=="checkpoint": print(json.dumps(create_legacy_checkpoint(),ensure_ascii=False))
    else:
        problems=verify(); print(json.dumps({"ok":not problems,"errors":problems},ensure_ascii=False)); raise SystemExit(0 if not problems else 12)
