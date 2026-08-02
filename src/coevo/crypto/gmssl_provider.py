"""Locked GmSSL 3.2.0 MVP prototype provider.

The Python process never receives private-key bytes, private-key passwords, or
an unwrapped SM4 session key. Those values exist only in the one-shot helper.
"""
from __future__ import annotations

import os
import hashlib
import json
import re
import struct
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .contract import ProviderScope

_MAGIC: Final[bytes] = b"COEVOCRYPTO/1"
_REPLY: Final[bytes] = b"COEVOCRYPTO-R/1"
_SAFE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
_MAX_FRAME: Final[int] = 16 * 1024 * 1024


class GmsslPrototypeError(RuntimeError):
    """A stable fail-closed provider or helper failure."""

    code = "AGT-CRY-001"


@dataclass(frozen=True, slots=True)
class GmsslPrototypeHandle:
    """Non-secret identity reference; it contains no key or password bytes."""

    profile: str
    role: str
    certificate_id: str

    def __post_init__(self) -> None:
        if not _SAFE.fullmatch(self.profile):
            raise ValueError("profile must be a safe identifier")
        if self.role not in {"sender", "recipient"}:
            raise ValueError("role must be sender or recipient")
        if not isinstance(self.certificate_id, str) or not self.certificate_id:
            raise ValueError("certificate_id is required")


@dataclass(frozen=True, slots=True)
class SealedPayload:
    wrapped_key: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes


class GmsslPrototypeProvider:
    """One-shot COEVOCRYPTO/1 client with a controlled PowerShell launcher."""

    name = "gmssl-3.2.0-mvp-prototype"
    scope: Final[ProviderScope] = ProviderScope.MVP_PROTOTYPE
    key_handle_backed: Final[bool] = False

    def __init__(self, repository_root: str | Path, *, timeout_seconds: float = 10.0) -> None:
        root = Path(repository_root).resolve(strict=True)
        launcher = root / "scripts" / "invoke-gmssl-crypto.ps1"
        if not launcher.is_file() or launcher.is_symlink():
            raise GmsslPrototypeError("controlled crypto launcher is unavailable")
        try:
            lock = json.loads((root / "docs" / "dependencies" / "toolchain-lock.json").read_text("utf-8"))
            metadata = lock["tools"]["gmssl_prototype_provider"]["helper"]["launcher"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise GmsslPrototypeError("crypto provider lock metadata is unavailable") from exc
        launcher_bytes = launcher.read_bytes()
        if (len(launcher_bytes) != metadata.get("size")
                or hashlib.sha256(launcher_bytes).hexdigest() != metadata.get("sha256")):
            raise GmsslPrototypeError("controlled crypto launcher lock mismatch")
        if not 0.1 <= timeout_seconds <= 30.0:
            raise ValueError("timeout_seconds must be between 0.1 and 30")
        self._root = root
        self._launcher = launcher
        self._timeout = timeout_seconds

    def sender_handle(self, profile: str, certificate_id: str) -> GmsslPrototypeHandle:
        return GmsslPrototypeHandle(profile, "sender", certificate_id)

    def recipient_handle(self, profile: str, certificate_id: str) -> GmsslPrototypeHandle:
        return GmsslPrototypeHandle(profile, "recipient", certificate_id)

    def sm3(self, data: bytes) -> bytes:
        return self._invoke(1, "default", data)[0]

    def sign(self, handle: GmsslPrototypeHandle, data: bytes) -> bytes:
        self._require(handle, "sender")
        return self._invoke(2, handle.profile, data)[0]

    def verify(self, handle: GmsslPrototypeHandle, data: bytes, signature: bytes) -> bool:
        self._require(handle, "sender")
        result = self._invoke(3, handle.profile, data, signature)
        return len(result) == 1 and result[0] == b"\x01"

    def seal(self, handle: GmsslPrototypeHandle, plaintext: bytes, *, associated_data: bytes, nonce: bytes | None = None) -> SealedPayload:
        self._require(handle, "recipient")
        nonce = os.urandom(12) if nonce is None else nonce
        if not isinstance(nonce, bytes) or len(nonce) != 12:
            raise GmsslPrototypeError("SM4-GCM nonce must be 12 bytes")
        result = self._invoke(4, handle.profile, plaintext, associated_data, nonce)
        if len(result) != 4 or len(result[1]) != 12 or len(result[3]) != 16:
            raise GmsslPrototypeError("invalid seal response")
        return SealedPayload(*result)

    def open(self, handle: GmsslPrototypeHandle, sealed: SealedPayload, *, associated_data: bytes) -> bytes:
        self._require(handle, "recipient")
        if not isinstance(sealed, SealedPayload):
            raise TypeError("sealed must be SealedPayload")
        return self._invoke(
            5,
            handle.profile,
            sealed.wrapped_key,
            sealed.nonce,
            sealed.ciphertext,
            sealed.tag,
            associated_data,
        )[0]

    @staticmethod
    def _require(handle: GmsslPrototypeHandle, role: str) -> None:
        if not isinstance(handle, GmsslPrototypeHandle) or handle.role != role:
            raise GmsslPrototypeError(f"{role} handle is required")

    def _invoke(
        self,
        action: int,
        profile: str,
        *frames: bytes,
        retries: int = 1,
    ) -> tuple[bytes, ...]:
        if not _SAFE.fullmatch(profile) or not 1 <= len(frames) <= 5:
            raise GmsslPrototypeError("invalid provider request")
        if not isinstance(retries, int) or not 0 <= retries <= 3:
            raise ValueError("retries must be an integer in 0..3")
        values: list[bytes] = []
        for value in frames:
            if not isinstance(value, bytes) or len(value) > _MAX_FRAME:
                raise GmsslPrototypeError("provider frame must be bounded bytes")
            values.append(value)
        profile_bytes = profile.encode("ascii")
        request = bytearray(_MAGIC + bytes((action, len(profile_bytes))) + profile_bytes + bytes((len(values),)))
        for value in values:
            request.extend(struct.pack(">I", len(value)))
            request.extend(value)
        system_root = os.environ.get("SystemRoot", r"C:\Windows")
        powershell = Path(system_root) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        command = [
            str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-File", str(self._launcher),
            "-ProfileName", profile,
            "-HelperTimeoutMilliseconds", str(max(100, int(self._timeout * 1000))),
        ]
        environment = {"SystemRoot": system_root, "WINDIR": system_root}
        attempt = 0
        try:
            while True:
                attempt += 1
                request_payload = bytes(request)
                try:
                    completed = subprocess.run(
                        command,
                        cwd=self._root,
                        input=request_payload,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=environment,
                        timeout=self._timeout + 5.0,
                        check=False,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    if attempt <= retries:
                        time.sleep(0.25 * attempt)
                        continue
                    raise GmsslPrototypeError("GCP-E-LAUNCH") from exc
                if completed.returncode == 0:
                    return self._decode(completed.stdout)
                diagnostic = completed.stderr.decode("ascii", "replace").strip()
                if not re.fullmatch(
                    r"(?:GCP-E-[A-Z0-9-]+|.*GCP-E-[A-Z0-9-]+.*)",
                    diagnostic,
                    re.DOTALL,
                ):
                    # Launch-level failure with an unrecognised diagnostic is
                    # transient (helper lock contention / AV scan / process
                    # spawn race); retry a bounded number of times. Recognised
                    # GCP-E-* diagnostics from the helper are authoritative
                    # and are NEVER retried.
                    diagnostic = "GCP-E-LAUNCH"
                    if attempt <= retries:
                        time.sleep(0.25 * attempt)
                        continue
                raise GmsslPrototypeError(diagnostic)
        finally:
            # Hygiene: never leave request bytes (which may embed wrapped
            # key material) resident in the Python heap after the call.
            request[:] = b"\x00" * len(request)

    @staticmethod
    def _decode(data: bytes) -> tuple[bytes, ...]:
        if not data.startswith(_REPLY) or len(data) < len(_REPLY) + 1:
            raise GmsslPrototypeError("invalid crypto helper response")
        cursor = len(_REPLY)
        count = data[cursor]
        cursor += 1
        frames: list[bytes] = []
        for _ in range(count):
            if cursor + 4 > len(data):
                raise GmsslPrototypeError("truncated crypto helper response")
            size = struct.unpack(">I", data[cursor : cursor + 4])[0]
            cursor += 4
            if size > _MAX_FRAME or cursor + size > len(data):
                raise GmsslPrototypeError("invalid crypto helper frame")
            frames.append(data[cursor : cursor + size])
            cursor += size
        if cursor != len(data):
            raise GmsslPrototypeError("trailing crypto helper response bytes")
        return tuple(frames)
