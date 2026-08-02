"""Archive old loop records (dry-run by default).

Usage:
    python scripts/archive_records.py --dry-run   # show the plan
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

from src.coevo.records_archive import archive_plan  # noqa: E402


POLICY = {
    "verification": {"keep_recent": 60, "min_age_days": 30, "size": 1_000_000},
    "decisions": {"keep_recent": 20, "min_age_days": 90, "size": 500_000},
    "audit": {"keep_recent": 2000, "min_age_days": 30, "size": 5_000_000},
}
FILES = {
    "verification": ROOT / "loop" / "VERIFICATION.md",
    "decisions": ROOT / "loop" / "DECISIONS.md",
    "audit": ROOT / "loop" / "tool-audit.jsonl",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Archive old loop records")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    apply = bool(args.apply)
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    date_stamp = now[:10].replace("-", "")
    archive_dir = ROOT / "loop" / "archive" / date_stamp

    for kind, path in FILES.items():
        if not path.is_file():
            print(f"[skip] {kind}: missing {path}")
            continue
        text = path.read_text(encoding="utf-8")
        plan = archive_plan(
            text,
            kind=kind,
            now=now,
            keep_recent=POLICY[kind]["keep_recent"],
            min_age_days=POLICY[kind]["min_age_days"],
            size_threshold_bytes=POLICY[kind]["size"],
        )
        if not plan["archive"]:
            print(f"[ok] {kind}: nothing to archive")
            continue
        print(
            f"[{kind}] archive {plan['archived_sections']} section(s): "
            f"{plan['reason']}"
        )
        if apply:
            archive_dir.mkdir(parents=True, exist_ok=True)
            target = archive_dir / f"{kind}-{date_stamp}.txt"
            with target.open("w", encoding="utf-8") as stream:
                stream.write(plan["archive"] + "\n")
            path.write_text(plan["keep"] + "\n", encoding="utf-8")
            print(f"  -> wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
