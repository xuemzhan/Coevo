"""CI-2: build the offline Coevo toolchain artifact reproducibly.

Pure-stdlib builder that zips the locked runtime subset (python full
runtime + files lock, node, gmssl, control) under a ``.tools/`` root, the
layout expected by ``ci-restore-toolchain.ps1``. Prints the SHA-256 digest
to pin in ``docs/dependencies/ci-artifact.json``.

Usage:
    python scripts/ci-build-toolchain.py --version 1.0.0 [--out PATH] [--tools-root PATH]

Fail-closed: the output must not already exist (unless ``--force``), the
tools root must contain the expected runtime directories, and nothing is
downloaded.
"""
from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path
from typing import Final


REQUIRED_TOOLS: Final[tuple[str, ...]] = (
    "python/3.14.3/python.exe",
    "node/24.14.0/node.exe",
    "control/control.pyz",
)
INCLUDE_TOOLS: Final[tuple[str, ...]] = ("python", "node", "gmssl", "control")


def build_archive(tools_root: Path, out: Path, *, force: bool = False) -> str:
    tools_root = tools_root.resolve()
    out = out.resolve()
    for relative in REQUIRED_TOOLS:
        if not (tools_root / relative).is_file():
            raise SystemExit(
                f"tools root is missing required entry: {tools_root / relative}"
            )
    if out.exists() and not force:
        raise SystemExit(f"output already exists: {out} (use --force to overwrite)")
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for sub in INCLUDE_TOOLS:
            base = tools_root / sub
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*")):
                if path.is_dir():
                    continue
                relative = path.relative_to(tools_root).as_posix()
                if "__pycache__" in relative or relative.endswith(".pyc"):
                    continue
                zf.write(path, f".tools/{relative}")
                count += 1
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(
        "artifact ready: "
        f"path={out} size={out.stat().st_size} files={count} sha256={digest}"
    )
    return digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo toolchain artifact builder")
    parser.add_argument("--version", required=True, help="semantic artifact version")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--tools-root", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    tools_root = args.tools_root or Path(__file__).resolve().parents[1] / ".tools"
    out = args.out or Path.cwd() / f"coevo-toolchain-win64-{args.version}.zip"
    build_archive(tools_root, out, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
