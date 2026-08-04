"""US-3 PII redaction layer (US-3-AC-1 / AC-1 + AC-2).

The recommender MUST NOT receive raw PII. This module is the only
boundary where raw identity attributes (name, email, organisation)
are converted into stable codes + hashes + non-PII display hints.

Properties (fail-closed by construction)
-----------------------------------------
* **Irreversible within the slice.** ``redact_identity`` returns a
  :class:`RedactedIdentity` that carries NO recoverable form of the
  raw input. The SHA-256 ``identity_hash`` is for cross-record
  correlation only; it does not store the input.
* **Deterministic.** Given the same ``(pool_code, raw_name, raw_email,
  org_code)`` tuple, the output is byte-identical. This lets the
  recommender de-duplicate records across imports.
* **Display-hint bounded.** ``display_hint`` is at most 16 characters
  and is derived from the *hash*, not from the raw name. Callers
  cannot reverse-engineer PII from the hint.
* **No silent fallback.** An empty raw name, email, or org_code
  raises :class:`TalentValidationError`. AC-2 explicitly forbids
  allowing blank identities into the talent pool.

This module is pure-Python; no IO, no model, no crypto library other
than :mod:`hashlib` (stdlib).
"""
from __future__ import annotations

import hashlib
import re


from .models import (
    RedactedIdentity,
    TalentValidationError,
)


_SAFE_CODE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.\-]{0,63}$")
_DISPLAY_MAX = 16


def stable_pool_code(raw_org: str) -> str:
    """Turn a free-form organisation name into a stable safe-id pool code.

    The code is deterministic for the same input (lower-cased +
    non-alnum replaced with underscores + collapsed). Returns a string
    matching :data:`_SAFE_CODE`.
    """
    if not isinstance(raw_org, str) or not raw_org.strip():
        raise TalentValidationError("raw_org must be a non-empty string")
    lowered = raw_org.strip().lower()
    cleaned = re.sub(r"[^a-z0-9_]+", "_", lowered).strip("_")
    if not cleaned:
        raise TalentValidationError(
            f"raw_org {raw_org!r} does not yield a usable pool code"
        )
    if not _SAFE_CODE.match(cleaned):
        # Truncate to safe-id length
        cleaned = cleaned[:64]
        cleaned = re.sub(r"[^a-zA-Z0-9_.\-]", "_", cleaned)
        if not _SAFE_CODE.match(cleaned):
            raise TalentValidationError(
                f"derived pool code {cleaned!r} is not a safe-id"
            )
    return cleaned


def _digest_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def redact_identity(
    *,
    pool_code: str,
    raw_name: str,
    raw_email: str,
    org_code: str,
) -> RedactedIdentity:
    """Produce a :class:`RedactedIdentity` from raw inputs.

    The function is the ONLY entry point for raw PII into the
    recommender slice. The output carries:

    * ``pool_code`` (echoed for downstream sanity checks);
    * ``display_hint`` — first 16 chars of the identity hash, lower-cased,
      with non-safe-id chars replaced. Suitable for UI rendering
      without leaking PII.
    * ``identity_hash`` — SHA-256 hex of the canonicalised identity
      string. Two records with identical inputs produce identical
      hashes (so the recommender can deduplicate imports), but the
      hash cannot be reversed to recover the raw input.
    """
    if not _SAFE_CODE.match(pool_code):
        raise TalentValidationError(
            f"pool_code must match safe-id; got {pool_code!r}"
        )
    if not isinstance(raw_name, str) or not raw_name.strip():
        raise TalentValidationError("raw_name must be a non-empty string")
    if not isinstance(raw_email, str) or not raw_email.strip():
        raise TalentValidationError("raw_email must be a non-empty string")
    if not _SAFE_CODE.match(org_code):
        raise TalentValidationError(
            f"org_code must match safe-id; got {org_code!r}"
        )

    canonical = f"{pool_code}|{raw_name.strip().lower()}|{raw_email.strip().lower()}|{org_code}"
    digest = _digest_hex(canonical)

    hint_source = digest[:_DISPLAY_MAX * 2].lower()
    # Substitute any non-safe-id char with '_' so display_hint is safe
    hint = re.sub(r"[^a-z0-9_]", "_", hint_source)[:_DISPLAY_MAX]
    if not hint:
        raise TalentValidationError(
            "derived display_hint is empty; refusing to emit"
        )

    return RedactedIdentity(
        pool_code=pool_code,
        display_hint=hint,
        identity_hash=digest,
    )
