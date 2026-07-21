"""Fail-closed X.509 inspection through controlled Windows/.NET stdin."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / "scripts" / "inspect_certificate.ps1"


def _powershell_executable() -> str:
    exe = os.environ.get("COEVO_POWERSHELL_PATH")
    if exe and Path(exe).is_absolute():
        return exe
    fallback = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if fallback.is_file():
        return str(fallback)
    raise CertificateError("Windows PowerShell is unavailable")


class CertificateError(ValueError):
    pass


@dataclass(frozen=True)
class InspectedCertificate:
    fingerprint_sha256: str
    public_key_spki_der: bytes
    valid_from: datetime
    valid_to: datetime
    serial_number: str
    public_key_algorithm_oid: str


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise CertificateError("certificate helper returned an invalid timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CertificateError("certificate helper returned an invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise CertificateError("certificate helper timestamp lacks timezone")
    return parsed.astimezone(UTC)


def inspect_certificate(certificate_der: bytes) -> InspectedCertificate:
    if not isinstance(certificate_der, bytes) or not certificate_der or len(certificate_der) > 1024 * 1024:
        raise CertificateError("invalid certificate_der")
    if not HELPER.is_file():
        raise CertificateError("controlled certificate helper is unavailable")
    request = json.dumps({"certificate_der_base64": base64.b64encode(certificate_der).decode("ascii")}, separators=(",", ":"))
    process = subprocess.run(
        [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HELPER)],
        cwd=ROOT, input=request, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )
    if process.returncode:
        raise CertificateError("certificate is not an accepted DER X.509 certificate")
    try:
        item = json.loads(process.stdout)
        spki = base64.b64decode(item["spki_der_base64"], validate=True)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise CertificateError("certificate helper returned invalid output") from exc
    digest = hashlib.sha256(certificate_der).hexdigest()
    if item.get("schema_version") != "1.0" or item.get("content_type") != "Cert" or item.get("has_private_key") is not False:
        raise CertificateError("certificate helper output failed policy checks")
    if item.get("certificate_sha256") != digest or not spki or len(spki) > 64 * 1024:
        raise CertificateError("certificate helper output does not match input")
    valid_from = _instant(item.get("valid_from")); valid_to = _instant(item.get("valid_to"))
    if valid_from >= valid_to:
        raise CertificateError("certificate validity range is invalid")
    serial = item.get("serial_number"); algorithm = item.get("public_key_algorithm_oid")
    if not isinstance(serial, str) or not serial or not isinstance(algorithm, str):
        raise CertificateError("certificate helper returned incomplete metadata")
    return InspectedCertificate(digest, spki, valid_from, valid_to, serial, algorithm)
