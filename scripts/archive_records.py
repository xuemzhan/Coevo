"""Archive old loop records (dry-run by default).

Usage:
    python scripts/archive_records.py --dry-run   # show the plan
    python scripts/archive_records.py --check     # gate: fail if any record needs archiving
    python scripts/archive_records.py --apply     # write archives + trim tails
"""
from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.records_archive import (  # noqa: E402
    ARCHIVABLE_KINDS,
    POLICY,
    archivable,
    archive_plan,
    over_policy_size,
    record_preamble,
)


FILES = {
    "verification": ROOT / "loop" / "VERIFICATION.md",
    "decisions": ROOT / "loop" / "DECISIONS.md",
    "audit": ROOT / "loop" / "tool-audit.jsonl",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive old loop records")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    check = bool(args.check)
    apply = bool(args.apply)
    if check and apply:
        print("--check and --apply are mutually exclusive", file=sys.stderr)
        return 2
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    date_stamp = now[:10].replace("-", "")
    archive_dir = ROOT / "loop" / "archive" / date_stamp
    pending: list[str] = []

    # Audit-chain guard (RECORDS-ARCHIVE-3): tool-audit.jsonl is append-only
    # and seal-protected. Trimming it would break the signed audit head
    # (audit tail deletion) and there is no re-anchor flow yet, so the tool
    # reports the condition but refuses to touch it.
    audit_path = FILES["audit"]
    if audit_path.is_file():
        audit_over = over_policy_size(
            "audit", audit_path.read_text(encoding="utf-8", errors="replace")
        )
        if audit_over:
            print(
                "[audit] over archiving policy but NOT actionable via this tool: "
                "audit archival requires a dedicated re-anchor flow (not "
                "implemented); refusing to touch loop/tool-audit.jsonl"
            )
            if apply:
                print(
                    "apply refused: the audit chain must remain append-only",
                    file=sys.stderr,
                )
                return 3

    for kind in ARCHIVABLE_KINDS:
        assert archivable(kind), f"{kind} must stay outside the archive tool"
        path = FILES[kind]
        if not path.is_file():
            print(f"[skip] {kind}: missing {path}")
            if check:
                pending.append(f"{kind}: missing {path}")
            continue
        text = path.read_text(encoding="utf-8")
        plan = archive_plan(
            text,
            kind=kind,
            now=now,
            keep_recent=POLICY[kind]["keep_recent"],
            min_age_days=POLICY[kind]["min_age_days"],
            size_threshold_bytes=POLICY[kind]["size"],
            size_bytes=path.stat().st_size,
        )
        if not plan["archive"]:
            print(f"[ok] {kind}: nothing to archive")
            continue
        reason = (
            f"[{kind}] archive {plan['archived_sections']} section(s): "
            f"{plan['reason']}"
        )
        print(
            reason,
        )
        if check:
            pending.append(reason)
            continue
        if apply:
            archive_dir.mkdir(parents=True, exist_ok=True)
            target = archive_dir / f"{kind}-{date_stamp}.txt"
            with target.open("a", encoding="utf-8") as stream:
                stream.write(plan["archive"] + "\n")
            # Preserve the record-file preamble (e.g. DECISIONS title) so a
            # rewrite never drops the header (RECORDS-HYGIENE-1).
            path.write_text(record_preamble(text) + plan["keep"] + "\n", encoding="utf-8")
            print(f"  -> wrote {target}")
    if check:
        if pending:
            print(f"check failed: {len(pending)} record file(s) need archiving")
            return 1
        print("check ok: all record files within archiving policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
