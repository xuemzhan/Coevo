"""Offline Coevo MVP demo runner (CLI).

Usage:
    python scripts/run_demo.py --smoke                # headless end-to-end check
    python scripts/run_demo.py --runtime-dir <dir>    # run + cockpit server
    python scripts/run_demo.py --no-server            # run pipeline only
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.app import run_demo_pipeline  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Coevo MVP demo")
    parser.add_argument(
        "--runtime-dir",
        default=str(ROOT / "loop" / "runtime" / "demo"),
        help="parent directory for demo run artifacts",
    )
    parser.add_argument("--port", type=int, default=12751)
    parser.add_argument("--no-server", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(argv)

    result = run_demo_pipeline(
        Path(args.runtime_dir),
        with_cockpit=not args.no_server and not args.smoke,
        cockpit_port=args.port,
    )
    print("demo outcome:", result.outcome)
    print("package:", result.package_path)
    print("package sha256:", result.package_wire_sha256)
    print("knowledge bundle:", result.knowledge_bundle_id)
    print("audit events published:", result.audit_event_count)
    if result.cockpit_url:
        print("cockpit url:", result.cockpit_url)
    if args.smoke:
        if result.outcome != "completed" or result.package_path is None:
            print("DEMO FAILED", file=sys.stderr)
            return 1
        if not result.package_path.is_file():
            print("DEMO FAILED: package missing", file=sys.stderr)
            return 1
        print("DEMO OK")
        return 0
    if result.cockpit_url:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
