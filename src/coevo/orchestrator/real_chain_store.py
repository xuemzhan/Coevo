"""SQLite-backed idempotency and hash-chain audit store for real orchestration."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 真实编排链 SQLite 幂等与哈希链审计存储：事务化、锚点恢复、失败关闭。
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..identity.audit_anchor import (
    AuditAnchorError,
    FreshnessAuthority,
    SignedAuditAnchor,
    Signer,
    WindowsCertificateSigner,
    WindowsFreshnessAuthority,
)


class RealChainStoreError(Exception):
    pass


class RealChainStoreRecoveryRequired(RealChainStoreError):
    """The SQLite commit succeeded but its signed anchor was not promoted."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"real-chain store recovery is required for {event_id}")
        self.event_id = event_id


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize ``value`` to canonical JSON bytes with strict type checks."""
    def validate(item: Any, path: str) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            return
        if isinstance(item, float):
            if not math.isfinite(item):
                raise RealChainStoreError(f"non-finite float at {path}")
            return
        if isinstance(item, list):
            for index, child in enumerate(item):
                validate(child, f"{path}[{index}]")
            return
        if isinstance(item, dict) and all(isinstance(key, str) for key in item):
            for key, child in item.items():
                validate(child, f"{path}.{key}")
            return
        raise RealChainStoreError(f"non-JSON value at {path}")
    validate(value, "$")
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise RealChainStoreError("value cannot be canonicalized") from exc


def canonical_digest(value: Any) -> str:
    """Return the SHA-256 hex digest of the canonical JSON form of ``value``."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class RealChainAuditEntry:
    sequence: int
    event_id: str
    action: str
    result: str
    payload_digest: str
    recorded_at: str
    previous_hash: str
    entry_hash: str


@dataclass(frozen=True)
class RecoveryContext:
    event_id: str
    event_digest: str
    project_id: str
    state: str


def _snapshot(outcome: Any) -> str:
    if outcome is None:
        return ""
    report = outcome.orch_report
    preview = dataclasses.asdict(outcome.package_preview) if outcome.package_preview else None
    payload = {
        "chain_id": outcome.chain_id,
        "event_id": outcome.event_id,
        "workspace_project_id": outcome.workspace_project_id,
        "flow": list(outcome.flow_understanding_summary),
        "baseline": list(outcome.baseline_summary),
        "recommendation": list(outcome.recommendation_summary),
        "package": list(outcome.package_summary),
        "event_digest": outcome.event_digest,
        "project_input_digest": outcome.project_input_digest,
        "confirmation_digest": outcome.confirmation_digest,
        "store_id": outcome.store_id,
        "package_preview": preview,
        "report": {
            "trace_id": report.trace_id,
            "chain_id": report.chain_id,
            "event_id": report.event_id,
            "workspace_project_id": report.workspace_project_id,
            "outcome": report.outcome.value,
            "completed_at": report.completed_at,
            "execution_mode": report.execution_mode,
            "trace": [{
                "trace_id": item.trace_id,
                "step_index": item.step_index,
                "agent_id": item.agent_id,
                "result": item.result.value,
                "requires_human_confirmation": item.requires_human_confirmation,
                "confirmed_by": item.confirmed_by,
                "detail": item.detail,
                "recorded_at": item.recorded_at,
            } for item in report.trace],
        },
    }
    return canonical_json_bytes(payload).decode("utf-8")


def _restore(text: str) -> Any:
    if not text:
        return None
    from . import (
        OrchestrationOutcome, OrchestrationReport, OrchestrationStepResult,
        OrchestrationTrace,
    )
    from ._real_chain import PackagePreview, RealChainOutcome
    value = json.loads(text)
    report_value = value["report"]
    traces = tuple(OrchestrationTrace(
        item["trace_id"], item["step_index"], item["agent_id"],
        OrchestrationStepResult(item["result"]), item["requires_human_confirmation"],
        item["confirmed_by"], item["detail"], item["recorded_at"],
    ) for item in report_value["trace"])
    report = OrchestrationReport(
        report_value["trace_id"], report_value["chain_id"], report_value["event_id"],
        report_value["workspace_project_id"], OrchestrationOutcome(report_value["outcome"]),
        traces, report_value["completed_at"], report_value["execution_mode"],
    )
    preview = PackagePreview(**value["package_preview"]) if value["package_preview"] else None
    return RealChainOutcome(
        value["chain_id"], value["event_id"], value["workspace_project_id"],
        tuple(value["flow"]), tuple(value["baseline"]), tuple(value["recommendation"]),
        tuple(value["package"]), report, value["event_digest"],
        value["project_input_digest"], value["confirmation_digest"], preview,
        value.get("store_id", ""),
    )


class RealChainStore:
    """Signed, rollback-resistant real-chain state and audit repository."""

    _SCHEMA_VERSION = "1.0"
    _CONSTRUCTION_TOKEN = object()
    _SCHEMA_SQL = """
        CREATE TABLE real_chain_records(
            event_id TEXT PRIMARY KEY, event_digest TEXT NOT NULL,
            project_id TEXT NOT NULL, state TEXT NOT NULL,
            held_snapshot TEXT NOT NULL DEFAULT '', confirmation_digest TEXT NOT NULL DEFAULT '',
            confirmed_snapshot TEXT NOT NULL DEFAULT '', resume_digest TEXT NOT NULL DEFAULT '',
            completed_snapshot TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE real_chain_audit(
            sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL,
            action TEXT NOT NULL, result TEXT NOT NULL, payload_digest TEXT NOT NULL,
            recorded_at TEXT NOT NULL, previous_hash TEXT NOT NULL, entry_hash TEXT NOT NULL
        );
        CREATE TABLE real_chain_metadata(
            singleton INTEGER PRIMARY KEY CHECK(singleton=1), store_id TEXT NOT NULL,
            schema_version TEXT NOT NULL
        );
    """

    @classmethod
    def create(
        cls, database: str | Path, *, signer: Signer | None = None,
        freshness: FreshnessAuthority | None = None,
    ) -> "RealChainStore":
        """Create a new real-chain store."""
        return cls(
            database, signer=signer, freshness=freshness, create=True,
            _token=cls._CONSTRUCTION_TOKEN,
        )

    @classmethod
    def open(
        cls, database: str | Path, *, signer: Signer | None = None,
        freshness: FreshnessAuthority | None = None,
    ) -> "RealChainStore":
        """Open an existing real-chain store."""
        return cls(
            database, signer=signer, freshness=freshness, create=False,
            _token=cls._CONSTRUCTION_TOKEN,
        )

    def __init__(
        self, database: str | Path, *, signer: Signer | None = None,
        freshness: FreshnessAuthority | None = None, create: bool = False,
        _token: object | None = None,
    ) -> None:
        if _token is not self._CONSTRUCTION_TOKEN:
            raise RealChainStoreError("use RealChainStore.create or RealChainStore.open")
        self._lock = threading.RLock()
        self._recovery_required = False
        self.database = Path(database).resolve()
        self.database_path = str(self.database)
        self.anchor = SignedAuditAnchor(
            self.database, signer or WindowsCertificateSigner(),
            freshness or WindowsFreshnessAuthority(),
        )
        if create:
            if self.database.exists() or any(path.exists() for path in self.anchor.artifacts()):
                raise AuditAnchorError("refusing to create real-chain store over existing state")
            target, uri = str(self.database), False
        else:
            if not self.database.is_file():
                raise AuditAnchorError("real-chain store does not exist")
            target, uri = f"file:{self.database.as_posix()}?mode=rw", True
        self.connection = sqlite3.connect(
            target, isolation_level=None, uri=uri, check_same_thread=False,
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        try:
            if create:
                self._create_schema()
                with self._guard():
                    self.connection.execute("BEGIN IMMEDIATE")
                    try:
                        self.connection.execute(
                            "INSERT INTO real_chain_metadata(singleton,store_id,schema_version) "
                            "VALUES(1,?,?)", (str(uuid.uuid4()), self._SCHEMA_VERSION),
                        )
                        self._validate_schema()
                        self._verify_audit_chain_unlocked()
                        self.anchor.prepare(self._checkpoint())
                        self.connection.commit()
                        self.anchor.promote()
                    except Exception:
                        if self.connection.in_transaction:
                            self.connection.rollback()
                        raise
            else:
                self._open_validate()
                self._mark_interrupted_for_recovery()
        except Exception:
            self.connection.close()
            if create:
                self._cleanup_failed_create()
            raise

    def _create_schema(self) -> None:
        self.connection.executescript(self._SCHEMA_SQL)

    def _cleanup_failed_create(self) -> None:
        try:
            if self.anchor.pending_head.exists():
                self.anchor.abort_pending()
        except Exception:
            pass
        for path in self.anchor.artifacts():
            path.unlink(missing_ok=True)
        self.database.unlink(missing_ok=True)

    @contextmanager
    def _guard(self):
        with self._lock:
            with self.anchor.locked():
                yield

    @staticmethod
    def _schema_projection_for(connection: sqlite3.Connection) -> dict[str, object]:
        master = [
            dict(row) for row in connection.execute(
                "SELECT type,name,tbl_name,sql FROM sqlite_master "
                "ORDER BY type,name,tbl_name"
            )
        ]
        # The trusted projection intentionally contains sqlite_sequence and
        # SQLite-owned auto-index rows. Exact equality therefore permits only
        # those engine objects produced by _SCHEMA_SQL, not arbitrary sqlite_*
        # objects or user-created tables, views, triggers, or indexes.
        temporary_master = [
            dict(row) for row in connection.execute(
                "SELECT type,name,tbl_name,sql FROM sqlite_temp_master "
                "ORDER BY type,name,tbl_name"
            )
        ]
        tables: dict[str, object] = {}
        for item in master:
            if item["type"] != "table":
                continue
            name = item["name"]
            columns = [dict(row) for row in connection.execute(
                "SELECT cid,name,type,\"notnull\",dflt_value,pk,hidden "
                "FROM pragma_table_xinfo(?) ORDER BY cid", (name,),
            )]
            indexes = []
            for index in connection.execute(
                "SELECT seq,name,\"unique\",origin,partial FROM pragma_index_list(?) "
                "ORDER BY seq,name", (name,),
            ):
                index_item = dict(index)
                index_item["columns"] = [dict(row) for row in connection.execute(
                    "SELECT seqno,cid,name,desc,coll,key FROM pragma_index_xinfo(?) "
                    "ORDER BY seqno", (index["name"],),
                )]
                indexes.append(index_item)
            foreign_keys = [dict(row) for row in connection.execute(
                "SELECT id,seq,\"table\",\"from\",\"to\",on_update,on_delete,match "
                "FROM pragma_foreign_key_list(?) ORDER BY id,seq", (name,),
            )]
            tables[name] = {
                "table_xinfo": columns,
                "index_list": indexes,
                "foreign_key_list": foreign_keys,
            }
        return {
            "sqlite_master": master,
            "sqlite_temp_master": temporary_master,
            "tables": tables,
        }

    @classmethod
    def _trusted_schema_projection(cls) -> dict[str, object]:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        try:
            connection.executescript(cls._SCHEMA_SQL)
            return cls._schema_projection_for(connection)
        finally:
            connection.close()

    def _schema_projection(self) -> dict[str, object]:
        return self._schema_projection_for(self.connection)

    def _validate_schema(self) -> None:
        if self._schema_projection() != self._trusted_schema_projection():
            raise RealChainStoreError("real-chain store schema is not trusted")
        metadata = self.connection.execute(
            "SELECT store_id,schema_version FROM real_chain_metadata WHERE singleton=1"
        ).fetchone()
        if (
            metadata is None or metadata["schema_version"] != self._SCHEMA_VERSION
            or not isinstance(metadata["store_id"], str) or not metadata["store_id"]
        ):
            raise RealChainStoreError("real-chain store metadata is invalid")

    def _store_id_unlocked(self) -> str:
        row = self.connection.execute(
            "SELECT store_id FROM real_chain_metadata WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RealChainStoreError("store identity is missing")
        return row["store_id"]

    def _checkpoint(self) -> dict[str, object]:
        records = [
            dict(row) for row in self.connection.execute(
                "SELECT event_id,event_digest,project_id,state,held_snapshot,"
                "confirmation_digest,confirmed_snapshot,resume_digest,completed_snapshot "
                "FROM real_chain_records ORDER BY event_id"
            )
        ]
        tail = self.connection.execute(
            "SELECT sequence,entry_hash FROM real_chain_audit ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        count = self.connection.execute("SELECT COUNT(*) FROM real_chain_audit").fetchone()[0]
        return {
            "store_id": self._store_id_unlocked(),
            "database_schema_version": self._SCHEMA_VERSION,
            "record_count": len(records),
            "records_sha256": canonical_digest(records),
            "schema_sha256": canonical_digest(self._schema_projection()),
            "audit_count": count,
            "audit_last_sequence": tail["sequence"] if tail else 0,
            "audit_tail_hash": tail["entry_hash"] if tail else "0" * 64,
        }

    def _recover_unlocked(self) -> None:
        checkpoint = self._checkpoint()
        self.anchor.recover(checkpoint)
        if not self.anchor.verify(checkpoint):
            raise RealChainStoreError("real-chain store checkpoint is invalid")

    def recover(self) -> None:
        self._run_checked_transaction(
            require_operable=False,
            on_commit=lambda: setattr(self, "_recovery_required", False),
        )

    def _open_validate(self) -> None:
        self._run_checked_transaction(require_operable=False)

    def _ensure_operable(self) -> None:
        if self._recovery_required:
            raise RealChainStoreRecoveryRequired("pending-anchor-promotion")

    def _read(self, operation: Any) -> Any:
        return self._run_checked_transaction(operation)

    def _run_checked_transaction(
        self,
        operation: Any = None,
        *,
        require_operable: bool = True,
        on_commit: Any = None,
    ) -> Any:
        """Run the shared validate/verify/recover/commit sequence inside BEGIN.

        Used by recover / _open_validate / _read. ``operation`` may return a
        value; ``on_commit`` runs after commit (e.g. clearing the recovery
        flag). Any failure rolls the transaction back and re-raises.
        """
        with self._guard():
            if require_operable:
                self._ensure_operable()
            self.connection.execute("BEGIN")
            try:
                self._validate_schema()
                self._verify_audit_chain_unlocked()
                self._recover_unlocked()
                result = operation() if operation is not None else None
                self.connection.commit()
                if on_commit is not None:
                    on_commit()
                return result
            except Exception:
                if self.connection.in_transaction:
                    self.connection.rollback()
                raise

    def _abort_if_pending(self) -> None:
        if self.anchor.pending_head.exists():
            self.anchor.abort_pending()

    def _transaction(self, operation: Any, *, event_id: str) -> Any:
        with self._guard():
            self._ensure_operable()
            self.connection.execute("BEGIN IMMEDIATE")
            committed = False
            recovered = False
            try:
                self._validate_schema()
                self._verify_audit_chain_unlocked()
                self._recover_unlocked()
                recovered = True
                result = operation()
                self._validate_schema()
                self._verify_audit_chain_unlocked()
                self.anchor.prepare(self._checkpoint())
                self.connection.commit()
                committed = True
                try:
                    self.anchor.promote()
                except Exception as exc:
                    self._recovery_required = True
                    raise RealChainStoreRecoveryRequired(event_id) from exc
                return result
            except RealChainStoreRecoveryRequired:
                raise
            except Exception:
                if not committed and self.connection.in_transaction:
                    self.connection.rollback()
                    if recovered:
                        self._abort_if_pending()
                raise

    @property
    def store_id(self) -> str:
        return self._read(self._store_id_unlocked)

    def close(self) -> None:
        self.connection.close()

    @property
    def audit_entries(self) -> tuple[RealChainAuditEntry, ...]:
        return self._read(self._audit_entries_unlocked)

    def _audit_entries_unlocked(self) -> tuple[RealChainAuditEntry, ...]:
        rows = self.connection.execute("SELECT * FROM real_chain_audit ORDER BY sequence").fetchall()
        return tuple(RealChainAuditEntry(**dict(row)) for row in rows)

    def _audit(self, event_id: str, action: str, result: str,
               digest: str, now: str) -> None:
        row = self.connection.execute(
            "SELECT sequence,entry_hash FROM real_chain_audit ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous = row["entry_hash"] if row else "0" * 64
        sequence = (row["sequence"] + 1) if row else 1
        body = {"sequence": sequence, "event_id": event_id, "action": action,
                "result": result, "payload_digest": digest, "recorded_at": now,
                "previous_hash": previous}
        entry_hash = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
        self.connection.execute(
            "INSERT INTO real_chain_audit(sequence,event_id,action,result,payload_digest,recorded_at,previous_hash,entry_hash) VALUES(?,?,?,?,?,?,?,?)",
            (sequence, event_id, action, result, digest, now, previous, entry_hash),
        )

    def verify_audit_chain(self) -> bool:
        return self._read(lambda: True)

    def _verify_audit_chain_unlocked(self) -> None:
        previous = "0" * 64
        for expected, entry in enumerate(self._audit_entries_unlocked(), start=1):
            body = {"sequence": entry.sequence, "event_id": entry.event_id,
                    "action": entry.action, "result": entry.result,
                    "payload_digest": entry.payload_digest, "recorded_at": entry.recorded_at,
                    "previous_hash": entry.previous_hash}
            if (entry.sequence != expected or entry.previous_hash != previous
                    or entry.entry_hash != hashlib.sha256(canonical_json_bytes(body)).hexdigest()):
                raise RealChainStoreError("real-chain audit history is invalid")
            previous = entry.entry_hash

    def _mark_interrupted_for_recovery(self) -> None:
        rows = self._read(lambda: self.connection.execute(
            "SELECT event_id FROM real_chain_records "
            "WHERE state IN ('DISPATCHING','PACKAGE_BUILDING')"
        ).fetchall())
        if not rows:
            return

        def operation() -> None:
            rows = self.connection.execute(
                "SELECT event_id,event_digest,state FROM real_chain_records WHERE state IN ('DISPATCHING','PACKAGE_BUILDING')"
            ).fetchall()
            for row in rows:
                self.connection.execute(
                    "UPDATE real_chain_records SET state='RECOVERY_REQUIRED' WHERE event_id=?",
                    (row["event_id"],),
                )
                self._audit(row["event_id"], "recovery", "required",
                            row["event_digest"], "1970-01-01T00:00:00Z")
        self._transaction(operation, event_id="startup-recovery")

    def begin_dispatch(self, event_id: str, event_digest: str,
                       project_id: str, now: str) -> Any | None:
        """Begin a dispatch transaction with replay gate."""
        def operation() -> Any | None:
            row = self.connection.execute(
                "SELECT * FROM real_chain_records WHERE event_id=?", (event_id,)
            ).fetchone()
            self._audit(event_id, "dispatch", "attempt", event_digest, now)
            if row is None:
                self.connection.execute(
                    "INSERT INTO real_chain_records(event_id,event_digest,project_id,state) VALUES(?,?,?,'DISPATCHING')",
                    (event_id, event_digest, project_id),
                )
                return None
            if row["event_digest"] != event_digest:
                self._audit(event_id, "dispatch", "digest_conflict", event_digest, now)
                return RealChainStoreError("same event_id has a different canonical digest")
            if row["state"] == "ESCALATED" and row["completed_snapshot"]:
                return _restore(row["completed_snapshot"])
            if row["state"] in {"HELD", "TERMINAL"}:
                return _restore(row["held_snapshot"])
            if row["state"] == "CONFIRMED_PENDING_PACKAGE":
                return _restore(row["confirmed_snapshot"])
            self._audit(event_id, "dispatch", "state_conflict", event_digest, now)
            return RealChainStoreError("event is in progress or requires recovery")
        result = self._transaction(operation, event_id=event_id)
        if isinstance(result, RealChainStoreError):
            raise result
        return result

    def finish_dispatch(self, event_id: str, event_digest: str,
                        outcome: Any, state: str, now: str) -> None:
        """Finish a dispatch as TERMINAL/HELD."""
        def operation() -> None:
            row = self._require(event_id, event_digest)
            if row["state"] != "DISPATCHING":
                raise RealChainStoreError("dispatch claim is not active")
            self.connection.execute(
                "UPDATE real_chain_records SET state=?,held_snapshot=? WHERE event_id=?",
                (state, _snapshot(outcome), event_id),
            )
            self._audit(event_id, "dispatch", state.lower(), event_digest, now)
        self._transaction(operation, event_id=event_id)

    def record_attempt(self, event_id: str, event_digest: str,
                       action: str, result: str, now: str) -> None:
        self._transaction(lambda: (self._require(event_id, event_digest),
                                   self._audit(event_id, action, result, event_digest, now)),
                          event_id=event_id)

    def record_authorization_rejection(self, event_id: str, event_digest: str,
                                       action: str, actor_id: str,
                                       permission: str, now: str) -> None:
        """Record an authorization rejection for an event."""
        digest = canonical_digest({"actor_id": actor_id, "permission": permission})
        self._transaction(lambda: (self._require(event_id, event_digest),
                                   self._audit(event_id, action, "unauthorized", digest, now)),
                          event_id=event_id)

    def held_outcome(self, event_id: str, event_digest: str) -> Any:
        return self._read(lambda: _restore(self._require(event_id, event_digest)["held_snapshot"]))

    def confirmed_outcome(self, event_id: str, event_digest: str) -> Any:
        return self._read(lambda: _restore(self._require(event_id, event_digest)["confirmed_snapshot"]))

    def confirm(self, event_id: str, event_digest: str, confirmation_digest: str,
                outcome_factory: Any, now: str) -> Any:
        """Confirm a held dispatch with a signed digest."""
        def operation() -> Any:
            row = self._require(event_id, event_digest)
            self._audit(event_id, "confirmation", "attempt", confirmation_digest, now)
            if row["confirmation_digest"]:
                if row["confirmation_digest"] != confirmation_digest:
                    self._audit(event_id, "confirmation", "digest_conflict",
                                confirmation_digest, now)
                    return RealChainStoreError("event already has a different confirmation")
                return _restore(row["confirmed_snapshot"])
            if row["state"] != "HELD":
                self._audit(event_id, "confirmation", "state_conflict",
                            confirmation_digest, now)
                return RealChainStoreError("only a held event can be confirmed")
            outcome = outcome_factory()
            self.connection.execute(
                "UPDATE real_chain_records SET state='CONFIRMED_PENDING_PACKAGE',confirmation_digest=?,confirmed_snapshot=? WHERE event_id=?",
                (confirmation_digest, _snapshot(outcome), event_id),
            )
            self._audit(event_id, "confirmation", "confirmed", confirmation_digest, now)
            return outcome
        result = self._transaction(operation, event_id=event_id)
        if isinstance(result, RealChainStoreError):
            raise result
        return result

    def begin_resume(self, event_id: str, event_digest: str,
                     resume_digest: str, now: str) -> None:
        """Begin the package-build resume transaction."""
        def operation() -> None:
            row = self._require(event_id, event_digest)
            self._audit(event_id, "resume", "attempt", resume_digest, now)
            if row["resume_digest"] and row["resume_digest"] != resume_digest:
                self._audit(event_id, "resume", "digest_conflict", resume_digest, now)
                return RealChainStoreError("event already has a different resume digest")
            if row["state"] == "PACKAGE_BUILDING":
                self._audit(event_id, "resume", "already_building", resume_digest, now)
                return RealChainStoreError("package build is already in progress")
            if row["state"] != "CONFIRMED_PENDING_PACKAGE":
                self._audit(event_id, "resume", "state_conflict", resume_digest, now)
                return RealChainStoreError("event is not confirmed for package build")
            self.connection.execute(
                "UPDATE real_chain_records SET state='PACKAGE_BUILDING',resume_digest=? WHERE event_id=?",
                (resume_digest, event_id),
            )
        result = self._transaction(operation, event_id=event_id)
        if isinstance(result, RealChainStoreError):
            raise result

    def finish_resume_failure(self, event_id: str, event_digest: str,
                              resume_digest: str, outcome: Any, code: str, now: str) -> None:
        """Finish a failed resume with rollback."""
        def operation() -> None:
            row = self._require(event_id, event_digest)
            if row["state"] != "PACKAGE_BUILDING" or row["resume_digest"] != resume_digest:
                raise RealChainStoreError("package claim does not match")
            self.connection.execute(
                "UPDATE real_chain_records SET state='ESCALATED',completed_snapshot=? WHERE event_id=?",
                (_snapshot(outcome), event_id),
            )
            self._audit(event_id, "package", code, resume_digest, now)
        self._transaction(operation, event_id=event_id)

    def finish_resume_success(self, event_id: str, event_digest: str,
                              resume_digest: str, outcome: Any, package_digest: str,
                              now: str) -> None:
        """Finish a successful resume with package wire digest."""
        def operation() -> None:
            row = self._require(event_id, event_digest)
            if row["state"] != "PACKAGE_BUILDING" or row["resume_digest"] != resume_digest:
                raise RealChainStoreError("package claim does not match")
            self.connection.execute(
                "UPDATE real_chain_records SET state='COMPLETED',completed_snapshot=? WHERE event_id=?",
                (_snapshot(outcome), event_id),
            )
            self._audit(event_id, "package", "completed", package_digest, now)
        self._transaction(operation, event_id=event_id)

    def recovery_context(self, event_id: str) -> RecoveryContext:
        """Return the recovery context for an event."""
        def operation() -> RecoveryContext:
            row = self.connection.execute(
                "SELECT event_id,event_digest,project_id,state FROM real_chain_records WHERE event_id=?",
                (event_id,),
            ).fetchone()
            if row is None:
                raise RealChainStoreError("unknown event")
            return RecoveryContext(**dict(row))
        return self._read(operation)

    def terminate_recovery(self, event_id: str, actor_digest: str, now: str) -> RecoveryContext:
        """Terminate a recovery and mark it resolved."""
        def operation() -> RecoveryContext:
            row = self.connection.execute(
                "SELECT event_id,event_digest,project_id,state FROM real_chain_records WHERE event_id=?",
                (event_id,),
            ).fetchone()
            if row is None or row["state"] != "RECOVERY_REQUIRED":
                raise RealChainStoreError("event does not require recovery")
            self.connection.execute(
                "UPDATE real_chain_records SET state='ESCALATED' WHERE event_id=?", (event_id,)
            )
            self._audit(event_id, "recovery", "manually_escalated", actor_digest, now)
            return RecoveryContext(row["event_id"], row["event_digest"], row["project_id"], "ESCALATED")
        return self._transaction(operation, event_id=event_id)

    def _require(self, event_id: str, event_digest: str) -> sqlite3.Row:
        row = self.connection.execute(
            "SELECT * FROM real_chain_records WHERE event_id=?", (event_id,)
        ).fetchone()
        if row is None or row["event_digest"] != event_digest:
            raise RealChainStoreError("unknown event or digest mismatch")
        return row
