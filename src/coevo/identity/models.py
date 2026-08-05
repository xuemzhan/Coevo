"""Internal immutable identity data models."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 身份领域不可变模型：Actor/组织/用户/客户端/可信证书/角色绑定等。

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    actor_id: str


@dataclass(frozen=True)
class Organization:
    organization_id: str
    code: str
    name: str


@dataclass(frozen=True)
class UserIdentity:
    user_id: str
    organization_id: str
    display_name: str


@dataclass(frozen=True)
class ClientIdentity:
    client_id: str
    organization_id: str
    assigned_user_id: str
    display_name: str


@dataclass(frozen=True)
class TrustedCertificate:
    certificate_id: str
    owner_user_id: str
    bound_client_id: str
    certificate_der: bytes
    public_key_spki_der: bytes
    fingerprint_sha256: str
    valid_from: str
    valid_to: str
    serial_number: str
    public_key_algorithm_oid: str
    revoked: bool


@dataclass(frozen=True)
class ProjectRoleBinding:
    project_id: str
    user_id: str
    role_code: str


@dataclass(frozen=True)
class IdentityBundle:
    organization: Organization
    user: UserIdentity
    client: ClientIdentity
    certificate: TrustedCertificate
    roles: tuple[ProjectRoleBinding, ...]
    payload_digest: str


@dataclass(frozen=True)
class RegistrationResult:
    request_id: str
    organization_id: str
    user_id: str
    client_id: str
    certificate_id: str
    replayed: bool = False
