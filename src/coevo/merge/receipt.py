"""Signed, sealed merge commit receipts for the US-10/US-11 trust boundary."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-10/11 信任边界：签名合并收据 + 密封收据 store（访问期全量重校验），
# 快照冻结防篡改。
from __future__ import annotations

import base64
import dataclasses
import datetime as dt
import hashlib
import json
from dataclasses import dataclass

from src.coevo.identity import PrivateKeyReference, PrivateKeyService
from src.coevo.report import ReportStatus
from src.coevo.task_decomposition import (
    Deliverable, DependencyEdge, Milestone, ProjectBaseline, Task,
    WorkPackage,
)
from src.coevo.task_decomposition.models import Override

BASELINE_DIGEST_ALGORITHM = "sha256"
BASELINE_SCHEMA = "coevo.project-baseline/1.0"
BASELINE_DOMAIN = "coevo.project-baseline"
RECEIPT_DOMAIN = "coevo.merge.commit-receipt"
RECEIPT_SCHEMA = "1.0"
SIGNATURE_ALGORITHM = "RSA-PKCS1-v1_5-SHA256"
COMMITTED_STATUS_DECISIONS = frozenset({"accept", "manual"})
RECEIPT_PACKAGE_TYPES = frozenset({"RESULT_SUBMISSION", "TASK_PROGRESS"})
_DOMAIN_TYPES = frozenset({
    ProjectBaseline, WorkPackage, Task, Deliverable, DependencyEdge, Milestone,
    Override,
})
_STORE_SEAL = object()
_CANONICAL_MAX_DEPTH = 32
_CANONICAL_MAX_CONTAINER_ITEMS = 4096
_CANONICAL_MAX_NODES = 100000
_CANONICAL_MAX_STRING_BYTES = 1024 * 1024
_SNAPSHOT_MAX_BYTES = 2 * 1024 * 1024
_SNAPSHOT_BASE64_MAX_CHARS = 4 * ((_SNAPSHOT_MAX_BYTES + 2) // 3)
_RECEIPT_MAX_BYTES = 4 * 1024 * 1024


class MergeCommitReceiptError(Exception):
    """Fail-closed receipt validation or registration error."""


class MergeCommitReceiptDuplicateError(MergeCommitReceiptError):
    """A receipt, package identity, digest, or sequence was already committed."""


@dataclass(frozen=True)
class FrozenBaselineSnapshot:
    """One exact-type, transitively immutable baseline serialization."""

    baseline: ProjectBaseline
    payload: bytes
    digest: str

    def __post_init__(self) -> None:
        if type(self.baseline) is not ProjectBaseline:
            raise MergeCommitReceiptError("snapshot baseline must be exact ProjectBaseline")
        if type(self.payload) is not bytes or not self.payload:
            raise MergeCommitReceiptError("snapshot payload must be non-empty exact bytes")
        if self.digest != hashlib.sha256(self.payload).hexdigest():
            raise MergeCommitReceiptError("snapshot digest does not match payload")


def freeze_baseline(baseline: ProjectBaseline) -> FrozenBaselineSnapshot:
    """Validate and serialize a baseline exactly once, closing every reference."""
    if type(baseline) is not ProjectBaseline:
        raise MergeCommitReceiptError("baseline must be exact ProjectBaseline")
    baseline_copy = _copy_domain_value(baseline, path="baseline")
    canonical = {
        "domain": BASELINE_DOMAIN,
        "schema_version": RECEIPT_SCHEMA,
        "baseline": _freeze_value(baseline_copy, path="baseline"),
    }
    payload = _encode(canonical, max_bytes=_SNAPSHOT_MAX_BYTES)
    return FrozenBaselineSnapshot(
        baseline=baseline_copy, payload=payload,
        digest=hashlib.sha256(payload).hexdigest(),
    )


def canonical_baseline_digest(baseline: ProjectBaseline) -> str:
    """Return the canonical digest for a frozen baseline snapshot."""
    return freeze_baseline(baseline).digest


@dataclass(frozen=True)
class ReceiptSigningAuthority:
    """Explicit key/trust binding used by the controlled merge boundary."""

    service: PrivateKeyService
    reference: PrivateKeyReference
    signer_certificate_id: str
    parent_pinned_thumbprint: str

    def __post_init__(self) -> None:
        if type(self.service) is not PrivateKeyService:
            raise MergeCommitReceiptError("signing service must be exact PrivateKeyService")
        if type(self.reference) is not PrivateKeyReference:
            raise MergeCommitReceiptError("signing reference must be exact PrivateKeyReference")
        if self.signer_certificate_id != self.reference.bound_certificate_id:
            raise MergeCommitReceiptError("signer certificate does not bind the key reference")
        if not isinstance(self.parent_pinned_thumbprint, str) or not self.parent_pinned_thumbprint:
            raise MergeCommitReceiptError("parent certificate pin is required")


@dataclass(frozen=True)
class MergeCommitReceipt:
    receipt_id: str
    payload: bytes
    signature: bytes
    signature_algorithm: str
    signer_certificate_id: str
    signer_key_id: str
    signer_public_sha256: str
    signer_algorithm_oid: str
    parent_pinned_thumbprint: str
    signed_at: str
    store_id: str
    store_sequence: int
    previous_receipt_id: str | None
    previous_receipt_hash: str
    snapshot: FrozenBaselineSnapshot
    package_id: str
    package_digest: str
    sender_cert_id: str
    recipient_cert_id: str
    sequence_no: int
    package_type: str
    import_processed_at: str
    project_id: str
    task_id: str
    report_status: ReportStatus
    status_decision: str
    base_revision: str
    current_revision: str
    merged_revision: str
    commit_decided_at: str
    decision_maker: str
    baseline_digest_algorithm: str
    baseline_schema: str
    baseline_digest: str
    completed_task_id: str | None

    def __post_init__(self) -> None:
        _validate_receipt(self)

    def to_dict(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "payload_base64": base64.b64encode(self.payload).decode("ascii"),
            "signature_base64": base64.b64encode(self.signature).decode("ascii"),
            **_signed_fields(self, include_snapshot_payload=False),
        }


def build_signed_merge_commit_receipt(
    *, authority: ReceiptSigningAuthority, trusted_time: dt.datetime,
    actor_id: str = "merge-engine", **fields: object,
) -> MergeCommitReceipt:
    """Freeze, sign, immediately verify, and return one authoritative receipt."""
    if type(authority) is not ReceiptSigningAuthority:
        raise MergeCommitReceiptError("authority must be ReceiptSigningAuthority")
    if trusted_time.tzinfo is None:
        raise MergeCommitReceiptError("trusted_time must include timezone")
    snapshot = freeze_baseline(fields.pop("baseline"))
    signed_at = trusted_time.astimezone(dt.UTC).isoformat().replace("+00:00", "Z")
    signing_fields = dict(fields)
    if type(signing_fields.get("report_status")) is ReportStatus:
        signing_fields["report_status"] = signing_fields["report_status"].value
    signing_fields.update({
        "domain": RECEIPT_DOMAIN,
        "schema_version": RECEIPT_SCHEMA,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "signer_certificate_id": authority.signer_certificate_id,
        "signer_key_id": authority.reference.key_id,
        "signer_public_sha256": authority.reference.key_public_sha256,
        "signer_algorithm_oid": authority.reference.algorithm_oid,
        "parent_pinned_thumbprint": authority.parent_pinned_thumbprint,
        "signed_at": signed_at,
        "snapshot_domain": BASELINE_DOMAIN,
        "snapshot_schema_version": RECEIPT_SCHEMA,
        "snapshot_payload_base64": base64.b64encode(snapshot.payload).decode("ascii"),
        "baseline_digest": snapshot.digest,
    })
    payload = _encode(
        _canonical_plain(signing_fields), max_bytes=_RECEIPT_MAX_BYTES,
    )
    signature = authority.service.use(
        authority.reference, payload, trusted_time=trusted_time,
        actor_id=actor_id, request_id=str(fields.get("package_id", "-")),
    )
    verified = authority.service.verify(
        authority.reference, payload, signature, trusted_time=trusted_time,
        actor_id=actor_id, request_id=str(fields.get("package_id", "-")),
        expected_certificate_id=authority.signer_certificate_id,
        expected_parent_thumbprint=authority.parent_pinned_thumbprint,
        expected_public_sha256=authority.reference.key_public_sha256,
        expected_algorithm_oid=authority.reference.algorithm_oid,
    )
    if not verified:
        raise MergeCommitReceiptError("freshly signed receipt failed immediate verification")
    receipt_id = "mcr." + hashlib.sha256(payload + signature).hexdigest()
    return MergeCommitReceipt(
        receipt_id=receipt_id, payload=payload, signature=signature,
        signature_algorithm=SIGNATURE_ALGORITHM,
        signer_certificate_id=authority.signer_certificate_id,
        signer_key_id=authority.reference.key_id,
        signer_public_sha256=authority.reference.key_public_sha256,
        signer_algorithm_oid=authority.reference.algorithm_oid,
        parent_pinned_thumbprint=authority.parent_pinned_thumbprint,
        signed_at=signed_at, snapshot=snapshot, baseline_digest=snapshot.digest,
        **fields,
    )


def verify_signed_receipt(
    receipt: MergeCommitReceipt, *, authority: ReceiptSigningAuthority,
    trusted_time: dt.datetime, actor_id: str = "risk-analyzer",
) -> FrozenBaselineSnapshot:
    """Verify a signed receipt against the trust policy and return its snapshot."""
    if type(receipt) is not MergeCommitReceipt:
        raise MergeCommitReceiptError("receipt must be exact MergeCommitReceipt")
    if type(authority) is not ReceiptSigningAuthority:
        raise MergeCommitReceiptError("authority must be ReceiptSigningAuthority")
    _validate_receipt(receipt)
    if (
        receipt.signer_certificate_id != authority.signer_certificate_id
        or receipt.signer_key_id != authority.reference.key_id
        or receipt.signer_public_sha256 != authority.reference.key_public_sha256
        or receipt.signer_algorithm_oid != authority.reference.algorithm_oid
        or receipt.parent_pinned_thumbprint != authority.parent_pinned_thumbprint
    ):
        raise MergeCommitReceiptError("receipt signer does not match trust policy")
    if not authority.service.verify(
        authority.reference, receipt.payload, receipt.signature,
        trusted_time=trusted_time, actor_id=actor_id,
        request_id=receipt.receipt_id,
        expected_certificate_id=authority.signer_certificate_id,
        expected_parent_thumbprint=authority.parent_pinned_thumbprint,
        expected_public_sha256=authority.reference.key_public_sha256,
        expected_algorithm_oid=authority.reference.algorithm_oid,
    ):
        raise MergeCommitReceiptError("receipt signature is invalid")
    return receipt.snapshot


class MergeCommitReceiptStore:
    """Sealed persistent-value store; callers cannot inject initial records."""

    __slots__ = ("_receipts", "_by_id", "_by_project")

    def __init_subclass__(cls, **kwargs):
        raise TypeError("MergeCommitReceiptStore may not be subclassed")

    def __init__(self, receipts=(), *, _seal=None) -> None:
        if _seal is not _STORE_SEAL or type(receipts) is not tuple:
            raise MergeCommitReceiptError("receipt store construction is sealed")
        self._receipts = receipts
        self._validate_history()
        # 构造期建立 O(1) 查询索引：store 不可变，索引永不失效。
        # 访问时仍按原语义全量重校验历史——收据对象虽为 frozen dataclass，
        # 但 object.__setattr__ 可模拟构造后篡改，密封 store 必须在每次
        # 访问时重新验证才能发现；校验失败即抛错，不返回脏数据。
        by_id: dict[str, MergeCommitReceipt] = {}
        by_project: dict[str, list[MergeCommitReceipt]] = {}
        for receipt in receipts:
            by_id[receipt.receipt_id] = receipt
            by_project.setdefault(receipt.project_id, []).append(receipt)
        self._by_id = by_id
        self._by_project = by_project

    @classmethod
    def empty(cls) -> "MergeCommitReceiptStore":
        return cls((), _seal=_STORE_SEAL)

    def __copy__(self):
        raise MergeCommitReceiptError("receipt store copying is forbidden")

    def __deepcopy__(self, memo):
        raise MergeCommitReceiptError("receipt store copying is forbidden")

    def get(self, receipt_id: str) -> MergeCommitReceipt | None:
        self._validate_history()
        return self._by_id.get(receipt_id)

    def by_project(self, project_id: str) -> tuple[MergeCommitReceipt, ...]:
        self._validate_history()
        return tuple(self._by_project.get(project_id, ()))

    def _append(self, receipt: MergeCommitReceipt, *, _seal) -> "MergeCommitReceiptStore":
        if _seal is not _STORE_SEAL or type(receipt) is not MergeCommitReceipt:
            raise MergeCommitReceiptError("receipt append is sealed")
        return type(self)(self._receipts + (receipt,), _seal=_STORE_SEAL)

    def _validate_history(self) -> None:
        ids: set[str] = set()
        packages: set[str] = set()
        digests: set[str] = set()
        latest_revision: dict[str, str] = {}
        latest_sequence: dict[tuple[str, str, str], int] = {}
        previous: MergeCommitReceipt | None = None
        for receipt in self._receipts:
            if type(receipt) is not MergeCommitReceipt:
                raise MergeCommitReceiptError("store contains a non-receipt")
            _validate_receipt(receipt)
            if receipt.store_sequence != len(ids) + 1:
                raise MergeCommitReceiptError("receipt store sequence is discontinuous")
            if previous is not None and (
                receipt.store_id != previous.store_id
                or receipt.previous_receipt_id != previous.receipt_id
                or receipt.previous_receipt_hash
                != hashlib.sha256(previous.payload + previous.signature).hexdigest()
            ):
                raise MergeCommitReceiptError("receipt store chain link is invalid")
            if receipt.receipt_id in ids or receipt.package_id in packages or receipt.package_digest in digests:
                raise MergeCommitReceiptDuplicateError("duplicate receipt/package identity")
            if receipt.project_id in latest_revision and receipt.current_revision != latest_revision[receipt.project_id]:
                raise MergeCommitReceiptError("receipt chain revision is discontinuous")
            scope = (receipt.project_id, receipt.sender_cert_id, receipt.recipient_cert_id)
            if scope in latest_sequence and receipt.sequence_no <= latest_sequence[scope]:
                raise MergeCommitReceiptError("receipt package sequence is not increasing")
            ids.add(receipt.receipt_id); packages.add(receipt.package_id); digests.add(receipt.package_digest)
            latest_revision[receipt.project_id] = receipt.merged_revision
            latest_sequence[scope] = receipt.sequence_no
            previous = receipt

    def __len__(self) -> int:
        return len(self._receipts)

    def __iter__(self):
        return iter(self._receipts)


def append_signed_receipt(
    store: MergeCommitReceiptStore, receipt: MergeCommitReceipt,
) -> MergeCommitReceiptStore:
    """Append a signed receipt to a sealed store, returning the new store."""
    if type(store) is not MergeCommitReceiptStore:
        raise MergeCommitReceiptError("store must be exact MergeCommitReceiptStore")
    return store._append(receipt, _seal=_STORE_SEAL)


def _validate_receipt(receipt: MergeCommitReceipt) -> None:
    if type(receipt.payload) is not bytes or type(receipt.signature) is not bytes or not receipt.signature:
        raise MergeCommitReceiptError("receipt payload/signature must be exact non-empty bytes")
    if type(receipt.snapshot) is not FrozenBaselineSnapshot:
        raise MergeCommitReceiptError("receipt snapshot must be exact FrozenBaselineSnapshot")
    refreshed_snapshot = freeze_baseline(receipt.snapshot.baseline)
    if (
        refreshed_snapshot.payload != receipt.snapshot.payload
        or refreshed_snapshot.digest != receipt.snapshot.digest
    ):
        raise MergeCommitReceiptError("snapshot object changed after freeze")
    for name in (
        "receipt_id", "package_id", "package_digest", "sender_cert_id", "recipient_cert_id",
        "package_type", "import_processed_at", "project_id", "task_id", "base_revision",
        "current_revision", "merged_revision", "commit_decided_at", "decision_maker",
        "baseline_digest_algorithm", "baseline_schema", "baseline_digest",
        "signature_algorithm", "signer_certificate_id", "signer_key_id",
        "signer_public_sha256", "signer_algorithm_oid",
        "parent_pinned_thumbprint", "signed_at",
    ):
        if not isinstance(getattr(receipt, name), str) or not getattr(receipt, name):
            raise MergeCommitReceiptError(f"{name} must be a non-empty string")
    if type(receipt.sequence_no) is not int or receipt.sequence_no < 1:
        raise MergeCommitReceiptError("sequence_no must be a positive exact integer")
    if type(receipt.store_sequence) is not int or receipt.store_sequence < 1:
        raise MergeCommitReceiptError("store_sequence must be a positive exact integer")
    if not isinstance(receipt.store_id, str) or not receipt.store_id:
        raise MergeCommitReceiptError("store_id is required")
    if receipt.store_sequence == 1:
        if receipt.previous_receipt_id is not None or receipt.previous_receipt_hash != "0" * 64:
            raise MergeCommitReceiptError("first receipt has invalid previous link")
    elif (
        not isinstance(receipt.previous_receipt_id, str)
        or not receipt.previous_receipt_id
        or len(receipt.previous_receipt_hash) != 64
    ):
        raise MergeCommitReceiptError("receipt previous link is incomplete")
    if type(receipt.report_status) is not ReportStatus:
        raise MergeCommitReceiptError("report_status must be exact ReportStatus")
    if receipt.package_type not in RECEIPT_PACKAGE_TYPES:
        raise MergeCommitReceiptError("package_type is not mergeable")
    if receipt.status_decision not in COMMITTED_STATUS_DECISIONS:
        raise MergeCommitReceiptError("status_decision must be accept or manual")
    if receipt.signature_algorithm != SIGNATURE_ALGORITHM:
        raise MergeCommitReceiptError("unsupported receipt signature algorithm")
    if receipt.signer_algorithm_oid != "1.2.840.113549.1.1.1":
        raise MergeCommitReceiptError("unsupported signer key algorithm")
    if receipt.baseline_digest_algorithm != BASELINE_DIGEST_ALGORITHM or receipt.baseline_schema != BASELINE_SCHEMA:
        raise MergeCommitReceiptError("unsupported baseline digest/schema")
    if receipt.baseline_digest != receipt.snapshot.digest:
        raise MergeCommitReceiptError("receipt digest does not bind snapshot")
    if receipt.project_id != receipt.snapshot.baseline.project_id:
        raise MergeCommitReceiptError("receipt project does not bind snapshot")
    if receipt.decision_maker != receipt.recipient_cert_id:
        raise MergeCommitReceiptError("decision_maker must be verified recipient")
    if _revision_number(receipt.merged_revision, receipt.project_id) != _revision_number(receipt.current_revision, receipt.project_id) + 1:
        raise MergeCommitReceiptError("merged revision must advance exactly once")
    if receipt.base_revision != receipt.current_revision:
        raise MergeCommitReceiptError("base revision must equal current revision")
    if receipt.completed_task_id != (receipt.task_id if receipt.report_status is ReportStatus.COMPLETED else None):
        raise MergeCommitReceiptError("completed task marker is inconsistent")
    if _parse_utc(receipt.import_processed_at, "import_processed_at") > _parse_utc(receipt.commit_decided_at, "commit_decided_at"):
        raise MergeCommitReceiptError("import must not follow commit")
    _parse_utc(receipt.signed_at, "signed_at")
    if receipt.signed_at != receipt.commit_decided_at:
        raise MergeCommitReceiptError("receipt must be signed at commit decision time")
    if receipt.payload != _encode(
        _canonical_plain(_signed_fields(receipt, include_snapshot_payload=True)),
        max_bytes=_RECEIPT_MAX_BYTES,
    ):
        raise MergeCommitReceiptError("signed payload does not match receipt fields")
    if receipt.receipt_id != "mcr." + hashlib.sha256(receipt.payload + receipt.signature).hexdigest():
        raise MergeCommitReceiptError("receipt_id does not match signed contents")


def _signed_fields(receipt: MergeCommitReceipt, *, include_snapshot_payload: bool) -> dict[str, object]:
    result = {
        "domain": RECEIPT_DOMAIN, "schema_version": RECEIPT_SCHEMA,
        "signature_algorithm": receipt.signature_algorithm,
        "signer_certificate_id": receipt.signer_certificate_id,
        "signer_key_id": receipt.signer_key_id,
        "signer_public_sha256": receipt.signer_public_sha256,
        "signer_algorithm_oid": receipt.signer_algorithm_oid,
        "parent_pinned_thumbprint": receipt.parent_pinned_thumbprint,
        "signed_at": receipt.signed_at,
        "snapshot_domain": BASELINE_DOMAIN,
        "snapshot_schema_version": RECEIPT_SCHEMA,
    }
    for field in dataclasses.fields(receipt):
        if field.name not in {
            "receipt_id", "payload", "signature", "snapshot", "signature_algorithm",
            "signer_certificate_id", "signer_key_id", "signer_public_sha256",
            "signer_algorithm_oid",
            "parent_pinned_thumbprint", "signed_at",
        }:
            field_value = getattr(receipt, field.name)
            result[field.name] = (
                field_value.value
                if type(field_value) is ReportStatus
                else field_value
            )
    if include_snapshot_payload:
        result["snapshot_payload_base64"] = base64.b64encode(receipt.snapshot.payload).decode("ascii")
    return result


def _freeze_value(value: object, *, path: str) -> object:
    value_type = type(value)
    if value_type in _DOMAIN_TYPES:
        return {
            field.name: (
                _normalize_canonical_plain(
                    getattr(value, field.name), path=f"{path}.{field.name}",
                )
                if value_type is Override
                and field.name in {"original_value", "edited_value"}
                else _freeze_value(
                    getattr(value, field.name), path=f"{path}.{field.name}",
                )
            )
            for field in dataclasses.fields(value)
        }
    if value is None or value_type is str:
        return value
    if value_type is int:
        return value
    if value_type is bool:
        raise MergeCommitReceiptError(f"{path} contains forbidden boolean")
    if value_type is tuple:
        return [_freeze_value(item, path=f"{path}[{index}]") for index, item in enumerate(value)]
    raise MergeCommitReceiptError(f"{path} contains unsupported or mutable type {value_type.__name__}")


def _copy_domain_value(value: object, *, path: str) -> object:
    value_type = type(value)
    if value_type in _DOMAIN_TYPES:
        copied_fields = {}
        for field in dataclasses.fields(value):
            field_value = getattr(value, field.name)
            field_path = f"{path}.{field.name}"
            if (
                value_type is Override
                and field.name in {"target_path", "reason"}
                and (type(field_value) is not str or not field_value)
            ):
                raise MergeCommitReceiptError(
                    f"{field_path} must be a non-empty exact string"
                )
            if (
                value_type is Override
                and field.name in {"original_value", "edited_value"}
            ):
                copied_fields[field.name] = _normalize_canonical_plain(
                    field_value, path=field_path,
                )
            else:
                copied_fields[field.name] = _copy_domain_value(
                    field_value, path=field_path,
                )
        return value_type(**copied_fields)
    if value is None or value_type in (str, int):
        return value
    if value_type is bool:
        raise MergeCommitReceiptError(f"{path} contains forbidden boolean")
    if value_type is tuple:
        return tuple(
            _copy_domain_value(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    raise MergeCommitReceiptError(
        f"{path} contains unsupported or mutable type {value_type.__name__}"
    )


def _normalize_canonical_plain(
    value: object, *, allow_tuple: bool = True, path: str = "value",
    max_total_utf8: int = _SNAPSHOT_MAX_BYTES,
) -> object:
    """Return a detached canonical JSON value under one bounded policy."""
    if type(max_total_utf8) is not int or max_total_utf8 < 0:
        raise MergeCommitReceiptError("canonical UTF-8 budget is invalid")
    state = {"nodes": 0, "utf8": 0}
    active: set[int] = set()

    def charge_utf8(size: int) -> None:
        if state["utf8"] > max_total_utf8 - size:
            raise MergeCommitReceiptError(
                "canonical value exceeds total UTF-8 limit"
            )
        state["utf8"] += size

    def normalize(item: object, *, item_path: str, depth: int) -> object:
        if depth > _CANONICAL_MAX_DEPTH:
            raise MergeCommitReceiptError(
                f"{item_path} exceeds maximum nesting depth"
            )
        state["nodes"] += 1
        if state["nodes"] > _CANONICAL_MAX_NODES:
            raise MergeCommitReceiptError("canonical value exceeds node limit")

        item_type = type(item)
        if item is None or item_type is bool or item_type is int:
            return item
        if item_type is str:
            encoded_size = len(item.encode("utf-8"))
            if encoded_size > _CANONICAL_MAX_STRING_BYTES:
                raise MergeCommitReceiptError(
                    f"{item_path} exceeds maximum string size"
                )
            charge_utf8(encoded_size)
            return item
        if item_type not in (list, tuple, dict):
            raise MergeCommitReceiptError(
                f"{item_path} contains unsupported value type {item_type.__name__}"
            )
        if item_type is tuple and not allow_tuple:
            raise MergeCommitReceiptError(
                f"{item_path} must use an exact list, not tuple"
            )
        if len(item) > _CANONICAL_MAX_CONTAINER_ITEMS:
            raise MergeCommitReceiptError(
                f"{item_path} exceeds maximum container size"
            )
        identity = id(item)
        if identity in active:
            raise MergeCommitReceiptError(f"{item_path} contains a cycle")
        active.add(identity)
        try:
            if item_type in (list, tuple):
                return [
                    normalize(
                        child, item_path=f"{item_path}[{index}]",
                        depth=depth + 1,
                    )
                    for index, child in enumerate(item)
                ]
            if any(type(key) is not str for key in item):
                raise MergeCommitReceiptError(
                    f"{item_path} keys must be exact strings"
                )
            for key in item:
                key_size = len(key.encode("utf-8"))
                if key_size > _CANONICAL_MAX_STRING_BYTES:
                    raise MergeCommitReceiptError(
                        f"{item_path} contains an oversized key"
                    )
                charge_utf8(key_size)
            return {
                key: normalize(
                    item[key], item_path=f"{item_path}.{key}",
                    depth=depth + 1,
                )
                for key in sorted(item)
            }
        finally:
            active.remove(identity)

    return normalize(value, item_path=path, depth=0)


def _canonical_plain(value: object) -> object:
    return _normalize_canonical_plain(
        value, path="signed_fields", max_total_utf8=_RECEIPT_MAX_BYTES,
    )


def _encode(value: object, *, max_bytes: int) -> bytes:
    if type(max_bytes) is not int or max_bytes < 0:
        raise MergeCommitReceiptError("encoded JSON budget is invalid")
    _guard_integer_materialization(value, max_bytes=max_bytes)
    encoder = json.JSONEncoder(
        ensure_ascii=False, separators=(",", ":"), sort_keys=True,
    )
    chunks: list[bytes] = []
    size = 0
    for text in encoder.iterencode(value):
        encoded = text.encode("utf-8")
        if size > max_bytes - len(encoded):
            raise MergeCommitReceiptError("encoded JSON exceeds byte limit")
        chunks.append(encoded)
        size += len(encoded)
    return b"".join(chunks)


def _guard_integer_materialization(value: object, *, max_bytes: int) -> None:
    remaining = max_bytes
    active: set[int] = set()

    def visit(item: object) -> None:
        nonlocal remaining
        item_type = type(item)
        if item_type is int:
            bits = abs(item).bit_length()
            digits_upper_bound = max(1, (bits * 30103 + 99999) // 100000)
            if item < 0:
                digits_upper_bound += 1
            if digits_upper_bound > remaining:
                raise MergeCommitReceiptError(
                    "integer cannot fit encoded JSON budget"
                )
            remaining -= digits_upper_bound
            return
        if item_type in (list, tuple, dict):
            identity = id(item)
            if identity in active:
                raise MergeCommitReceiptError("encoded JSON contains a cycle")
            active.add(identity)
            try:
                children = item.values() if item_type is dict else item
                for child in children:
                    visit(child)
            finally:
                active.remove(identity)

    visit(value)


def _parse_utc(value: str, field: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MergeCommitReceiptError(f"{field} must be UTC ending in Z")
    try:
        return dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise MergeCommitReceiptError(f"{field} must be ISO-8601 UTC") from exc


def _revision_number(revision: str, project_id: str) -> int:
    prefix = f"{project_id}-R"
    suffix = revision[len(prefix):] if revision.startswith(prefix) else ""
    if len(suffix) < 4 or not suffix.isdigit():
        raise MergeCommitReceiptError("revision does not match project format")
    return int(suffix)


__all__ = [
    "BASELINE_DIGEST_ALGORITHM", "BASELINE_SCHEMA", "FrozenBaselineSnapshot",
    "MergeCommitReceipt", "MergeCommitReceiptDuplicateError",
    "MergeCommitReceiptError", "MergeCommitReceiptStore",
    "ReceiptSigningAuthority", "append_signed_receipt",
    "build_signed_merge_commit_receipt", "canonical_baseline_digest",
    "freeze_baseline", "verify_signed_receipt",
]
