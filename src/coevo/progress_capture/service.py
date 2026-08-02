"""progress_capture.service - ProgressCaptureService facade and its private helpers."""

from __future__ import annotations

from typing import Iterable
from src.coevo.workspace.models import WorkspaceEntry

from .models import DOMAIN, EvidenceInput, EvidenceKind, ItemOverride, ProgressCapture, ProgressCaptureConflictError, ProgressCaptureValidationError, ProgressDraft, ProgressItem, ProgressItemKind, ProgressItemStatus, SCHEMA_VERSION, _check_confidence, _check_iso_utc, _check_non_empty_str, _check_safe_id

class ProgressCaptureService:
    """Pure-function facade over the US-8 data model.

    All public methods return new dataclass instances; no IO / DB / LLM /
    scheduling. The service is fully deterministic for a given
    ``(workspace, evidence_inputs, now)`` triple and the resulting
    ``capture_id`` is content-stable.
    """

    @staticmethod
    def extract_progress(
        workspace: WorkspaceEntry,
        evidence_inputs: Iterable[EvidenceInput],
        *,
        now: str,
    ) -> ProgressCapture:
        """AC-1..AC-4 + AC-7: parse inputs into a draft capture.

        Fails closed on:

        * workspace not a :class:`WorkspaceEntry`
        * any evidence_inputs item with kind == FILE_MTIME_ONLY (forbidden
          by AC-7)
        * any evidence_inputs item with confidence outside [0.0, 1.0]
        * any evidence_inputs item with empty evidence_refs
        * any evidence_ref path that traverses outside the workspace
        * ``now`` not in strict ISO-8601 UTC ``Z`` form
        """
        if not isinstance(workspace, WorkspaceEntry):
            raise ProgressCaptureValidationError(
                "workspace must be a WorkspaceEntry instance"
            )
        _check_iso_utc(now, field="now")

        inputs = tuple(evidence_inputs)
        for idx, ev in enumerate(inputs):
            if not isinstance(ev, EvidenceInput):
                raise ProgressCaptureValidationError(
                    f"evidence_inputs[{idx}] must be an EvidenceInput instance"
                )

        items: list[ProgressItem] = []
        for idx, ev in enumerate(inputs):
            item = ProgressItem(
                item_id=_make_item_id(workspace.project_id, ev.task_id, idx),
                workspace_project_id=workspace.project_id,
                task_id=ev.task_id,
                kind=_classify(ev),
                text=ev.text,
                source_kind=ev.kind,
                source_ref=ev.source_ref,
                confidence=ev.confidence,
                evidence_refs=ev.evidence_refs,
                status=ProgressItemStatus.PROPOSED,
                overrides=(),
                created_at=now,
            )
            items.append(item)

        capture_id = _make_capture_id(workspace.project_id, now, len(items))

        return ProgressCapture(
            schema_version=SCHEMA_VERSION,
            capture_id=capture_id,
            workspace=workspace,
            progress_items=tuple(items),
            requires_user_confirmation=True,
            formally_accepted=False,
            accepted_at="",
            accepted_by="",
            created_at=now,
        )

    @staticmethod
    def revise(
        capture: ProgressCapture,
        item_id: str,
        *,
        new_text: str | None = None,
        new_kind: ProgressItemKind | None = None,
        new_confidence: float | None = None,
        reason: str,
        now: str,
    ) -> ProgressCapture:
        """AC-5: replace item fields and append an override."""
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        _check_iso_utc(now, field="now")
        _check_non_empty_str(reason, field="reason")
        if new_text is None and new_kind is None and new_confidence is None:
            raise ProgressCaptureValidationError(
                "revise requires at least one of new_text/new_kind/new_confidence"
            )
        if new_confidence is not None:
            _check_confidence(new_confidence)

        new_items: list[ProgressItem] = []
        found = False
        for item in capture.progress_items:
            if item.item_id != item_id:
                new_items.append(item)
                continue
            found = True
            if item.status == ProgressItemStatus.REJECTED:
                raise ProgressCaptureConflictError(
                    f"cannot revise REJECTED item {item_id!r}"
                )
            if item.status == ProgressItemStatus.ACCEPTED and capture.formally_accepted:
                raise ProgressCaptureConflictError(
                    f"cannot revise ACCEPTED item {item_id!r} on a formally_accepted capture"
                )
            new_overrides = item.overrides
            replaced_text = item.text
            replaced_kind = item.kind
            replaced_confidence = item.confidence
            if new_text is not None:
                _check_non_empty_str(new_text, field="new_text")
                new_overrides = new_overrides + (
                    ItemOverride(
                        target_path="text",
                        original_value=item.text,
                        edited_value=new_text,
                        reason=reason,
                        edited_at=now,
                    ),
                )
                replaced_text = new_text
            if new_kind is not None:
                if not isinstance(new_kind, ProgressItemKind):
                    raise ProgressCaptureValidationError(
                        f"new_kind must be ProgressItemKind; got {new_kind!r}"
                    )
                new_overrides = new_overrides + (
                    ItemOverride(
                        target_path="kind",
                        original_value=item.kind,
                        edited_value=new_kind,
                        reason=reason,
                        edited_at=now,
                    ),
                )
                replaced_kind = new_kind
            if new_confidence is not None:
                new_overrides = new_overrides + (
                    ItemOverride(
                        target_path="confidence",
                        original_value=item.confidence,
                        edited_value=new_confidence,
                        reason=reason,
                        edited_at=now,
                    ),
                )
                replaced_confidence = new_confidence
            new_items.append(
                ProgressItem(
                    item_id=item.item_id,
                    workspace_project_id=item.workspace_project_id,
                    task_id=item.task_id,
                    kind=replaced_kind,
                    text=replaced_text,
                    source_kind=item.source_kind,
                    source_ref=item.source_ref,
                    confidence=replaced_confidence,
                    evidence_refs=item.evidence_refs,
                    status=ProgressItemStatus.REVISED,
                    overrides=new_overrides,
                    created_at=item.created_at,
                )
            )
        if not found:
            raise ProgressCaptureValidationError(
                f"item_id {item_id!r} not present in capture"
            )
        return ProgressCapture(
            schema_version=capture.schema_version,
            capture_id=capture.capture_id,
            workspace=capture.workspace,
            progress_items=tuple(new_items),
            requires_user_confirmation=True,
            formally_accepted=False,
            accepted_at="",
            accepted_by="",
            created_at=capture.created_at,
        )

    @staticmethod
    def reject(
        capture: ProgressCapture,
        item_id: str,
        *,
        reason: str,
        now: str,
    ) -> ProgressCapture:
        """AC-5: mark item as REJECTED with a reason-bearing override."""
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        _check_iso_utc(now, field="now")
        _check_non_empty_str(reason, field="reason")

        new_items: list[ProgressItem] = []
        found = False
        for item in capture.progress_items:
            if item.item_id != item_id:
                new_items.append(item)
                continue
            found = True
            if item.status == ProgressItemStatus.REJECTED:
                raise ProgressCaptureConflictError(
                    f"item {item_id!r} is already REJECTED"
                )
            override = ItemOverride(
                target_path="status",
                original_value=item.status,
                edited_value=ProgressItemStatus.REJECTED,
                reason=reason,
                edited_at=now,
            )
            new_items.append(
                ProgressItem(
                    item_id=item.item_id,
                    workspace_project_id=item.workspace_project_id,
                    task_id=item.task_id,
                    kind=item.kind,
                    text=item.text,
                    source_kind=item.source_kind,
                    source_ref=item.source_ref,
                    confidence=item.confidence,
                    evidence_refs=item.evidence_refs,
                    status=ProgressItemStatus.REJECTED,
                    overrides=item.overrides + (override,),
                    created_at=item.created_at,
                )
            )
        if not found:
            raise ProgressCaptureValidationError(
                f"item_id {item_id!r} not present in capture"
            )
        return ProgressCapture(
            schema_version=capture.schema_version,
            capture_id=capture.capture_id,
            workspace=capture.workspace,
            progress_items=tuple(new_items),
            requires_user_confirmation=True,
            formally_accepted=False,
            accepted_at="",
            accepted_by="",
            created_at=capture.created_at,
        )

    @staticmethod
    def accept(
        capture: ProgressCapture,
        *,
        accepted_by: str,
        now: str,
    ) -> ProgressCapture:
        """AC-6: flip formally_accepted to True; stamp accepted_by/at."""
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        if capture.formally_accepted:
            raise ProgressCaptureConflictError(
                f"capture {capture.capture_id!r} is already formally_accepted"
            )
        _check_safe_id(accepted_by, field="accepted_by")
        _check_iso_utc(now, field="now")

        new_items = tuple(
            ProgressItem(
                item_id=item.item_id,
                workspace_project_id=item.workspace_project_id,
                task_id=item.task_id,
                kind=item.kind,
                text=item.text,
                source_kind=item.source_kind,
                source_ref=item.source_ref,
                confidence=item.confidence,
                evidence_refs=item.evidence_refs,
                status=(
                    ProgressItemStatus.ACCEPTED
                    if item.status
                    in (ProgressItemStatus.PROPOSED, ProgressItemStatus.REVISED)
                    else item.status
                ),
                overrides=item.overrides,
                created_at=item.created_at,
            )
            for item in capture.progress_items
        )
        return ProgressCapture(
            schema_version=capture.schema_version,
            capture_id=capture.capture_id,
            workspace=capture.workspace,
            progress_items=new_items,
            requires_user_confirmation=True,
            formally_accepted=True,
            accepted_at=now,
            accepted_by=accepted_by,
            created_at=capture.created_at,
        )

    @staticmethod
    def to_report_draft(capture: ProgressCapture) -> ProgressDraft:
        """AC-8: flatten an accepted capture into a US-9-bound draft.

        Raises :class:`ProgressCaptureConflictError` if the capture is
        not yet formally accepted. REJECTED items are excluded from
        every segment; the draft binds every segment entry back to its
        source :class:`ProgressItem.item_id`.
        """
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        if not capture.formally_accepted:
            raise ProgressCaptureConflictError(
                f"capture {capture.capture_id!r} is not formally_accepted; "
                "call accept() before to_report_draft()"
            )

        # All non-rejected items, segmented by kind.
        completed: list[str] = []
        pending: list[str] = []
        next_steps: list[str] = []
        blockers: list[str] = []
        ids: list[str] = []
        for item in capture.progress_items:
            if item.status == ProgressItemStatus.REJECTED:
                continue
            ids.append(item.item_id)
            if item.kind == ProgressItemKind.COMPLETED:
                completed.append(item.item_id)
            elif item.kind == ProgressItemKind.PENDING:
                pending.append(item.item_id)
            elif item.kind == ProgressItemKind.NEXT_STEP:
                next_steps.append(item.item_id)
            elif item.kind == ProgressItemKind.BLOCKER:
                blockers.append(item.item_id)

        # task_id is the same for every item (AC-1 contract).
        task_ids = {item.task_id for item in capture.progress_items}
        workspace_task_id = next(iter(task_ids)) if task_ids else ""

        draft_id = "pd." + capture.capture_id[len("pc."):] + ".1"
        return ProgressDraft(
            draft_id=draft_id,
            workspace_project_id=capture.workspace.project_id,
            workspace_task_id=workspace_task_id,
            completed_work=tuple(completed),
            pending_work=tuple(pending),
            next_steps=tuple(next_steps),
            blockers=tuple(blockers),
            source_progress_ids=tuple(ids),
        )

    @staticmethod
    def to_audit_record(capture: ProgressCapture) -> dict:
        """Project a capture into a JSON-safe audit record.

        Mirrors US-11/12/13: includes counts + status flags, EXCLUDES
        ``text``, ``confidence`` numeric values, and ``override.reason``
        free text. Sensitive business phrasing is never written into the
        audit chain.
        """
        if not isinstance(capture, ProgressCapture):
            raise ProgressCaptureValidationError(
                "capture must be a ProgressCapture instance"
            )
        items_summary: list[dict] = []
        for item in capture.progress_items:
            items_summary.append(
                {
                    "item_id": item.item_id,
                    "task_id": item.task_id,
                    "kind": item.kind.value,
                    "source_kind": item.source_kind.value,
                    "evidence_ref_count": len(item.evidence_refs),
                    "override_count": len(item.overrides),
                    "status": item.status.value,
                }
            )
        return {
            "schema_version": SCHEMA_VERSION,
            "domain": DOMAIN,
            "capture_id": capture.capture_id,
            "workspace_project_id": capture.workspace.project_id,
            "workspace_role_id": capture.workspace.role_id,
            "workspace_revision": capture.workspace.revision,
            "item_count": len(capture.progress_items),
            "items": items_summary,
            "requires_user_confirmation": capture.requires_user_confirmation,
            "formally_accepted": capture.formally_accepted,
            "accepted_by": capture.accepted_by if capture.formally_accepted else "",
            "accepted_at": capture.accepted_at if capture.formally_accepted else "",
            "created_at": capture.created_at,
        }

def _classify(ev: EvidenceInput) -> ProgressItemKind:
    """Map an :class:`EvidenceInput` to a :class:`ProgressItemKind`.

    Pure heuristic that follows AC-1/AC-2: TASK_DEPENDENCY_RESOLVED is
    always a NEXT_STEP, ARTIFACT_FILE is always COMPLETED,
    DOCUMENT_CONTENT is COMPLETED unless the text contains a "blocker"
    cue (case-insensitive), and EXPLICIT_USER_TEXT is COMPLETED unless
    the text contains "pending"/"next"/"blocker" cues.
    """
    text_lc = ev.text.lower()
    if ev.kind == EvidenceKind.TASK_DEPENDENCY_RESOLVED:
        return ProgressItemKind.NEXT_STEP
    if ev.kind == EvidenceKind.ARTIFACT_FILE:
        return ProgressItemKind.COMPLETED
    if "blocker" in text_lc or "blocked" in text_lc or "stuck" in text_lc:
        return ProgressItemKind.BLOCKER
    if "next" in text_lc or "upcoming" in text_lc or "todo" in text_lc:
        return ProgressItemKind.NEXT_STEP
    if "pending" in text_lc or "wip" in text_lc or "in progress" in text_lc:
        return ProgressItemKind.PENDING
    return ProgressItemKind.COMPLETED

def _make_item_id(project_id: str, task_id: str, index: int) -> str:
    return f"pc.{project_id}.{task_id}.{index}"

def _make_capture_id(project_id: str, now: str, item_count: int) -> str:
    # content-stable id: workspace project + safe-id-encoded UTC timestamp
    # + item count. ISO-8601 colons and "T" are replaced so the id matches
    # the project-wide safe-id regex (mirrors US-2/5/9/10/13 naming).
    safe_now = now.replace(":", "").replace("T", "t").replace(".", "p")
    return f"pc.{project_id}.{safe_now}.{item_count}"
