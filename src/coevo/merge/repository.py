"""SQLite receipt history protected by signed monotonic freshness anchors."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# SQLite 收据历史 + 签名单调新鲜度锚：流式逐行校验，防超大/畸形行。
from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

from src.coevo.identity.audit_anchor import (
    AuditAnchorError, FreshnessAuthority, SignedAuditAnchor, Signer,
    WindowsCertificateSigner, WindowsFreshnessAuthority,
)
from src.coevo.report import ReportStatus
from src.coevo.task_decomposition import (
    Deliverable, DependencyEdge, Milestone, ProjectBaseline, Task, WorkPackage,
)
from src.coevo.task_decomposition.models import Override

from .receipt import (
    FrozenBaselineSnapshot, MergeCommitReceipt, MergeCommitReceiptError,
    MergeCommitReceiptStore, ReceiptSigningAuthority, append_signed_receipt,
    _RECEIPT_MAX_BYTES, _SNAPSHOT_BASE64_MAX_CHARS, _SNAPSHOT_MAX_BYTES,
    _normalize_canonical_plain, freeze_baseline, verify_signed_receipt,
)


# Row-level guards (US-11-AC-1 Round-2 fix: defense in depth against oversized
# or malformed stored columns BEFORE the SQL cursor materialises a single
# row and BEFORE Python json.loads / base64.b64decode touch any byte).
#
# These constants intentionally mirror / narrow the receipt-domain limits.
# Any byte that survives the SQL cursor must pass these tests before the
# repository trusts the column for downstream processing.
_ROW_PAYLOAD_MAX_BYTES = _RECEIPT_MAX_BYTES          # <= 4 MiB
_ROW_SIGNATURE_MAX_BYTES = 1024                       # RSA-2048/3072/4096 SIG
_ROW_SIGNATURE_MIN_BYTES = 1                          # non-empty
_ROW_RECEIPT_ID_PREFIX = "mcr."
_ROW_RECEIPT_ID_HEX_LEN = 64
_ROW_RECEIPT_ID_MAX_LEN = (
    len(_ROW_RECEIPT_ID_PREFIX) + _ROW_RECEIPT_ID_HEX_LEN
)
_ROW_HASH_HEX_LEN = 64
_ROW_PROJECTION = "store_sequence,receipt_id,payload,signature,receipt_hash"



class MergeReceiptRepositoryError(MergeCommitReceiptError):
    pass


class MergeReceiptRepositoryRecoveryRequired(RuntimeError):
    """The database commit succeeded but its prepared anchor needs recovery."""

    def __init__(self, receipt_id: str) -> None:
        super().__init__(
            f"receipt {receipt_id} committed; repository reopen/recovery is required"
        )
        self.receipt_id = receipt_id


class MergeReceiptRepository:
    """Controlled verification-only repository; every read revalidates history."""

    @classmethod
    def create(
        cls, database: str | Path, verification_authority: ReceiptSigningAuthority,
        signer: Signer | None = None, freshness: FreshnessAuthority | None = None,
    ) -> "MergeReceiptRepository":
        return cls(database, verification_authority, signer, freshness, create=True)

    @classmethod
    def open(
        cls, database: str | Path, verification_authority: ReceiptSigningAuthority,
        signer: Signer | None = None, freshness: FreshnessAuthority | None = None,
    ) -> "MergeReceiptRepository":
        return cls(database, verification_authority, signer, freshness, create=False)

    def __init__(
        self, database: str | Path, verification_authority: ReceiptSigningAuthority,
        signer: Signer | None, freshness: FreshnessAuthority | None, *, create: bool,
    ) -> None:
        if type(verification_authority) is not ReceiptSigningAuthority:
            raise MergeReceiptRepositoryError("verification authority is required")
        self.database = Path(database).resolve()
        self._authority = verification_authority
        self.anchor = SignedAuditAnchor(
            self.database, signer or WindowsCertificateSigner(),
            freshness or WindowsFreshnessAuthority(),
        )
        if create:
            if self.database.exists() or any(item.exists() for item in self.anchor.artifacts()):
                raise AuditAnchorError("refusing to create receipt store over existing state")
            target, uri = str(self.database), False
        else:
            if not self.database.is_file():
                raise AuditAnchorError("receipt store does not exist")
            target, uri = f"file:{self.database.as_posix()}?mode=rw", True
        self.connection = sqlite3.connect(
            target, isolation_level=None, uri=uri, check_same_thread=False,
        )
        self.connection.row_factory = sqlite3.Row
        try:
            if create:
                self.connection.executescript(
                    Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
                )
                self.connection.execute(
                    "INSERT INTO merge_metadata VALUES(1,?,'1.0')", (str(uuid.uuid4()),)
                )
                with self.anchor.locked():
                    self.anchor.prepare(self._checkpoint())
                    self.anchor.promote()
            else:
                self._validate_schema()
                with self.anchor.locked():
                    self.anchor.recover(self._checkpoint())
        except Exception:
            self.connection.close()
            if create:
                self._cleanup_failed_create()
            raise

    @property
    def store_id(self) -> str:
        return self.connection.execute(
            "SELECT store_id FROM merge_metadata WHERE singleton=1"
        ).fetchone()[0]

    def close(self) -> None:
        self.connection.close()

    def _cleanup_failed_create(self) -> None:
        try:
            if self.anchor.pending_head.exists():
                self.anchor.abort_pending()
        except Exception:
            pass
        for item in self.anchor.artifacts():
            item.unlink(missing_ok=True)
        self.database.unlink(missing_ok=True)

    def _validate_schema(self) -> None:
        tables = {
            row[0] for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if not {"merge_metadata", "merge_receipts"}.issubset(tables):
            raise MergeReceiptRepositoryError("receipt store schema is incomplete")
        metadata = self.connection.execute(
            "SELECT schema_version FROM merge_metadata WHERE singleton=1"
        ).fetchone()
        if metadata is None or metadata[0] != "1.0":
            raise MergeReceiptRepositoryError("receipt store schema is unsupported")

    def _checkpoint(self) -> dict[str, object]:
        tail = self.connection.execute(
            "SELECT store_sequence,receipt_id,receipt_hash FROM merge_receipts "
            "ORDER BY store_sequence DESC LIMIT 1"
        ).fetchone()
        count = self.connection.execute("SELECT COUNT(*) FROM merge_receipts").fetchone()[0]
        return {
            "store_id": self.store_id,
            "database_schema_version": "1.0",
            "receipt_count": count,
            "store_sequence": tail["store_sequence"] if tail else 0,
            "receipt_id": tail["receipt_id"] if tail else None,
            "receipt_hash": tail["receipt_hash"] if tail else "0" * 64,
        }

    def _abort_if_pending(self) -> None:
        if self.anchor.pending_head.exists():
            self.anchor.abort_pending()

    def _recover(self) -> None:
        self.anchor.recover(self._checkpoint())
        if not self.anchor.verify(self._checkpoint()):
            raise MergeReceiptRepositoryError("receipt store checkpoint is invalid")

    def commit(
        self, builder: Callable[[str, int, str | None, str], MergeCommitReceipt],
        *, trusted_time: datetime,
    ) -> MergeCommitReceipt:
        """Commit a signed receipt after full verification."""
        with self.anchor.locked():
            self._recover()
            self.connection.execute("BEGIN IMMEDIATE")
            committed = False
            try:
                history = self._iter_verified_history(trusted_time)
                rows = list(history)
                current_view = MergeCommitReceiptStore.empty()
                for historical in history:
                    current_view = append_signed_receipt(current_view, historical)
                tail_receipt = history[-1] if history else None
                sequence = (
                    tail_receipt.store_sequence + 1
                ) if tail_receipt else 1
                previous_id = (
                    tail_receipt.receipt_id if tail_receipt else None
                )
                previous_hash = (
                    hashlib.sha256(
                        tail_receipt.payload + tail_receipt.signature,
                    ).hexdigest() if tail_receipt else "0" * 64
                )
                receipt = builder(self.store_id, sequence, previous_id, previous_hash)
                if (
                    type(receipt) is not MergeCommitReceipt
                    or receipt.store_id != self.store_id
                    or receipt.store_sequence != sequence
                    or receipt.previous_receipt_id != previous_id
                    or receipt.previous_receipt_hash != previous_hash
                ):
                    raise MergeReceiptRepositoryError("builder returned an unbound receipt")
                verify_signed_receipt(
                    receipt, authority=self._authority, trusted_time=trusted_time,
                )
                candidate_view = append_signed_receipt(current_view, receipt)
                if len(candidate_view) != len(rows) + 1:
                    raise MergeReceiptRepositoryError(
                        "candidate receipt did not advance the current view"
                    )
                receipt_hash = hashlib.sha256(receipt.payload + receipt.signature).hexdigest()
                self.connection.execute(
                    "INSERT INTO merge_receipts VALUES(?,?,?,?,?,?,?,?)",
                    (
                        sequence, receipt.receipt_id, receipt.package_id,
                        receipt.package_digest, receipt.project_id,
                        receipt.payload, receipt.signature, receipt_hash,
                    ),
                )
                persisted = self.connection.execute(
                    "SELECT COUNT(*) AS count,MAX(store_sequence) AS head "
                    "FROM merge_receipts"
                ).fetchone()
                persisted_head = self.connection.execute(
                    "SELECT receipt_id,receipt_hash FROM merge_receipts "
                    "WHERE store_sequence=?", (sequence,),
                ).fetchone()
                if (
                    persisted["count"] != len(rows) + 1
                    or persisted["head"] != sequence
                    or persisted_head is None
                    or persisted_head["receipt_id"] != receipt.receipt_id
                    or persisted_head["receipt_hash"] != receipt_hash
                ):
                    raise MergeReceiptRepositoryError(
                        "receipt insert did not produce the expected head"
                    )
                self.anchor.prepare(self._checkpoint())
                self.connection.commit()
                committed = True
                try:
                    self.anchor.promote()
                except Exception as exc:
                    raise MergeReceiptRepositoryRecoveryRequired(
                        receipt.receipt_id
                    ) from exc
                return receipt
            except MergeReceiptRepositoryRecoveryRequired:
                raise
            except Exception as exc:
                if not committed and self.connection.in_transaction:
                    self.connection.rollback()
                    self._abort_if_pending()
                if isinstance(exc, sqlite3.IntegrityError):
                    raise MergeReceiptRepositoryError(
                        "receipt identity was already committed"
                    ) from exc
                raise

    def get_verified(
        self, receipt_id: str, *, trusted_time: datetime,
    ) -> MergeCommitReceipt:
        """Fetch and verify a receipt by id."""
        with self.anchor.locked():
            self._recover()
            receipts = self._verify_history(trusted_time)
        for receipt in receipts:
            if receipt.receipt_id == receipt_id:
                return receipt
        raise MergeReceiptRepositoryError("receipt is absent")

    def verified_history(self, *, trusted_time: datetime) -> tuple[MergeCommitReceipt, ...]:
        with self.anchor.locked():
            self._recover()
            return self._verify_history(trusted_time)

    def _verify_history(self, trusted_time: datetime) -> tuple[MergeCommitReceipt, ...]:
        return self._iter_verified_history(trusted_time)

    def _iter_verified_history(
        self, trusted_time: datetime,
    ) -> tuple[MergeCommitReceipt, ...]:
        """Stream rows through the SQL cursor one at a time.

        Defense in depth (US-11-AC-1 Round-2 fix): we NEVER use
        ``fetchall`` against ``merge_receipts``. Each row is read
        through the DB-API cursor, validated against the row-level
        size / type / format guards, and only THEN handed to the
        per-row verifier. A single oversized or malformed row is
        rejected before any subsequent row is materialised.
        """
        cursor = self.connection.execute(
            "SELECT " + _ROW_PROJECTION +
            " FROM merge_receipts ORDER BY store_sequence"
        )
        try:
            receipts: list[MergeCommitReceipt] = []
            previous_id = None
            previous_hash = "0" * 64
            expected_sequence = 0
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                expected_sequence += 1
                _validate_row_shape(row)
                receipt = _decode_receipt(
                    row["receipt_id"], row["payload"], row["signature"],
                )
                if (
                    row["store_sequence"] != expected_sequence
                    or receipt.store_sequence != expected_sequence
                    or receipt.store_id != self.store_id
                    or receipt.previous_receipt_id != previous_id
                    or receipt.previous_receipt_hash != previous_hash
                ):
                    raise MergeReceiptRepositoryError(
                        "receipt history chain is invalid"
                    )
                verify_signed_receipt(
                    receipt, authority=self._authority, trusted_time=trusted_time,
                )
                computed = hashlib.sha256(
                    receipt.payload + receipt.signature
                ).hexdigest()
                if computed != row["receipt_hash"]:
                    raise MergeReceiptRepositoryError(
                        "receipt row hash is invalid"
                    )
                receipts.append(receipt)
                previous_id, previous_hash = receipt.receipt_id, computed
            return tuple(receipts)
        finally:
            cursor.close()




def _validate_row_shape(row: sqlite3.Row) -> None:
    """Reject oversized or malformed stored columns BEFORE parse/decode.

    Invariants (US-11-AC-1 Round-2 fix):

    * ``store_sequence`` must be a positive exact int.
    * ``receipt_id`` must be ``str`` of length <= _ROW_RECEIPT_ID_MAX_LEN
      and exactly equal to ``mcr.`` + 64 lowercase hex chars.
    * ``payload`` must be ``bytes`` of length in
      (0, _ROW_PAYLOAD_MAX_BYTES].
    * ``signature`` must be ``bytes`` of length in
      [_ROW_SIGNATURE_MIN_BYTES, _ROW_SIGNATURE_MAX_BYTES].
    * ``receipt_hash`` must be ``str`` of length _ROW_HASH_HEX_LEN
      holding exactly 64 lowercase hex chars.

    These are the FIRST checks performed on every row the SQL
    cursor returns. Anything that fails one of them is rejected
    before json.loads / base64.b64decode / SHA-256 ever run.
    """
    try:
        store_sequence = row["store_sequence"]
        receipt_id = row["receipt_id"]
        payload = row["payload"]
        signature = row["signature"]
        receipt_hash = row["receipt_hash"]
    except (IndexError, KeyError, TypeError) as exc:
        raise MergeReceiptRepositoryError(
            "stored receipt row is missing a required column"
        ) from exc
    if type(store_sequence) is not int or store_sequence < 1:
        raise MergeReceiptRepositoryError(
            "stored receipt sequence is not a positive integer"
        )
    if (
        type(receipt_id) is not str
        or not receipt_id
        or len(receipt_id) > _ROW_RECEIPT_ID_MAX_LEN
        or not receipt_id.startswith(_ROW_RECEIPT_ID_PREFIX)
    ):
        raise MergeReceiptRepositoryError(
            "stored receipt_id has an invalid prefix or length"
        )
    hex_part = receipt_id[len(_ROW_RECEIPT_ID_PREFIX):]
    if (
        len(hex_part) != _ROW_RECEIPT_ID_HEX_LEN
        or not all("0" <= ch <= "9" or "a" <= ch <= "f" for ch in hex_part)
    ):
        raise MergeReceiptRepositoryError(
            "stored receipt_id is not 64 lowercase hex chars"
        )
    if (
        type(payload) is not bytes
        or not payload
        or len(payload) > _ROW_PAYLOAD_MAX_BYTES
    ):
        raise MergeReceiptRepositoryError(
            "stored receipt payload is missing, oversized, or not bytes"
        )
    if (
        type(signature) is not bytes
        or len(signature) < _ROW_SIGNATURE_MIN_BYTES
        or len(signature) > _ROW_SIGNATURE_MAX_BYTES
    ):
        raise MergeReceiptRepositoryError(
            "stored receipt signature has an invalid length or type"
        )
    if (
        type(receipt_hash) is not str
        or len(receipt_hash) != _ROW_HASH_HEX_LEN
        or not all("0" <= ch <= "9" or "a" <= ch <= "f" for ch in receipt_hash)
    ):
        raise MergeReceiptRepositoryError(
            "stored receipt_hash is not 64 lowercase hex chars"
        )


def _decode_receipt(receipt_id: str, payload: bytes, signature: bytes) -> MergeCommitReceipt:
    try:
        # Row-level precheck (US-11-AC-1 Round-2 fix). The strict
        # receipt_id / signature / hash format is enforced at the
        # SQL boundary by :func:`_validate_row_shape`; here we only
        # re-confirm the column types and the size cap so that one
        # malformed or oversized column cannot DoS the decode path
        # even when the function is invoked directly by tests.
        if type(receipt_id) is not str or not receipt_id:
            raise MergeReceiptRepositoryError("stored receipt_id is not a string")
        if (
            type(signature) is not bytes
            or len(signature) < _ROW_SIGNATURE_MIN_BYTES
            or len(signature) > _ROW_SIGNATURE_MAX_BYTES
        ):
            raise MergeReceiptRepositoryError(
                "stored receipt signature has an invalid length or type"
            )
        if type(payload) is not bytes or not payload or len(payload) > _RECEIPT_MAX_BYTES:
            raise MergeReceiptRepositoryError("stored receipt payload is missing or oversized")
        item = json.loads(payload)
        if type(item) is not dict:
            raise MergeReceiptRepositoryError("stored receipt must be an exact object")
        snapshot_base64 = item["snapshot_payload_base64"]
        if (
            type(snapshot_base64) is not str
            or len(snapshot_base64) > _SNAPSHOT_BASE64_MAX_CHARS
            or len(snapshot_base64) % 4 != 0
            or not snapshot_base64.isascii()
        ):
            raise MergeReceiptRepositoryError(
                "stored snapshot encoding is invalid or oversized"
            )
        padding = len(snapshot_base64) - len(snapshot_base64.rstrip("="))
        if padding > 2 or "=" in snapshot_base64[:-padding or None]:
            raise MergeReceiptRepositoryError("stored snapshot padding is invalid")
        decoded_bound = (len(snapshot_base64) // 4) * 3 - padding
        if decoded_bound > _SNAPSHOT_MAX_BYTES:
            raise MergeReceiptRepositoryError("stored snapshot is oversized")
        snapshot_payload = base64.b64decode(snapshot_base64, validate=True)
        if type(snapshot_payload) is not bytes or len(snapshot_payload) > _SNAPSHOT_MAX_BYTES:
            raise MergeReceiptRepositoryError("decoded snapshot is oversized")
        snapshot_item = json.loads(snapshot_payload)
        baseline = _decode_baseline(snapshot_item["baseline"])
        if freeze_baseline(baseline).payload != snapshot_payload:
            raise MergeReceiptRepositoryError(
                "decoded baseline does not reproduce signed snapshot bytes"
            )
        snapshot = FrozenBaselineSnapshot(
            baseline=baseline, payload=snapshot_payload,
            digest=hashlib.sha256(snapshot_payload).hexdigest(),
        )
        values = dict(item)
        for name in (
            "domain", "schema_version", "snapshot_domain",
            "snapshot_schema_version", "snapshot_payload_base64",
        ):
            values.pop(name)
        values["report_status"] = ReportStatus(values["report_status"])
        return MergeCommitReceipt(
            receipt_id=receipt_id, payload=payload, signature=bytes(signature),
            snapshot=snapshot, **values,
        )
    except Exception as exc:
        raise MergeReceiptRepositoryError("stored receipt cannot be decoded") from exc


def _decode_baseline(value: dict) -> ProjectBaseline:
    baseline_keys = {
        "project_id", "version", "created_at", "title", "process_flow_ref",
        "objective", "plan_start", "plan_end", "responsible_units",
        "work_packages", "dependencies", "milestones", "overrides",
    }
    _require_exact_mapping(value, baseline_keys, "baseline")
    if type(value["overrides"]) is not list:
        raise MergeReceiptRepositoryError("baseline.overrides must be an exact list")
    overrides = tuple(
        _decode_override(item, index=index)
        for index, item in enumerate(value["overrides"])
    )
    packages = tuple(
        WorkPackage(
            item["work_package_id"], item["standard_stage"], item["title"],
            tuple(
                Task(
                    task["task_id"], task["title"], task["responsible_role"],
                    task["plan_start"], task["plan_end"],
                    tuple(
                        Deliverable(
                            deliverable["deliverable_id"], deliverable["title"],
                            deliverable["kind"],
                            tuple(deliverable["acceptance_criteria"]),
                        )
                        for deliverable in task["deliverables"]
                    ),
                )
                for task in item["tasks"]
            ),
        )
        for item in value["work_packages"]
    )
    return ProjectBaseline(
        project_id=value["project_id"], version=value["version"],
        created_at=value["created_at"], title=value["title"],
        process_flow_ref=tuple(value["process_flow_ref"]),
        objective=value["objective"], plan_start=value["plan_start"],
        plan_end=value["plan_end"],
        responsible_units=tuple(value["responsible_units"]),
        work_packages=packages,
        dependencies=tuple(
            DependencyEdge(
                item["predecessor_task_id"], item["successor_task_id"], item["kind"]
            )
            for item in value["dependencies"]
        ),
        milestones=tuple(
            Milestone(
                item["milestone_id"], item["title"], item["target_date"],
                item["work_package_id"],
            )
            for item in value["milestones"]
        ),
        overrides=overrides,
    )


def _decode_override(value: object, *, index: int) -> Override:
    path = f"baseline.overrides[{index}]"
    _require_exact_mapping(
        value, {"target_path", "original_value", "edited_value", "reason"}, path,
    )
    target_path = value["target_path"]
    reason = value["reason"]
    if type(target_path) is not str or not target_path:
        raise MergeReceiptRepositoryError(f"{path}.target_path must be a non-empty exact string")
    if type(reason) is not str or not reason:
        raise MergeReceiptRepositoryError(f"{path}.reason must be a non-empty exact string")
    return Override(
        target_path=target_path,
        original_value=_normalize_canonical_plain(
            value["original_value"], allow_tuple=False,
            path=f"{path}.original_value",
        ),
        edited_value=_normalize_canonical_plain(
            value["edited_value"], allow_tuple=False,
            path=f"{path}.edited_value",
        ),
        reason=reason,
    )


def _require_exact_mapping(value: object, keys: set[str], path: str) -> None:
    if type(value) is not dict:
        raise MergeReceiptRepositoryError(f"{path} must be an exact object")
    if set(value) != keys or any(type(key) is not str for key in value):
        raise MergeReceiptRepositoryError(f"{path} fields are not exact")


__all__ = [
    "MergeReceiptRepository", "MergeReceiptRepositoryError",
    "MergeReceiptRepositoryRecoveryRequired",
]
