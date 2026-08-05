"""SQLite identity persistence protected by signed, monotonic freshness anchors."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# SQLite 身份持久化 + 签名单调新鲜度锚：原子写、审计链、冲突即回滚。

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .audit_anchor import AuditAnchorError, FreshnessAuthority, SignedAuditAnchor, Signer, WindowsCertificateSigner, WindowsFreshnessAuthority
from .models import IdentityBundle, RegistrationResult


logger = logging.getLogger(__name__)


class ConflictError(RuntimeError):
    pass


class IdentityRepository:
    BUSINESS_TABLES = {
        "organizations": "organization_id", "users": "user_id", "clients": "client_id",
        "trusted_certificates": "certificate_id", "project_role_bindings": "project_id,user_id,role_code",
        "identity_commands": "request_id",
    }
    REQUIRED_TABLES = frozenset((*BUSINESS_TABLES, "identity_metadata", "identity_audit_events"))

    @classmethod
    def create(cls, database: str | Path, signer: Signer | None = None, freshness: FreshnessAuthority | None = None) -> "IdentityRepository":
        return cls(database, signer, freshness, create=True)

    @classmethod
    def open(cls, database: str | Path, signer: Signer | None = None, freshness: FreshnessAuthority | None = None) -> "IdentityRepository":
        return cls(database, signer, freshness, create=False)

    def __init__(self, database: str | Path, signer: Signer | None, freshness: FreshnessAuthority | None, *, create: bool):
        self.database = Path(database).resolve()
        self.anchor = SignedAuditAnchor(self.database, signer or WindowsCertificateSigner(), freshness or WindowsFreshnessAuthority())
        if create:
            if self.database.exists() or any(path.exists() for path in self.anchor.artifacts()):
                raise AuditAnchorError("refusing to create identity store over existing state")
            connection_target = str(self.database)
            uri = False
        else:
            if not self.database.is_file():
                raise AuditAnchorError("identity store does not exist; explicit create is required")
            connection_target = f"file:{self.database.as_posix()}?mode=rw"
            uri = True
        self.connection = sqlite3.connect(connection_target, isolation_level=None, uri=uri)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        try:
            if create:
                schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
                self.connection.executescript(schema)
                self.connection.execute("INSERT INTO identity_metadata(singleton,store_id,schema_version) VALUES(1,?,'1.0')", (str(uuid.uuid4()),))
                with self.anchor.locked():
                    self.anchor.prepare(self._checkpoint())
                    self.anchor.promote()
            else:
                self._validate_schema()
                if not self._internal_audit_valid():
                    raise AuditAnchorError("identity audit hash chain is invalid")
                with self.anchor.locked():
                    self.anchor.recover(self._checkpoint())
        except Exception:
            self.connection.close()
            if create:
                self._cleanup_failed_create()
            raise

    def _cleanup_failed_create(self) -> None:
        """Best-effort removal of a half-created store (never masks the original error)."""
        try:
            if self.anchor.pending_head.exists() and self.anchor.pending_signature.exists() and self.anchor.pending_new_signature.exists():
                self.anchor.abort_pending()
        except Exception as exc:  # noqa: BLE001 - best-effort cleanup must never mask the original error
            logger.warning(
                "identity failed-create: abort_pending failed: %s", exc
            )
        for path in self.anchor.artifacts():
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning(
                    "identity failed-create: cannot remove %s: %s", path, exc
                )
        try:
            self.database.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning(
                "identity failed-create: cannot remove database %s: %s",
                self.database, exc,
            )

    def _validate_schema(self) -> None:
        tables = {row[0] for row in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not self.REQUIRED_TABLES.issubset(tables):
            raise AuditAnchorError("identity store schema is incomplete")
        metadata = self.connection.execute("SELECT store_id,schema_version FROM identity_metadata WHERE singleton=1").fetchone()
        if metadata is None or metadata["schema_version"] != "1.0":
            raise AuditAnchorError("identity store schema version is unsupported")
        certificate_columns = {row[1] for row in self.connection.execute("PRAGMA table_info(trusted_certificates)")}
        if not {"serial_number", "public_key_algorithm_oid", "public_key_spki_der"}.issubset(certificate_columns):
            raise AuditAnchorError("identity certificate schema is incomplete")

    def close(self) -> None:
        self.connection.close()

    def _insert_audit(self, actor_id: str, action: str, request_id: str, result: str, target: dict, payload_digest: str | None) -> None:
        previous = self.connection.execute("SELECT event_hash FROM identity_audit_events ORDER BY sequence_no DESC LIMIT 1").fetchone()
        prev_hash = previous[0] if previous else "0" * 64
        event = {
            "event_id": str(uuid.uuid4()), "occurred_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "actor_id": actor_id, "action": action, "request_id": request_id, "result": result,
            "target_summary": json.dumps(target, sort_keys=True, separators=(",", ":")),
            "payload_digest": payload_digest, "prev_hash": prev_hash,
        }
        event_hash = hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.connection.execute(
            "INSERT INTO identity_audit_events(event_id,occurred_at,actor_id,action,request_id,result,target_summary,payload_digest,prev_hash,event_hash) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (event["event_id"], event["occurred_at"], actor_id, action, request_id, result, event["target_summary"], payload_digest, prev_hash, event_hash),
        )

    @staticmethod
    def _safe_value(value: Any) -> Any:
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)} if isinstance(value, bytes) else value

    def _business_digest(self) -> str:
        state: dict[str, list[dict[str, Any]]] = {}
        for table, ordering in self.BUSINESS_TABLES.items():
            rows = self.connection.execute(f"SELECT * FROM {table} ORDER BY {ordering}").fetchall()
            state[table] = [{key: self._safe_value(row[key]) for key in row.keys()} for row in rows]
        return hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def _checkpoint(self) -> dict:
        metadata = self.connection.execute("SELECT store_id,schema_version FROM identity_metadata WHERE singleton=1").fetchone()
        tail = self.connection.execute("SELECT sequence_no,event_hash FROM identity_audit_events ORDER BY sequence_no DESC LIMIT 1").fetchone()
        count = self.connection.execute("SELECT COUNT(*) FROM identity_audit_events").fetchone()[0]
        return {
            "store_id": metadata["store_id"], "database_schema_version": metadata["schema_version"],
            "audit_sequence": tail["sequence_no"] if tail else 0, "audit_count": count,
            "audit_event_hash": tail["event_hash"] if tail else "0" * 64, "business_state_sha256": self._business_digest(),
        }

    def _internal_audit_valid(self) -> bool:
        previous = "0" * 64
        for row in self.connection.execute("SELECT * FROM identity_audit_events ORDER BY sequence_no"):
            event = {key: row[key] for key in ("event_id", "occurred_at", "actor_id", "action", "request_id", "result", "target_summary", "payload_digest", "prev_hash")}
            expected = hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if row["prev_hash"] != previous or row["event_hash"] != expected:
                return False
            previous = row["event_hash"]
        return True

    def _recover_and_require_consistent(self) -> None:
        if not self._internal_audit_valid():
            raise AuditAnchorError("identity audit hash chain is invalid")
        checkpoint = self._checkpoint()
        self.anchor.recover(checkpoint)
        if not self.anchor.verify(checkpoint):
            raise AuditAnchorError("identity database does not match its signed audit anchor")

    def _abort_if_pending(self) -> None:
        if self.anchor.pending_head.exists():
            self.anchor.abort_pending()

    def _commit_with_anchor(self) -> None:
        committed = False
        try:
            self.anchor.prepare(self._checkpoint())
            self.connection.commit()
            committed = True
            self.anchor.promote()
        except Exception:
            if not committed:
                self.connection.rollback()
                self._abort_if_pending()
            raise

    def record_rejection(self, actor_id: str, request_id: str, result: str, payload_digest: str | None = None) -> None:
        """Record an authorization rejection event."""
        with self.anchor.locked():
            self._recover_and_require_consistent()
            self.connection.execute("BEGIN IMMEDIATE")
            try:
                self._insert_audit(actor_id, "register_identity_bundle", request_id, result, {}, payload_digest)
                self._commit_with_anchor()
            except Exception:
                if self.connection.in_transaction:
                    self.connection.rollback(); self._abort_if_pending()
                raise

    def register(self, actor_id: str, request_id: str, bundle: IdentityBundle) -> RegistrationResult:
        """Register an identity bundle atomically with audit."""
        result = RegistrationResult(request_id, bundle.organization.organization_id, bundle.user.user_id, bundle.client.client_id, bundle.certificate.certificate_id)
        result_json = json.dumps(result.__dict__, sort_keys=True, separators=(",", ":"))
        with self.anchor.locked():
            self._recover_and_require_consistent()
            try:
                self.connection.execute("BEGIN IMMEDIATE")
                prior = self.connection.execute("SELECT payload_digest,result_json FROM identity_commands WHERE request_id=?", (request_id,)).fetchone()
                if prior:
                    if prior["payload_digest"] != bundle.payload_digest:
                        raise ConflictError("request_id was already used with different content")
                    data = json.loads(prior["result_json"]); data["replayed"] = True; replay = RegistrationResult(**data)
                    self._insert_audit(actor_id, "register_identity_bundle", request_id, "replayed", {"organization_id": replay.organization_id, "user_id": replay.user_id, "client_id": replay.client_id, "certificate_id": replay.certificate_id}, bundle.payload_digest)
                    self._commit_with_anchor(); return replay
                self.connection.execute("INSERT INTO organizations(organization_id,code,name) VALUES(?,?,?)", (bundle.organization.organization_id, bundle.organization.code, bundle.organization.name))
                self.connection.execute("INSERT INTO users(user_id,organization_id,display_name) VALUES(?,?,?)", (bundle.user.user_id, bundle.user.organization_id, bundle.user.display_name))
                self.connection.execute("INSERT INTO clients(client_id,organization_id,assigned_user_id,display_name) VALUES(?,?,?,?)", (bundle.client.client_id, bundle.client.organization_id, bundle.client.assigned_user_id, bundle.client.display_name))
                cert = bundle.certificate
                self.connection.execute("INSERT INTO trusted_certificates(certificate_id,owner_user_id,bound_client_id,certificate_der,public_key_spki_der,fingerprint_sha256,valid_from,valid_to,serial_number,public_key_algorithm_oid,revoked) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (cert.certificate_id, cert.owner_user_id, cert.bound_client_id, cert.certificate_der, cert.public_key_spki_der, cert.fingerprint_sha256, cert.valid_from, cert.valid_to, cert.serial_number, cert.public_key_algorithm_oid, int(cert.revoked)))
                self.connection.executemany("INSERT INTO project_role_bindings(project_id,user_id,role_code) VALUES(?,?,?)", [(role.project_id, role.user_id, role.role_code) for role in bundle.roles])
                self.connection.execute("INSERT INTO identity_commands(request_id,payload_digest,result_json) VALUES(?,?,?)", (request_id, bundle.payload_digest, result_json))
                self._insert_audit(actor_id, "register_identity_bundle", request_id, "success", {"organization_id": result.organization_id, "user_id": result.user_id, "client_id": result.client_id, "certificate_id": result.certificate_id}, bundle.payload_digest)
                self._commit_with_anchor(); return result
            except ConflictError:
                self.connection.rollback(); self._abort_if_pending(); raise
            except sqlite3.IntegrityError as exc:
                self.connection.rollback(); self._abort_if_pending(); raise ConflictError("identity bundle conflicts with existing data") from exc
            except Exception:
                if self.connection.in_transaction:
                    self.connection.rollback(); self._abort_if_pending()
                raise

    def verify_audit_chain(self) -> bool:
        return self._internal_audit_valid() and self.anchor.verify(self._checkpoint())
