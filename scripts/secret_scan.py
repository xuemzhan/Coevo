"""SECSCAN-1: scan tracked text files for high-confidence secret material.

The scanner looks for obvious secret forms that should never be committed:

* PEM private-key blocks (``-----BEGIN ... PRIVATE KEY-----``, including
  RSA / EC / DSA / OpenSSH / encrypted / SM2 variants, plus PGP
  ``-----BEGIN PGP PRIVATE KEY BLOCK-----``);
* AWS access key ids (``AKIA...``);
* GitHub token family (``ghp_``/``gho_``/``ghu_``/``ghs_``/``ghr_`` and
  fine-grained ``github_pat_...``);
* OpenAI-style keys (``sk-...``);
* Slack tokens (``xox[a|b|p|r|s]-...``);
* Google API keys (``AIza...``), npm access tokens (``npm_...``),
  Stripe live/test secret + restricted keys (``sk_live_``/``sk_test_``/
  ``rk_live_``) and SendGrid API keys (``SG.<id>.<key>``);
* high-entropy assignments to key-ish names
  (``api_key``/``secret``/``token``/``password = "<20+ chars>"``).

Allow-listing (kept deliberately narrow):

* ``tests/`` files may contain fake PEM blocks and fake key-like
  assignments (negative-test fixtures); token-style patterns
  (``AKIA``/``ghp_``/``sk-``/``xox``) still apply everywhere.
* ``loop/`` record files (VERIFICATION.md / DECISIONS.md / BACKLOG.yaml)
  legitimately quote gate output and test fixtures, so the same
  PEM / PGP / key-assignment fixture patterns are allowed there;
  token-style patterns still apply everywhere.
* the scanner skips its own source (it necessarily contains the pattern
  literals).

When the root is a git checkout, only tracked files are scanned (gitignored
material such as ``.tools/`` and ``loop/runtime/`` is excluded). A
non-git root (used by tests) is walked recursively.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Final


_TEXT_SUFFIXES: Final[frozenset[str]] = frozenset({
    ".py", ".md", ".json", ".ps1", ".cs", ".yaml", ".yml",
    ".js", ".ts", ".html", ".css", ".sql", ".txt", ".mjs", ".tsv",
})
_MAX_FILE_BYTES: Final[int] = 1 * 1024 * 1024
_TESTS_ALLOWED_PATTERNS: Final[frozenset[str]] = frozenset({
    "pem_private_key",
    "pgp_private_key",
    "key_assignment",
})
_FIXTURE_ALLOWED_PREFIXES: Final[tuple[str, ...]] = ("tests/", "loop/")
_SELF_SKIP: Final[frozenset[str]] = frozenset({"scripts/secret_scan.py"})

_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "pem_private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |SM2 )?PRIVATE KEY-----",
        re.IGNORECASE,
    ),
    "pgp_private_key": re.compile(
        r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
        re.IGNORECASE,
    ),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_pat": re.compile(
        r"\b(?:ghp_|gho_|ghu_|ghs_|ghr_|github_pat_)[A-Za-z0-9_]{22,}\b"
    ),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "npm_token": re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),
    "stripe_key": re.compile(
        r"\b(?:sk_live_|sk_test_|rk_live_)[0-9A-Za-z]{16,}\b"
    ),
    "sendgrid_key": re.compile(
        r"\bSG\.[A-Za-z0-9_-]{22,}\.[A-Za-z0-9_-]{20,}\b"
    ),
    "key_assignment": re.compile(
        r"(?:api[_-]?key|secret|token|password)\s*[:=]\s*"
        r"[\"'][A-Za-z0-9+/=_-]{20,}[\"']",
        re.IGNORECASE,
    ),
}


def tracked_files(root: Path) -> list[str]:
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError("git ls-files failed")
        return [
            item for item in result.stdout.decode("utf-8", errors="replace").split("\0")
            if item
        ]
    # Non-git root (tests): walk, skipping heavy/generated directories.
    found: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        parts = relative.split("/")
        if any(part in (".git", ".tools", "__pycache__", "loop") for part in parts[:2]):
            continue
        if path.suffix in _TEXT_SUFFIXES:
            found.append(relative)
    return found


def scan_file(root: Path, relative: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if relative in _SELF_SKIP:
        return findings
    path = root / relative
    try:
        if path.stat().st_size > _MAX_FILE_BYTES:
            return findings
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for name, pattern in _PATTERNS.items():
        if (
            name in _TESTS_ALLOWED_PATTERNS
            and relative.startswith(_FIXTURE_ALLOWED_PREFIXES)
        ):
            continue
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            snippet = match.group(0)
            findings.append(
                {
                    "path": relative,
                    "line": line,
                    "pattern": name,
                    "snippet": snippet if len(snippet) <= 40 else snippet[:37] + "...",
                }
            )
    return findings


def scan(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for relative in tracked_files(root):
        findings.extend(scan_file(root, relative))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo secret scan")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    findings = scan(root)
    if args.json:
        print(json.dumps({"ok": not findings, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print("secret scan ok")
        for item in findings:
            print(
                f"SECRET {item['pattern']}: {item['path']}:{item['line']} "
                f"({item['snippet']})"
            )
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
