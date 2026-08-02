"""Offline .agent package protocol.

This package implements the wire-level surface of US-5 (the .agent
envelope). Sub-modules:

* ``agent_package`` — Round-1 (US-5-AC-1): the binary Fixed Header
  and the canonical JSON Envelope Header plus the surrounding strict
  validation, with no cryptographic operation.
* ``sm2_extension`` — deferred algorithm registry only. US-5-AC-1 does
  not advertise RSA or encode extension fields; SM2 remains fail-closed
  until a later approved cryptographic-product AC.
* ``agent_payload`` — US-5-AC-2 (§ 7.4): SM4-GCM AEAD payload block
  wire encoding (header + nonce + ciphertext + tag). The crypto
  operation is fail-closed in P1.
* ``sm2_sign`` — US-5-AC-2 (§ 9 + § 12): canonical manifest bytes
  + SM3 stand-in digest + signature-record wire encoding. SM2 sign
  / verify is fail-closed in P1.
* ``sm2_keywrap`` — US-5-AC-2 (§ 7.3): SM2 key-transport block
  wire encoding. SM2 wrap / unwrap is fail-closed in P1.
* ``replay_detector`` — US-5-AC-2 (§ 17): duplicate / replay /
  revocation detection logic over an in-memory registry.
* ``package_builder`` — US-5-AC-2 end-to-end builder / parser that
  ties the four layers together. Crypto-bearing surfaces remain
  fail-closed in P1.
* ``import_transaction`` — US-5-AC-3 (§ 15): the 7-step atomic-import
  transaction state machine (pure-function; no IO).
* ``processed_package_store`` — US-5-AC-3 (§ 17): in-memory
  processed-package registry with atomic register / scope / digest
  queries. Pure-function; DB persistence is a future slice.
* ``import_service`` — US-5-AC-3 facade tying the importer +
  store + replay detector + base_revision check together.
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
from .agent_payload import (
    PAYLOAD_HEADER_MAGIC,
    PAYLOAD_HEADER_SIZE,
    PAYLOAD_NONCE_SIZE,
    PAYLOAD_TAG_SIZE,
    AgentPackageCryptoUnavailableError,
    AgentPackageCryptoUnavailableError as AgentPackagePayloadCryptoUnavailableError,
    AgentPackageCryptoDecryptError,
    PayloadBlock,
    assemble_payload_block,
    decode_payload_header,
    encrypt_payload,
    decrypt_payload,
    encode_payload_header,
    generate_payload_nonce,
)
from .sm2_sign import (
    SIGNATURE_ALGORITHM,
    SIGNED_OBJECT_NAME,
    AgentPackageCanonicalizationError as AgentPackageSignatureCanonicalizationError,
    AgentPackageCryptoUnavailableError as AgentPackageSignCryptoUnavailableError,
    AgentPackageCryptoVerifyError,
    SignatureRecord,
    build_signature_record,
    canonical_manifest_bytes,
    compute_sm3_digest,
    decode_signature_record,
    sign_manifest,
    verify_signature,
)
from .sm2_keywrap import (
    KDF_ITERATIONS_DEFAULT,
    KDF_NAME,
    KEY_BLOCK_FORMAT,
    SESSION_KEY_SIZE,
    AgentPackageCryptoUnavailableError as AgentPackageKeywrapCryptoUnavailableError,
    KeyTransportBlock,
    build_key_transport_block,
    decode_key_transport_bytes,
    encode_key_transport_bytes,
    generate_session_key,
    unwrap_session_key,
    wrap_session_key,
)
from .replay_detector import (
    AgentPackageReplayError,
    ProcessedPackage,
    ReplayDecision,
    ReplayOutcome,
    check_reference_target,
    check_replay,
)
from .package_builder import (
    BuiltPackage,
    OpenedPackage,
    build_encrypted_package,
    build_signed_payload,
    build_unsigned_package,
    open_encrypted_package,
    parse_package_bytes,
)
from .import_transaction import (
    AgentPackageImportConflictError,
    AgentPackageImportError,
    AgentPackageImportReplayError,
    AgentPackageImportValidationError,
    AtomicImporter,
    ImportStep,
    ImportTransaction,
)
from .processed_package_store import (
    AgentPackageStoreDuplicateError,
    AgentPackageStoreError,
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from .import_service import (
    DEFAULT_EMPTY_STORE,
    ImportOutcome,
    PackageImportService,
)

__all__ = [
    "AgentPackageAlgorithmUnsupportedError",
    "AgentPackageCanonicalizationError",
    "AgentPackageCryptoDecryptError",
    "AgentPackageCryptoUnavailableError",
    "AgentPackageCryptoVerifyError",
    "AgentPackageEnvelopeError",
    "AgentPackageError",
    "AgentPackageFlags",
    "AgentPackageImportConflictError",
    "AgentPackageImportError",
    "AgentPackageImportReplayError",
    "AgentPackageImportValidationError",
    "AgentPackageKeywrapCryptoUnavailableError",
    "AgentPackageLayoutError",
    "AgentPackageMagicError",
    "AgentPackagePayloadCryptoUnavailableError",
    "AgentPackageReplayError",
    "AgentPackageSignatureCanonicalizationError",
    "AgentPackageSignCryptoUnavailableError",
    "AgentPackageStoreDuplicateError",
    "AgentPackageStoreError",
    "AgentPackageVersionError",
    "AtomicImporter",
    "BuiltPackage",
    "OpenedPackage",
    "DEFAULT_EMPTY_STORE",
    "ENVELOPE_MAX_BYTES",
    "EnvelopeHeader",
    "FIXED_HEADER_SIZE",
    "ImportOutcome",
    "ImportStep",
    "ImportTransaction",
    "IMPLEMENTED_KEY_ALGORITHMS",
    "KDF_ITERATIONS_DEFAULT",
    "KDF_NAME",
    "KEY_BLOCK_FORMAT",
    "MAGIC",
    "PACKAGE_TYPES",
    "PAYLOAD_HEADER_MAGIC",
    "PAYLOAD_HEADER_SIZE",
    "PAYLOAD_NONCE_SIZE",
    "PAYLOAD_TAG_SIZE",
    "PROTOCOL_MAJOR",
    "PROTOCOL_MINOR",
    "PackageImportService",
    "ParsedPackageHeader",
    "PayloadBlock",
    "ProcessedPackage",
    "ProcessedPackageRecord",
    "ProcessedPackageStore",
    "ReplayDecision",
    "ReplayOutcome",
    "SESSION_KEY_SIZE",
    "SIGNATURE_ALGORITHM",
    "SIGNED_OBJECT_NAME",
    "SM2_SM3",
    "SUPPORTED_KEY_ALGORITHMS",
    "SignatureRecord",
    "KeyTransportBlock",
    "assemble_payload_block",
    "build_envelope_template",
    "build_encrypted_package",
    "build_key_transport_block",
    "build_signature_record",
    "build_signed_payload",
    "build_unsigned_package",
    "canonical_manifest_bytes",
    "check_reference_target",
    "check_replay",
    "compute_sm3_digest",
    "decode_envelope",
    "decode_fixed_header",
    "decode_key_transport_bytes",
    "decode_payload_header",
    "decode_signature_record",
    "decrypt_payload",
    "encode_envelope",
    "encode_fixed_header",
    "encode_key_transport_bytes",
    "encode_payload_header",
    "encrypt_payload",
    "generate_payload_nonce",
    "generate_session_key",
    "parse_package_bytes",
    "open_encrypted_package",
    "parse_package_header",
    "require_supported_key_algorithm",
    "sign_manifest",
    "unwrap_session_key",
    "verify_signature",
    "wrap_session_key",
]
