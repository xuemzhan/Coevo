"""Offline .agent package protocol.

This package implements the wire-level surface of US-5 (the .agent
envelope). Two modules live here today:

* ``agent_package`` — Round-1 (US-5-AC-1): the binary Fixed Header
  and the canonical JSON Envelope Header plus the surrounding strict
  validation, with no cryptographic operation. Inner-payload
  decryption, SM2 key-wrap, SM2 signing / verification, manifest
  parsing and replay detection belong to subsequent slices
  (US-5 AC-2 and onward) and require the approved SM2/SM4 product
  (a password-scheme change per AGENTS.md §6).

* ``sm2_extension`` — deferred algorithm registry only. US-5-AC-1 does
  not advertise RSA or encode extension fields; SM2 remains fail-closed until
  a later approved cryptographic-product AC.
"""

from .agent_package import (
    ENVELOPE_MAX_BYTES,
    FIXED_HEADER_SIZE,
    MAGIC,
    PACKAGE_TYPES,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    AgentPackageCanonicalizationError,
    AgentPackageEnvelopeError,
    AgentPackageError,
    AgentPackageFlags,
    AgentPackageLayoutError,
    AgentPackageMagicError,
    AgentPackageVersionError,
    EnvelopeHeader,
    ParsedPackageHeader,
    build_envelope_template,
    decode_envelope,
    decode_fixed_header,
    encode_envelope,
    encode_fixed_header,
    parse_package_header,
)
from .sm2_extension import (
    IMPLEMENTED_KEY_ALGORITHMS,
    SM2_SM3,
    SUPPORTED_KEY_ALGORITHMS,
    AgentPackageAlgorithmUnsupportedError,
    require_supported_key_algorithm,
)

__all__ = [
    "MAGIC",
    "PROTOCOL_MAJOR",
    "PROTOCOL_MINOR",
    "FIXED_HEADER_SIZE",
    "ENVELOPE_MAX_BYTES",
    "PACKAGE_TYPES",
    "IMPLEMENTED_KEY_ALGORITHMS",
    "SM2_SM3",
    "SUPPORTED_KEY_ALGORITHMS",
    "AgentPackageAlgorithmUnsupportedError",
    "AgentPackageCanonicalizationError",
    "AgentPackageEnvelopeError",
    "AgentPackageError",
    "AgentPackageFlags",
    "AgentPackageLayoutError",
    "AgentPackageMagicError",
    "AgentPackageVersionError",
    "EnvelopeHeader",
    "ParsedPackageHeader",
    "build_envelope_template",
    "decode_envelope",
    "decode_fixed_header",
    "encode_envelope",
    "encode_fixed_header",
    "parse_package_header",
    "require_supported_key_algorithm",
]
