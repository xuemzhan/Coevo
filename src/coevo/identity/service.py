"""Authorized identity registration service with a trusted policy boundary."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 身份注册服务（US-0）：
#   register_identity_bundle(actor, request_id, payload)：安全管理员
#     以 identity:write 权限提交身份包；校验信封（audit_identifier）、
#     拒绝敏感输入（私钥/口令）、校验五要素一致性（组织/用户/终端/
#     证书/项目角色），最后经 IdentityRepository 原子入库并审计。
#     同 request_id 重放返回 replayed=True（幂等，不重复入库）。
#   关键安全不变量：权限边界由注入的 Authorizer 决定（组合根装配，
#     绝不由请求数据构造）；证书指纹唯一约束在仓库层强制，防止证书复用。

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .models import Actor, RegistrationResult
from .repository import ConflictError, IdentityRepository
from .validation import SensitiveInputError, ValidationError, audit_identifier, reject_sensitive_input, validate_bundle, validate_id


class UnauthorizedError(PermissionError):
    pass


class Authorizer(Protocol):
    def is_allowed(self, actor_id: str, permission: str) -> bool: ...


class StaticAuthorizer:
    """Trusted composition-root policy; never construct this from request data."""

    def __init__(self, grants: Mapping[str, frozenset[str]]):
        self._grants = {actor: frozenset(permissions) for actor, permissions in grants.items()}

    def is_allowed(self, actor_id: str, permission: str) -> bool:
        return permission in self._grants.get(actor_id, frozenset())


class IdentityService:
    def __init__(self, repository: IdentityRepository, authorizer: Authorizer):
        self.repository = repository
        self.authorizer = authorizer

    def register_identity_bundle(self, actor: Actor, request_id: str, payload: Any) -> RegistrationResult:
        """Register an identity bundle after authorization."""
        raw_actor_id = getattr(actor, "actor_id", None)
        actor_audit_id = audit_identifier(raw_actor_id)
        request_audit_id = audit_identifier(request_id)
        try:
            actor_id = validate_id("actor_id", raw_actor_id)
            valid_request_id = validate_id("request_id", request_id)
        except ValidationError:
            self.repository.record_rejection(actor_audit_id, request_audit_id, "invalid_envelope")
            raise
        try:
            reject_sensitive_input(payload)
        except SensitiveInputError:
            self.repository.record_rejection(actor_id, valid_request_id, "sensitive_input_rejected")
            raise
        except ValidationError:
            self.repository.record_rejection(actor_id, valid_request_id, "invalid_input")
            raise
        if not self.authorizer.is_allowed(actor_id, "identity:write"):
            self.repository.record_rejection(actor_id, valid_request_id, "unauthorized")
            raise UnauthorizedError("identity:write permission is required")
        try:
            bundle = validate_bundle(payload)
        except ValidationError:
            self.repository.record_rejection(actor_id, valid_request_id, "invalid_input")
            raise
        try:
            return self.repository.register(actor_id, valid_request_id, bundle)
        except ConflictError:
            self.repository.record_rejection(actor_id, valid_request_id, "conflict", bundle.payload_digest)
            raise
