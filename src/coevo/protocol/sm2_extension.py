"""Deferred algorithm identifiers for future approved cryptographic products.

US-5-AC-1 implements only the Fixed Header and base Envelope Header. It does
not define or advertise an RSA wire suite, and it does not encode extension
fields. The protocol-mandated SM2/SM3 identifier is retained solely so later
ACs can fail closed until an approved implementation is available.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 未来批准密码产品的算法标识占位：不支持的算法显式拒绝。

from __future__ import annotations

from .agent_package import AgentPackageError

SM2_SM3 = "sm2-with-sm3"
SUPPORTED_KEY_ALGORITHMS = frozenset({SM2_SM3})
IMPLEMENTED_KEY_ALGORITHMS: frozenset[str] = frozenset()


class AgentPackageAlgorithmUnsupportedError(AgentPackageError):
    """The declared algorithm has no approved runtime implementation."""


def require_supported_key_algorithm(algorithm: str) -> str:
    """Fail closed until a later AC wires an approved SM2 product."""
    if algorithm not in SUPPORTED_KEY_ALGORITHMS:
        raise AgentPackageAlgorithmUnsupportedError(
            f"algorithm {algorithm!r} is not recognised by the protocol"
        )
    raise AgentPackageAlgorithmUnsupportedError(
        f"algorithm {algorithm!r} is declared but no approved runtime "
        "implementation is available"
    )


__all__ = [
    "SM2_SM3",
    "SUPPORTED_KEY_ALGORITHMS",
    "IMPLEMENTED_KEY_ALGORITHMS",
    "AgentPackageAlgorithmUnsupportedError",
    "require_supported_key_algorithm",
]
