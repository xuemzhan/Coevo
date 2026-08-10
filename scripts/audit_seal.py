"""Create and verify a signed audit-log head without exposing private key material."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, shutil, subprocess, uuid
from pathlib import Path
from audit_log import DEFAULT_AUDIT, DEFAULT_CHECKPOINT, canonical as audit_canonical, exclusive_lock, verify as verify_chain

ROOT=Path(os.environ.get("COEVO_REPO_ROOT",Path(__file__).resolve().parents[1])); HEAD=ROOT/"loop/audit-head.json"; SIGNATURE=ROOT/"loop/audit-head.p7s"; CONFIG=ROOT/"loop/audit-signing.json"; SCRIPT=ROOT/"scripts/audit_signature.ps1"; JOURNAL=ROOT/"loop/audit-seal.transaction.json"
def canonical(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")+b"\n"
def powershell(action,head=HEAD,signature=SIGNATURE):
    executable=os.environ.get("COEVO_POWERSHELL_PATH")
    if not executable or not Path(executable).is_absolute():
        executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable or not Path(executable).is_absolute():
        fallback = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        if fallback.is_file(): executable = str(fallback)
    if not executable or not Path(executable).is_absolute(): raise RuntimeError("locked Windows PowerShell path is unavailable")
    result=subprocess.run([executable,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(SCRIPT),"-Action",action,"-HeadPath",str(head),"-SignaturePath",str(signature),"-ConfigPath",str(CONFIG)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
    if result.returncode: raise RuntimeError((result.stderr or result.stdout).strip())
def signed_head(head=HEAD,signature=SIGNATURE): powershell("Verify",head,signature); return json.loads(head.read_text(encoding="utf-8"))
def verify_seal(audit=DEFAULT_AUDIT,head=HEAD,signature=SIGNATURE):
    problems=verify_chain(audit,DEFAULT_CHECKPOINT)
    if problems: raise ValueError("audit chain invalid: "+"; ".join(problems))
    sealed=signed_head(head,signature); raw=audit.read_bytes(); byte_count=sealed["audit_byte_count"]
    if len(raw)<byte_count: raise ValueError("audit tail deletion detected")
    prefix=raw[:byte_count]
    if hashlib.sha256(prefix).hexdigest()!=sealed["audit_sha256"]: raise ValueError("signed audit prefix mismatch")
    if len(prefix.splitlines())!=sealed["audit_line_count"]: raise ValueError("signed audit line count mismatch")
    return "fully-sealed" if len(raw)==byte_count else "valid-prefix-with-unsealed-tail"
def recover():
    if not JOURNAL.exists(): return
    tx=json.loads(JOURNAL.read_text(encoding="utf-8")); head_bak=Path(tx["head_backup"]); sig_bak=Path(tx["signature_backup"])
    try: verify_seal()
    except Exception:
        if head_bak.exists() and sig_bak.exists(): shutil.copyfile(head_bak,HEAD); shutil.copyfile(sig_bak,SIGNATURE)
        else: HEAD.unlink(missing_ok=True); SIGNATURE.unlink(missing_ok=True)
    for path in (head_bak,sig_bak,Path(tx["head_pending"]),Path(tx["signature_pending"])): path.unlink(missing_ok=True)
    JOURNAL.unlink(missing_ok=True)
def seal(audit=DEFAULT_AUDIT):
    with exclusive_lock(audit.with_suffix(".lock")):
        recover(); problems=verify_chain(audit,DEFAULT_CHECKPOINT)
        if problems: raise ValueError("audit chain invalid: "+"; ".join(problems))
        raw=audit.read_bytes(); lines=raw.splitlines(); config=json.loads(CONFIG.read_text(encoding="utf-8")); sequence=1
        if HEAD.exists() and SIGNATURE.exists(): sequence=int(signed_head().get("sequence",0))+1
        checkpoint=json.loads(DEFAULT_CHECKPOINT.read_text(encoding="utf-8"))
        item={"schema_version":"1.0","generation_id":str(uuid.uuid4()),"sequence":sequence,"audit_path":"loop/tool-audit.jsonl","audit_byte_count":len(raw),"audit_line_count":len(lines),"audit_sha256":hashlib.sha256(raw).hexdigest(),"tail_line_sha256":hashlib.sha256(lines[-1]).hexdigest() if lines else None,"tail_record_hash":json.loads(lines[-1]).get("record_hash") if lines else None,"legacy_checkpoint_hash":checkpoint["checkpoint_hash"],"signer_thumbprint":config["thumbprint"],"signature_algorithm":config["signature_algorithm"],"digest_algorithm":config["digest_algorithm"],"signed_at":dt.datetime.now(dt.UTC).isoformat().replace("+00:00","Z")}
        head_pending=HEAD.with_suffix(".json.pending"); sig_pending=SIGNATURE.with_suffix(".p7s.pending"); head_bak=HEAD.with_suffix(".json.bak"); sig_bak=SIGNATURE.with_suffix(".p7s.bak")
        if HEAD.exists(): shutil.copyfile(HEAD,head_bak)
        if SIGNATURE.exists(): shutil.copyfile(SIGNATURE,sig_bak)
        tx={"head_backup":str(head_bak),"signature_backup":str(sig_bak),"head_pending":str(head_pending),"signature_pending":str(sig_pending)}
        JOURNAL.write_text(json.dumps(tx,indent=2)+"\n",encoding="utf-8"); head_pending.write_bytes(canonical(item)); powershell("Sign",head_pending,sig_pending); powershell("Verify",head_pending,sig_pending)
        os.replace(head_pending,HEAD); os.replace(sig_pending,SIGNATURE)
        if verify_seal(audit)!="fully-sealed": raise RuntimeError("new audit seal does not cover the complete log")
        for path in (head_bak,sig_bak): path.unlink(missing_ok=True)
        JOURNAL.unlink(missing_ok=True); return item


def reanchor_plan(
    raw_lines: list[bytes],
    *,
    previous_head_sequence: int | None,
    now: str,
) -> dict[str, object]:
    """Plan an audit-generation re-anchor (REVIEW2-10).

    The whole current generation is archived (bytes preserved), a genesis
    record anchors the new generation to the archived digest, and the
    legacy checkpoint is reset to the genesis line. No existing record is
    rewritten -- append-only integrity is preserved within each generation.
    """

    lines = [line for line in raw_lines if line.strip()]
    if len(lines) < 2:
        raise ValueError(
            "audit log has fewer than 2 lines; nothing to re-anchor"
        )
    archived_bytes = b"".join(lines)
    genesis = {
        "schema_version": "1.0",
        "ts": now,
        "actor": "audit_seal",
        "tool": "audit_seal",
        "event": "audit_generation",
        "generation_id": str(uuid.uuid4()),
        "previous_generation_sha256": hashlib.sha256(
            archived_bytes
        ).hexdigest(),
        "previous_generation_line_count": len(lines),
        "previous_head_sequence": previous_head_sequence,
        "prev_hash": "0" * 64,
        "result": "reanchored",
    }
    genesis_item = dict(genesis)
    genesis_item["record_hash"] = hashlib.sha256(
        audit_canonical(genesis_item)
    ).hexdigest()
    genesis_raw = (
        json.dumps(genesis_item, ensure_ascii=False, sort_keys=True).encode(
            "utf-8"
        )
        + b"\n"
    )
    checkpoint_item = {
        "schema_version": "1.0",
        "algorithm": "sha256",
        "legacy_line_count": 0,
        "legacy_byte_count": 0,
        "legacy_sha256": hashlib.sha256(b"").hexdigest(),
        "first_chained_line": 1,
    }
    checkpoint_item["checkpoint_hash"] = hashlib.sha256(
        audit_canonical(checkpoint_item)
    ).hexdigest()
    return {
        "archived_bytes": archived_bytes,
        "archived_sha256": hashlib.sha256(archived_bytes).hexdigest(),
        "archived_line_count": len(lines),
        "genesis_item": genesis_item,
        "genesis_raw": genesis_raw,
        "checkpoint_item": checkpoint_item,
        "checkpoint_rendered": (
            json.dumps(checkpoint_item, ensure_ascii=False, indent=2) + "\n"
        ),
    }


def reanchor(
    *,
    audit: Path = DEFAULT_AUDIT,
    head: Path = HEAD,
    signature: Path = SIGNATURE,
    checkpoint: Path = DEFAULT_CHECKPOINT,
    archive_dir: Path | None = None,
) -> dict[str, object]:
    """Re-anchor the audit log to a new generation (REVIEW2-10).

    Fail-closed: the current chain must be fully sealed before anything is
    touched; the old generation is archived first; the new genesis +
    checkpoint are written atomically; the head is then re-sealed. If the
    seal fails, the archived bytes are restored.
    """

    with exclusive_lock(audit.with_suffix(".lock")):
        recover()
        if verify_seal(audit, head, signature) != "fully-sealed":
            raise ValueError(
                "re-anchor requires a fully-sealed audit chain"
            )
        raw = audit.read_bytes()
        old_lines = raw.splitlines(keepends=True)
        old_checkpoint = (
            checkpoint.read_bytes() if checkpoint.exists() else b""
        )
        now = dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")
        old_sequence = None
        if head.exists():
            old_sequence = json.loads(head.read_text(encoding="utf-8")).get(
                "sequence"
            )
        plan = reanchor_plan(old_lines, previous_head_sequence=old_sequence, now=now)
        date_stamp = now[:10].replace("-", "")
        target_dir = archive_dir or (ROOT / "loop" / "archive" / date_stamp)
        target_dir.mkdir(parents=True, exist_ok=True)
        archive_path = target_dir / (
            f"audit-generation-{old_sequence or 0}-{now.replace(':','-')}.jsonl"
        )
        archive_path.write_bytes(plan["archived_bytes"])  # type: ignore[arg-type]
        audit_tmp = audit.with_suffix(".jsonl.tmp")
        checkpoint_tmp = checkpoint.with_suffix(".json.tmp")
        try:
            audit_tmp.write_bytes(plan["genesis_raw"])  # type: ignore[arg-type]
            os.replace(audit_tmp, audit)
            checkpoint_tmp.write_text(
                plan["checkpoint_rendered"], encoding="utf-8"  # type: ignore[arg-type]
            )
            os.replace(checkpoint_tmp, checkpoint)
            seal(audit)
        except Exception:
            audit.write_bytes(raw)
            if old_checkpoint:
                checkpoint.write_bytes(old_checkpoint)
            elif checkpoint.exists():
                checkpoint.unlink(missing_ok=True)
            raise
        return {
            "ok": True,
            "previous_head_sequence": old_sequence,
            "archived_path": str(archive_path),
            "archived_sha256": plan["archived_sha256"],
            "archived_line_count": plan["archived_line_count"],
            "generation_id": plan["genesis_item"]["generation_id"],  # type: ignore[index]
            "new_head_sequence": json.loads(head.read_text(encoding="utf-8")).get(
                "sequence"
            ),
        }
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("action",choices=["sign","verify","re-anchor"]); parser.add_argument("--allow-tail",action="store_true"); parser.add_argument("--archive-dir",type=Path); args=parser.parse_args()
    try:
        if args.action=="sign":
            result=seal()
            print(json.dumps({"ok":True,"status":"fully-sealed","sequence":result.get("sequence")},ensure_ascii=False)); return 0
        if args.action=="re-anchor":
            print(json.dumps(reanchor(archive_dir=args.archive_dir),ensure_ascii=False)); return 0
        result=verify_seal()
        if result=="valid-prefix-with-unsealed-tail" and not args.allow_tail: raise ValueError("audit has an unsealed tail")
        print(json.dumps({"ok":True,"status":result},ensure_ascii=False)); return 0
    except Exception as exc: print(json.dumps({"ok":False,"error":str(exc)},ensure_ascii=True)); return 14
if __name__=="__main__": raise SystemExit(main())
