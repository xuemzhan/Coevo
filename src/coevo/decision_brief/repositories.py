"""decision_brief.repositories - persistent repositories for approved templates, risk confirmations and decision brief versions."""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import stat
from dataclasses import replace
from pathlib import Path, PurePosixPath
from threading import Lock
from src.coevo.merge.receipt import MergeCommitReceipt, ReceiptSigningAuthority
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.risk import RiskReport

from .models import ApprovedTemplate, BRIEF_SCHEMA, BriefContent, DecisionBrief, DecisionBriefConflictError, DecisionBriefValidationError, MAX_BRIEF_CONTENT_BYTES, MAX_TEMPLATE_BYTES, RISK_CONFIRMATION_DOMAIN, RiskConfirmation, _clone_brief, _clone_confirmation, _clone_risk_report, _content_digest, _content_sources, _digest, _encode_json, _is_link_or_reparse, _latest_receipt, _make_version, _parse_utc, _risk_digest, _safe_string, _stat_is_reparse, _validate_bound_risk, _validate_docx, _validate_risk_report, _validate_stored_brief, _validate_template_ref


def _replay_entry(
    events: dict[str, tuple[str, object]],
    event_id: str,
    intent: str,
    *,
    conflict_message: str,
) -> object | None:
    """Return the stored entry for an idempotent replay, or None if fresh.

    Shared by confirm/create/revise: an event_id already recorded with a
    different intent is an ID conflict (fail-closed); a matching intent
    returns the stored entry so the caller can apply its stale checks.
    """
    replay = events.get(event_id)
    if replay is None:
        return None
    if replay[0] != intent:
        raise DecisionBriefConflictError(conflict_message)
    return replay[1]


class ApprovedTemplateRegistry:
    """Pins reviewed DOCX bytes and re-verifies the file before every use."""

    def __init__(
        self,
        controlled_root: Path,
        *,
        max_template_bytes: int = MAX_TEMPLATE_BYTES,
    ) -> None:
        if not isinstance(controlled_root, Path):
            raise DecisionBriefValidationError("controlled_root must be Path")
        if isinstance(max_template_bytes, bool) or not isinstance(max_template_bytes, int):
            raise DecisionBriefValidationError("max_template_bytes must be an integer")
        if not 1 <= max_template_bytes <= MAX_TEMPLATE_BYTES:
            raise DecisionBriefValidationError("max_template_bytes exceeds policy")
        if _is_link_or_reparse(controlled_root):
            raise DecisionBriefValidationError("controlled template root is unsafe")
        root = controlled_root.resolve(strict=True)
        if not root.is_dir() or _is_link_or_reparse(root):
            raise DecisionBriefValidationError("controlled template root is unsafe")
        self._root = root
        self._max_template_bytes = max_template_bytes
        self._approvals: dict[str, tuple[str, str]] = {}
        self._lock = Lock()

    def approve(self, *, approval_id: str, template_ref: str) -> ApprovedTemplate:
        _safe_string(approval_id, field="approval_id", max_bytes=1024)
        payload = self._read_safe(template_ref)
        approval = ApprovedTemplate(
            approval_id=approval_id,
            template_ref=template_ref,
            template_digest=hashlib.sha256(payload).hexdigest(),
        )
        with self._lock:
            existing = self._approvals.get(approval_id)
            record = (approval.template_ref, approval.template_digest)
            if existing is not None and existing != record:
                raise DecisionBriefConflictError("template approval ID was already used")
            self._approvals[approval_id] = record
        return approval

    def verify(self, *, approval_id: str, template_ref: str) -> ApprovedTemplate:
        _safe_string(approval_id, field="approval_id", max_bytes=1024)
        with self._lock:
            record = self._approvals.get(approval_id)
        if record is None or record[0] != template_ref:
            raise DecisionBriefValidationError("template is not approved")
        payload = self._read_safe(template_ref)
        if hashlib.sha256(payload).hexdigest() != record[1]:
            raise DecisionBriefValidationError("approved template bytes changed")
        return ApprovedTemplate(
            approval_id=approval_id,
            template_ref=record[0],
            template_digest=record[1],
        )

    def _read_safe(self, template_ref: str) -> bytes:
        _validate_template_ref(template_ref)
        relative = PurePosixPath(template_ref)
        candidate = self._root.joinpath(*relative.parts)
        current = self._root
        for part in relative.parts:
            current = current / part
            try:
                info = current.lstat()
            except OSError as exc:
                raise DecisionBriefValidationError("template path is unavailable") from exc
            if stat.S_ISLNK(info.st_mode) or _stat_is_reparse(info):
                raise DecisionBriefValidationError("template path cannot contain links")
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(self._root)
            info = candidate.lstat()
        except (OSError, ValueError) as exc:
            raise DecisionBriefValidationError("template escapes controlled root") from exc
        if not stat.S_ISREG(info.st_mode) or _stat_is_reparse(info):
            raise DecisionBriefValidationError("template must be a regular file")
        if info.st_size < 1 or info.st_size > self._max_template_bytes:
            raise DecisionBriefValidationError("template file is empty or oversized")
        try:
            with resolved.open("rb") as stream:
                if not os.path.samestat(info, os.fstat(stream.fileno())):
                    raise DecisionBriefValidationError("template changed during verification")
                payload = stream.read(self._max_template_bytes + 1)
            final_info = candidate.lstat()
            final_resolved = candidate.resolve(strict=True)
            final_resolved.relative_to(self._root)
        except OSError as exc:
            raise DecisionBriefValidationError("template cannot be read") from exc
        except ValueError as exc:
            raise DecisionBriefValidationError("template escaped during verification") from exc
        if (
            not os.path.samestat(info, final_info)
            or _stat_is_reparse(final_info)
            or final_resolved != resolved
        ):
            raise DecisionBriefValidationError("template changed during verification")
        if len(payload) > self._max_template_bytes:
            raise DecisionBriefValidationError("template file is oversized")
        _validate_docx(payload)
        return payload

class RiskConfirmationRepository:
    """Owner-signed authoritative risk confirmations."""

    def __init__(self, authority: ReceiptSigningAuthority) -> None:
        if type(authority) is not ReceiptSigningAuthority:
            raise DecisionBriefValidationError("owner authority is required")
        self._authority = authority
        self._items: dict[str, RiskConfirmation] = {}
        self._events: dict[str, tuple[str, RiskConfirmation]] = {}
        self._lock = Lock()

    def confirm(
        self,
        *,
        receipt_id: str,
        receipt_repository: MergeReceiptRepository,
        risk_report: RiskReport,
        confirmed_at: str,
        confirmed_by: str,
        event_id: str,
    ) -> RiskConfirmation:
        trusted_time = _parse_utc(confirmed_at, field="confirmed_at")
        _safe_string(confirmed_by, field="confirmed_by", max_bytes=1024)
        _safe_string(event_id, field="event_id", max_bytes=1024)
        receipt = _latest_receipt(receipt_id, receipt_repository, trusted_time)
        _validate_risk_report(risk_report)
        _validate_bound_risk(receipt, risk_report, trusted_time)
        owner_identities = {
            confirmed_by,
            receipt.decision_maker,
            receipt.recipient_cert_id,
            self._authority.signer_certificate_id,
            self._authority.reference.bound_certificate_id,
        }
        if len(owner_identities) != 1:
            raise DecisionBriefValidationError(
                "risk confirmation owner identities do not match"
            )
        baseline_tasks = {
            task.task_id
            for work_package in receipt.snapshot.baseline.work_packages
            for task in work_package.tasks
        }
        if any(
            task_id not in baseline_tasks
            for risk in risk_report.risks
            for task_id in risk.affected_tasks
        ):
            raise DecisionBriefValidationError(
                "risk references a task outside the confirmed baseline"
            )
        fields = {
            "domain": RISK_CONFIRMATION_DOMAIN,
            "schema_version": BRIEF_SCHEMA,
            "receipt_id": receipt.receipt_id,
            "snapshot_digest": receipt.snapshot.digest,
            "risk_digest": _risk_digest(risk_report),
            "confirmed_at": confirmed_at,
            "confirmed_by": confirmed_by,
        }
        payload = _encode_json(fields, max_bytes=16 * 1024)
        intent = hashlib.sha256(payload).hexdigest()
        with self._lock:
            entry = _replay_entry(
                self._events, event_id, intent,
                conflict_message="risk confirmation event ID conflict",
            )
            if entry is not None:
                return _clone_confirmation(entry)
            signature = self._authority.service.use(
                self._authority.reference,
                payload,
                trusted_time=trusted_time,
                actor_id=confirmed_by,
                request_id=event_id,
            )
            if not self._verify_signature(payload, signature, trusted_time, event_id):
                raise DecisionBriefValidationError("risk confirmation signature is invalid")
            item = RiskConfirmation(
                confirmation_id=hashlib.sha256(payload + signature).hexdigest(),
                payload=payload,
                signature=signature,
                receipt_id=receipt.receipt_id,
                snapshot_digest=receipt.snapshot.digest,
                risk_digest=fields["risk_digest"],
                confirmed_at=confirmed_at,
                confirmed_by=confirmed_by,
                report=_clone_risk_report(risk_report),
            )
            self._items[item.confirmation_id] = item
            self._events[event_id] = (intent, item)
            return _clone_confirmation(item)

    def verified(
        self,
        confirmation_id: str,
        *,
        receipt: MergeCommitReceipt,
        trusted_time: dt.datetime,
    ) -> RiskConfirmation:
        _safe_string(confirmation_id, field="confirmation_id", max_bytes=1024)
        with self._lock:
            item = self._items.get(confirmation_id)
        if item is None:
            raise DecisionBriefValidationError("risk confirmation is absent")
        _validate_risk_report(item.report)
        if (
            item.receipt_id != receipt.receipt_id
            or item.snapshot_digest != receipt.snapshot.digest
            or item.risk_digest != _risk_digest(item.report)
        ):
            raise DecisionBriefValidationError("risk confirmation binding mismatch")
        if _parse_utc(item.confirmed_at, field="confirmed_at") > trusted_time:
            raise DecisionBriefValidationError("risk confirmation is from the future")
        RiskConfirmation(
            confirmation_id=item.confirmation_id,
            payload=item.payload,
            signature=item.signature,
            receipt_id=item.receipt_id,
            snapshot_digest=item.snapshot_digest,
            risk_digest=item.risk_digest,
            confirmed_at=item.confirmed_at,
            confirmed_by=item.confirmed_by,
            report=item.report,
        )
        if not self._verify_signature(
            item.payload, item.signature, trusted_time, item.confirmation_id
        ):
            raise DecisionBriefValidationError("risk confirmation signature is invalid")
        return _clone_confirmation(item)

    def _verify_signature(
        self,
        payload: bytes,
        signature: bytes,
        trusted_time: dt.datetime,
        request_id: str,
    ) -> bool:
        return self._authority.service.verify(
            self._authority.reference,
            payload,
            signature,
            trusted_time=trusted_time,
            actor_id="decision-brief",
            request_id=request_id,
            expected_certificate_id=self._authority.signer_certificate_id,
            expected_parent_thumbprint=self._authority.parent_pinned_thumbprint,
            expected_public_sha256=self._authority.reference.key_public_sha256,
            expected_algorithm_oid=self._authority.reference.algorithm_oid,
        )

class DecisionBriefRepository:
    """Authoritative in-memory draft store with CAS and event idempotency."""

    def __init__(self) -> None:
        self._briefs: dict[str, DecisionBrief] = {}
        self._events: dict[str, tuple[str, DecisionBrief]] = {}
        self._lock = Lock()

    def get(self, brief_id: str) -> DecisionBrief:
        _safe_string(brief_id, field="brief_id", max_bytes=1024)
        with self._lock:
            brief = self._briefs.get(brief_id)
        if brief is None:
            raise DecisionBriefValidationError("decision brief is absent")
        _validate_stored_brief(brief)
        return _clone_brief(brief)

    def create(self, brief: DecisionBrief, *, event_id: str) -> DecisionBrief:
        if type(brief) is not DecisionBrief:
            raise DecisionBriefValidationError("brief must be exact DecisionBrief")
        _validate_stored_brief(brief)
        _safe_string(event_id, field="event_id", max_bytes=1024)
        intent = hashlib.sha256(
            b"create\0" + brief.brief_id.encode() + b"\0" + brief.head_digest.encode()
        ).hexdigest()
        with self._lock:
            entry = _replay_entry(
                self._events, event_id, intent,
                conflict_message="brief event ID conflict",
            )
            if entry is not None:
                current = self._briefs.get(entry.brief_id)
                if current is None or current.head_digest != entry.head_digest:
                    raise DecisionBriefConflictError("stale brief event replay")
                return _clone_brief(entry)
            if brief.brief_id in self._briefs:
                raise DecisionBriefConflictError("decision brief already exists")
            stored = _clone_brief(brief)
            self._briefs[brief.brief_id] = stored
            self._events[event_id] = (intent, stored)
            return _clone_brief(stored)

    def revise(
        self,
        *,
        brief_id: str,
        content: BriefContent,
        editor_id: str,
        edit_reason: str,
        edited_at: str,
        expected_revision: int,
        expected_head_digest: str,
        event_id: str,
        template_registry: ApprovedTemplateRegistry,
    ) -> DecisionBrief:
        if type(content) is not BriefContent:
            raise DecisionBriefValidationError("content must be exact BriefContent")
        _safe_string(brief_id, field="brief_id", max_bytes=1024)
        _safe_string(editor_id, field="editor_id", max_bytes=1024)
        _safe_string(edit_reason, field="edit_reason", max_bytes=4096)
        edited_time = _parse_utc(edited_at, field="edited_at")
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int):
            raise DecisionBriefValidationError("expected_revision must be an integer")
        _digest(expected_head_digest, field="expected_head_digest")
        _safe_string(event_id, field="event_id", max_bytes=1024)
        if type(template_registry) is not ApprovedTemplateRegistry:
            raise DecisionBriefValidationError("exact template registry is required")
        with self._lock:
            brief = self._briefs.get(brief_id)
            if brief is None:
                raise DecisionBriefValidationError("decision brief is absent")
            _validate_stored_brief(brief)
            approved_template = template_registry.verify(
                approval_id=brief.wps_request.template_approval_id,
                template_ref=brief.wps_request.template_ref,
            )
            intent = hashlib.sha256(_encode_json({
                "operation": "revise",
                "brief_id": brief_id,
                "content_digest": _content_digest(content),
                "editor_id": editor_id,
                "edit_reason": edit_reason,
                "edited_at": edited_at,
                "expected_revision": expected_revision,
                "expected_head_digest": expected_head_digest,
                "template_approval_id": approved_template.approval_id,
                "template_ref": approved_template.template_ref,
                "template_digest": approved_template.template_digest,
            }, max_bytes=MAX_BRIEF_CONTENT_BYTES)).hexdigest()
            entry = _replay_entry(
                self._events, event_id, intent,
                conflict_message="brief event ID conflict",
            )
            if entry is not None:
                if brief.head_digest != entry.head_digest:
                    raise DecisionBriefConflictError("stale brief event replay")
                return _clone_brief(entry)
            if (
                brief.current.revision != expected_revision
                or brief.head_digest != expected_head_digest
            ):
                raise DecisionBriefConflictError("stale brief revision or head digest")
            if (
                approved_template.approval_id
                != brief.wps_request.template_approval_id
                or approved_template.template_ref != brief.wps_request.template_ref
                or approved_template.template_digest
                != brief.wps_request.template_digest
            ):
                raise DecisionBriefValidationError(
                    "approved template does not match the brief request"
                )
            known_sources = set(_content_sources(brief.current.content))
            if not set(_content_sources(content)).issubset(known_sources):
                raise DecisionBriefValidationError(
                    "revisions cannot introduce unverified source references"
                )
            if edited_time < _parse_utc(brief.current.created_at, field="created_at"):
                raise DecisionBriefValidationError("edited_at predates current version")
            next_version = _make_version(
                revision=expected_revision + 1,
                created_at=edited_at,
                edited_by=editor_id,
                edit_reason=edit_reason,
                source_receipt_id=brief.current.source_receipt_id,
                source_package_id=brief.current.source_package_id,
                content=content,
                previous_version_digest=brief.head_digest,
            )
            revised = replace(
                brief,
                versions=brief.versions + (next_version,),
                wps_request=replace(
                    brief.wps_request,
                    source_revision=next_version.revision,
                    template_approval_id=approved_template.approval_id,
                    template_ref=approved_template.template_ref,
                    template_digest=approved_template.template_digest,
                ),
            )
            stored = _clone_brief(revised)
            self._briefs[brief_id] = stored
            self._events[event_id] = (intent, stored)
            return _clone_brief(stored)
