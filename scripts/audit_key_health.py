"""Audit-signing key health diagnostics (P0-3 / AUDIT-KEY-1).

The audit chain is anchored by a pinned, non-exportable CodeSigning
certificate in ``CurrentUser/My`` plus a public certificate file and a
per-signer configuration archive (``loop/audit-signing-<thumbprint>.json``
for historical signers). Losing that key is a single point of failure for
the whole gate (historical precedent: the F713 key-loss incident that
made ``preflight`` exit 14). This tool gives operators a structured,
actionable health check before/after any gate run.

Checks (all fail-closed):

1. configuration exists and is structurally valid;
2. pinned public certificate file exists and its SHA-256 matches config;
3. the pinned certificate is present in ``CurrentUser/My``, has a private
   key, is non-exportable and within its validity window (delegated to
   ``audit_signature.ps1 -Action Inspect``);
4. the current ``audit-head.json`` signer matches the config, or a
   historical signer archive exists for the head's thumbprint.

No private key material is ever read, logged or printed. Only the
non-secret public certificate and configuration metadata are inspected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Final


THUMBPRINT_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9A-Fa-f]{40}$")
SHA256_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_CONFIG_FIELDS: Final[frozenset[str]] = frozenset({
    "schema_version",
    "prototype",
    "store",
    "thumbprint",
    "public_certificate",
    "public_certificate_sha256",
    "signature_algorithm",
    "digest_algorithm",
    "formal_replacement",
})

# PRODUCT-REVIEW T-07：密钥托管形态（A=维护机非导出证书，B=受控介质，
# C=独立审计节点）。缺省视为 A（当前原型形态），非法值失败关闭。
CUSTODY_MODES: Final[frozenset[str]] = frozenset({"A", "B", "C"})
_POWERSHELL_FALLBACK: Final[str] = (
    r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
)


class KeyHealthError(RuntimeError):
    """Raised when the configuration cannot even be loaded."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: Path) -> dict[str, object]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KeyHealthError(f"cannot read config {path}: {exc}") from exc
    try:
        config = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise KeyHealthError(f"config {path} is not valid JSON: {exc}") from exc
    if not isinstance(config, dict):
        raise KeyHealthError("config must be a JSON object")
    return config


def validate_config(config: dict[str, object]) -> list[str]:
    """Return a list of structural problems (empty means valid)."""
    problems: list[str] = []
    missing = sorted(REQUIRED_CONFIG_FIELDS - set(config))
    if missing:
        problems.append(f"missing config fields: {', '.join(missing)}")
    thumbprint = config.get("thumbprint")
    if not isinstance(thumbprint, str) or not THUMBPRINT_RE.fullmatch(thumbprint):
        problems.append("thumbprint must be a 40-char hexadecimal string")
    cert_sha = config.get("public_certificate_sha256")
    if not isinstance(cert_sha, str) or not SHA256_RE.fullmatch(cert_sha):
        problems.append("public_certificate_sha256 must be a 64-char lowercase hex digest")
    store = config.get("store")
    if store != "CurrentUser/My":
        problems.append("store must be 'CurrentUser/My' (pinned prototype policy)")
    for field in ("signature_algorithm", "digest_algorithm", "formal_replacement"):
        value = config.get(field)
        if not isinstance(value, str) or not value:
            problems.append(f"{field} must be a non-empty string")
    if config.get("schema_version") != "1.0":
        problems.append("schema_version must be '1.0'")
    return problems


def custody_problems(config: dict[str, object]) -> list[str]:
    """Validate the ``custody`` field (A/B/C); absent defaults to A."""
    custody = config.get("custody")
    if custody is None:
        return []
    if not isinstance(custody, str) or custody not in CUSTODY_MODES:
        return [f"custody must be one of {sorted(CUSTODY_MODES)}; got {custody!r}"]
    return []


def public_cert_problems(repo_root: Path, config: dict[str, object]) -> list[str]:
    problems: list[str] = []
    relative = config.get("public_certificate")
    if not isinstance(relative, str) or not relative:
        return ["public_certificate path is missing"]
    candidate = (repo_root / relative).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        return ["public_certificate escapes the repository root"]
    if not candidate.is_file():
        return [f"public certificate file is missing: {relative}"]
    expected = config.get("public_certificate_sha256")
    actual = _sha256_file(candidate)
    if expected != actual:
        problems.append(
            "public certificate file hash mismatch: "
            f"config={expected} actual={actual}"
        )
    return problems


def head_signer_problems(repo_root: Path, config: dict[str, object]) -> list[str]:
    """Check the current audit head's signer against config or archives."""
    head_path = repo_root / "loop" / "audit-head.json"
    if not head_path.exists():
        return []  # no head yet: nothing to cross-check
    try:
        head = json.loads(head_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return [f"audit-head.json is unreadable: {exc}"]
    signer = head.get("signer_thumbprint") if isinstance(head, dict) else None
    if not isinstance(signer, str) or not THUMBPRINT_RE.fullmatch(signer):
        return ["audit-head.json signer_thumbprint is invalid"]
    pinned = config.get("thumbprint")
    if signer.lower() == str(pinned).lower():
        return []
    archive = repo_root / "loop" / f"audit-signing-{signer.upper()}.json"
    if not archive.is_file():
        return [
            f"audit head signer {signer} does not match pinned config "
            f"{pinned} and no historical archive {archive.name} exists"
        ]
    try:
        archived = json.loads(archive.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return [f"historical archive {archive.name} is unreadable"]
    if (
        not isinstance(archived, dict)
        or archived.get("thumbprint") != signer
    ):
        return [f"historical archive {archive.name} does not match its signer"]
    return []


def _powershell_executable() -> str:
    configured = os.environ.get("COEVO_POWERSHELL_PATH")
    if configured and Path(configured).is_absolute() and Path(configured).is_file():
        return configured
    found = shutil.which("pwsh") or shutil.which("powershell")
    if found and Path(found).is_absolute() and Path(found).is_file():
        return found
    fallback = Path(_POWERSHELL_FALLBACK)
    if fallback.is_file():
        return str(fallback)
    return ""


def inspect_problems(
    script: Path,
    config_path: Path,
    repo_root: Path,
) -> list[str]:
    """Run ``audit_signature.ps1 -Action Inspect`` and surface problems."""
    executable = _powershell_executable()
    if not executable:
        return ["Windows PowerShell is unavailable for certificate inspection"]
    result = subprocess.run(
        [
            executable,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-Action",
            "Inspect",
            "-ConfigPath",
            str(config_path),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        return [f"certificate inspection failed: {message}"]
    try:
        inspected = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ["certificate inspection returned malformed JSON"]
    problems: list[str] = []
    if inspected.get("match_count") != 1:
        problems.append(
            f"pinned certificate count in CurrentUser/My is "
            f"{inspected.get('match_count')!r} (must be exactly 1)"
        )
    if inspected.get("has_private_key") is not True:
        problems.append("pinned certificate has no private key")
    if inspected.get("pfx_exportable") is not False:
        problems.append("pinned certificate private key is exportable (must refuse signing)")
    return problems


def remediations(problems: list[str]) -> list[str]:
    hints: list[str] = []
    joined = "\n".join(problems).lower()
    if "cannot read config" in joined or "not valid json" in joined:
        hints.append(
            "恢复配置：备份现有 loop/audit-signing.json 后按 runbook 重建 "
            "（scripts/audit_signature.ps1 -Action Initialize 会生成新证书与公钥文件）"
        )
    if "missing config fields" in joined or "thumbprint" in joined or "sha256" in joined:
        hints.append("修正 loop/audit-signing.json 的字段后再运行门禁")
    if "public certificate" in joined:
        hints.append("恢复 loop/audit-signing-public.cer（与配置哈希一致），缺失或哈希不符时不得签名")
    if "currentuser/my" in joined or "private key" in joined or "exportable" in joined:
        hints.append(
            "在 Cert:\\CurrentUser\\My 恢复/创建非导出 CodeSigning 证书 "
            "（见 docs/operations/audit-key-runbook.md §3 恢复流程）"
        )
    if "historical archive" in joined or "does not match pinned" in joined:
        hints.append(
            "为历史签名者补档 loop/audit-signing-<thumbprint>.json，"
            "或按 runbook 将配置切回对应签名者"
        )
    if "powershell" in joined:
        hints.append("确保 Windows PowerShell 5.1 可用（SystemRoot\\System32\\WindowsPowerShell\\v1.0\\powershell.exe）")
    return hints


def build_report(
    repo_root: Path,
    config_path: Path,
    *,
    inspect: bool,
) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    problems: list[str] = []
    try:
        config = load_config(config_path)
    except KeyHealthError as exc:
        problems.append(str(exc))
        checks.append({"name": "config.load", "ok": False, "detail": str(exc)})
        return {
            "ok": False,
            "config": str(config_path),
            "checks": checks,
            "problems": problems,
            "remediations": remediations(problems),
        }

    def _add(name: str, issues: list[str]) -> None:
        checks.append({"name": name, "ok": not issues, "detail": "; ".join(issues) or "ok"})
        problems.extend(issues)

    _add("config.structure", validate_config(config))
    _add("config.custody", custody_problems(config))
    _add("config.public_certificate", public_cert_problems(repo_root, config))
    _add("config.head_signer", head_signer_problems(repo_root, config))
    if inspect:
        _add(
            "certificate.inspect",
            inspect_problems(
                repo_root / "scripts" / "audit_signature.ps1",
                config_path,
                repo_root,
            ),
        )
    return {
        "ok": not problems,
        "config": str(config_path),
        "checks": checks,
        "problems": problems,
        "remediations": remediations(problems),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit-signing key health diagnostics (fail-closed)"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="audit-signing.json path (default: loop/audit-signing.json under repo root)",
    )
    parser.add_argument(
        "--no-inspect",
        action="store_true",
        help="skip the CurrentUser/My certificate inspection (config-only check)",
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    config_path = (
        args.config.resolve()
        if args.config is not None
        else repo_root / "loop" / "audit-signing.json"
    )
    report = build_report(
        repo_root, config_path, inspect=not args.no_inspect
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
