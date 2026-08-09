"""Strict validation performed before identity data reaches SQLite or audit logs."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 身份数据入库存前严格校验：敏感键拒绝、循环/别名结构拒绝、证书可用性。

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import UTC, datetime
from typing import Any, Mapping

from src.coevo.canon import canonical_digest
from .certificates import CertificateError, inspect_certificate
from .models import ClientIdentity, IdentityBundle, Organization, ProjectRoleBinding, TrustedCertificate, UserIdentity

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
FORBIDDEN_KEYS = {"privatekey", "pkcs8", "pkcs12", "pfx", "passphrase", "password", "secret", "filepath", "path"}
ALLOWED_ROLES = {"project_owner", "project_member"}


class ValidationError(ValueError):
    pass


class SensitiveInputError(ValidationError):
    pass


class CertificateStatusError(ValidationError):
    pass


def _key_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def reject_sensitive_input(value: Any) -> None:
    """Reject payloads containing private-key material, secrets or cycles."""
    stack: list[tuple[Any, int]] = [(value, 0)]
    seen: set[int] = set()
    nodes = 0
    aggregate_size = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > 512 or depth > 32:
            raise ValidationError("input structure exceeds safety limits")
        if isinstance(current, Mapping):
            marker = id(current)
            if marker in seen:
                raise ValidationError("cyclic or aliased input structure is not accepted")
            seen.add(marker)
            for key, child in current.items():
                token = _key_token(str(key))
                if token in FORBIDDEN_KEYS or "privatekey" in token:
                    raise SensitiveInputError("sensitive or private-key input is not accepted")
                stack.append((child, depth + 1))
        elif isinstance(current, (list, tuple)):
            marker = id(current)
            if marker in seen:
                raise ValidationError("cyclic or aliased input structure is not accepted")
            seen.add(marker)
            stack.extend((child, depth + 1) for child in current)
        elif isinstance(current, str):
            aggregate_size += len(current.encode("utf-8", errors="replace"))
            if "PRIVATE KEY" in current.upper():
                raise SensitiveInputError("private-key material is not accepted")
        elif isinstance(current, (bytes, bytearray)):
            aggregate_size += len(current)
            if b"PRIVATE KEY" in bytes(current).upper():
                raise SensitiveInputError("private-key material is not accepted")
        if aggregate_size > 2 * 1024 * 1024:
            raise ValidationError("input payload exceeds safety limit")


def validate_id(name: str, value: Any) -> str:
    """Validate ``value`` against the safe-ID grammar and return it."""
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ValidationError(f"invalid {name}")
    return value


def audit_identifier(value: Any) -> str:
    """Return a safe audit identifier, hashing malformed inputs."""
    try:
        return validate_id("audit identifier", value)
    except ValidationError:
        digest = hashlib.sha256(repr(value).encode("utf-8", errors="replace")).hexdigest()[:16]
        return f"invalid:{digest}"


def _text(name: str, value: Any, maximum: int = 128) -> str:
    """Fail-closed validation of a text field value."""
    if not isinstance(value, str):
        raise ValidationError(f"invalid {name}")
    normalized = unicodedata.normalize("NFC", value.strip())
    if not normalized or len(normalized) > maximum or any(unicodedata.category(char).startswith("C") for char in normalized):
        raise ValidationError(f"invalid {name}")
    return normalized


def _object(name: str, value: Any, allowed: set[str]) -> Mapping[str, Any]:
    """Fail-closed validation of an object field value."""
    if not isinstance(value, Mapping):
        raise ValidationError(f"{name} must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise ValidationError(f"unsupported {name} fields: {', '.join(sorted(map(str, unknown)))}")
    if set(value) != allowed:
        raise ValidationError(f"missing {name} fields: {', '.join(sorted(allowed - set(value)))}")
    return value


def _instant(value: str) -> datetime:
    """Fail-closed validation of an ISO instant."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise CertificateStatusError("stored certificate timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise CertificateStatusError("stored certificate timestamp lacks timezone")
    return parsed.astimezone(UTC)


def assert_certificate_usable(certificate: TrustedCertificate, trusted_time: datetime) -> None:
    """Reject revoked, not-yet-valid or expired certificates (fail-closed)."""
    if trusted_time.tzinfo is None:
        raise CertificateStatusError("trusted time must include timezone")
    current = trusted_time.astimezone(UTC)
    if certificate.revoked:
        raise CertificateStatusError("certificate is revoked")
    if current < _instant(certificate.valid_from):
        raise CertificateStatusError("certificate is not yet valid")
    if current >= _instant(certificate.valid_to):
        raise CertificateStatusError("certificate is expired")


def _digestable(value: Any) -> Any:
    """Fail-closed validation of a digestable value."""
    if isinstance(value, Mapping):
        return {str(k): _digestable(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_digestable(item) for item in value]
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)}
    return value


def validate_bundle(payload: Any) -> IdentityBundle:
    """Validate an identity bundle payload and return the frozen model."""
    reject_sensitive_input(payload)
    root = _object("bundle", payload, {"organization", "user", "client", "certificate", "roles"})
    org = _object("organization", root["organization"], {"organization_id", "code", "name"})
    user = _object("user", root["user"], {"user_id", "organization_id", "display_name"})
    client = _object("client", root["client"], {"client_id", "organization_id", "assigned_user_id", "display_name"})
    cert = _object("certificate", root["certificate"], {"certificate_id", "owner_user_id", "bound_client_id", "certificate_der", "revoked"})
    roles_raw = root["roles"]
    if not isinstance(roles_raw, list) or not 1 <= len(roles_raw) <= 16:
        raise ValidationError("roles must contain 1..16 entries")

    organization = Organization(validate_id("organization_id", org["organization_id"]), _text("organization code", org["code"], 64), _text("organization name", org["name"]))
    identity = UserIdentity(validate_id("user_id", user["user_id"]), validate_id("user organization_id", user["organization_id"]), _text("user display_name", user["display_name"]))
    device = ClientIdentity(validate_id("client_id", client["client_id"]), validate_id("client organization_id", client["organization_id"]), validate_id("assigned_user_id", client["assigned_user_id"]), _text("client display_name", client["display_name"]))
    if type(cert["revoked"]) is not bool:
        raise ValidationError("invalid certificate revoked status")
    try:
        inspected = inspect_certificate(cert["certificate_der"])
    except CertificateError as exc:
        raise ValidationError(str(exc)) from exc
    certificate = TrustedCertificate(
        validate_id("certificate_id", cert["certificate_id"]),
        validate_id("owner_user_id", cert["owner_user_id"]),
        validate_id("bound_client_id", cert["bound_client_id"]),
        cert["certificate_der"],
        inspected.public_key_spki_der,
        inspected.fingerprint_sha256,
        inspected.valid_from.isoformat().replace("+00:00", "Z"),
        inspected.valid_to.isoformat().replace("+00:00", "Z"),
        inspected.serial_number,
        inspected.public_key_algorithm_oid,
        cert["revoked"],
    )

    if identity.organization_id != organization.organization_id or device.organization_id != organization.organization_id:
        raise ValidationError("organization references do not match")
    if device.assigned_user_id != identity.user_id or certificate.owner_user_id != identity.user_id or certificate.bound_client_id != device.client_id:
        raise ValidationError("identity/client/certificate references do not match")
    roles: list[ProjectRoleBinding] = []
    for raw in roles_raw:
        role = _object("role", raw, {"project_id", "user_id", "role_code"})
        code = role["role_code"]
        if code not in ALLOWED_ROLES:
            raise ValidationError("unsupported project role")
        binding = ProjectRoleBinding(validate_id("project_id", role["project_id"]), validate_id("role user_id", role["user_id"]), code)
        if binding.user_id != identity.user_id:
            raise ValidationError("role user does not match bundle user")
        roles.append(binding)
    if len(set(roles)) != len(roles):
        raise ValidationError("duplicate role binding")
    digest = canonical_digest(_digestable(root))
    return IdentityBundle(organization, identity, device, certificate, tuple(roles), digest)
