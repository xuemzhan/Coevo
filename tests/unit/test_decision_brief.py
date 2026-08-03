"""Security and acceptance tests for the US-13 decision-brief boundary."""
from __future__ import annotations

import dataclasses
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.decision_brief import (
    BRIEF_SCHEMA,
    HIGH_RISK_MIN_SEVERITY,
    MAX_AFFECTED_TASKS_PER_RISK,
    MAX_RISK_COUNT,
    MAX_RISK_STRING_BYTES,
    WPS_TOOL_ID,
    ApprovedTemplateRegistry,
    BriefConclusion,
    BriefContent,
    BriefSourceKind,
    BriefType,
    DecisionBriefConflictError,
    DecisionBriefRepository,
    DecisionBriefService,
    DecisionBriefValidationError,
    RiskConfirmationRepository,
    SourceReference,
)
from src.coevo.risk import Risk, RiskKind, RiskReport, SourceKind
from tests.unit.test_merge_commit_receipt import (
    committed,
    repository_for,
    signing_authority,
)


GENERATED_AT = "2026-08-22T00:00:00Z"
CONFIRMED_AT = "2026-08-21T01:00:00Z"
TEMPLATE = "templates/decision-brief.docx"


def _risk(
    risk_id: str,
    severity: int,
    *,
    kind: RiskKind = RiskKind.DEADLINE_OVERRUN,
    affected_tasks: tuple[str, ...] = ("TASK-001",),
    recommendation: str | None = None,
) -> Risk:
    return Risk(
        risk_id=risk_id,
        kind=kind,
        source=SourceKind.FACTUAL,
        basis=f"sensitive basis {risk_id}",
        affected_tasks=affected_tasks,
        recommendation=recommendation or f"sensitive recommendation {risk_id}",
        suggested_deadline="2026-08-23T00:00:00Z",
        severity=severity,
        rationale=f"sensitive rationale {risk_id}",
    )


def _fixture(*, risks: tuple[Risk, ...] | None = None):
    outcome = committed()
    receipt = outcome.receipt
    assert receipt is not None
    selected = risks if risks is not None else (
        _risk("risk.high", 4),
        _risk("risk.low", 3, kind=RiskKind.LONG_SILENCE),
    )
    report = RiskReport(
        merge_reporter_package_id=receipt.package_id,
        project_id=receipt.project_id,
        analysed_at="2026-08-21T00:00:00Z",
        risks=tuple(sorted(selected, key=lambda risk: risk.risk_id)),
        coordination_meeting_recommended=True,
    )
    return outcome, receipt, repository_for(outcome), report


def _write_docx(path: Path, *, macro: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>',
        )
        if macro:
            archive.writestr("word/vbaProject.bin", b"not executable in this test")


class Harness:
    def __init__(self, root: Path, *, risks: tuple[Risk, ...] | None = None) -> None:
        _, self.receipt, self.receipts, self.report = _fixture(risks=risks)
        _write_docx(root / TEMPLATE)
        self.templates = ApprovedTemplateRegistry(root)
        self.approval = self.templates.approve(
            approval_id="approval.template.1", template_ref=TEMPLATE
        )
        self.risks = RiskConfirmationRepository(signing_authority())
        self.confirmation = self.risks.confirm(
            receipt_id=self.receipt.receipt_id,
            receipt_repository=self.receipts,
            risk_report=self.report,
            confirmed_at=CONFIRMED_AT,
            confirmed_by="CERT-OWNER",
            event_id="risk.confirm.1",
        )
        self.briefs = DecisionBriefRepository()

    def generate(
        self,
        *,
        brief_type: BriefType = BriefType.STAGE,
        event_id: str = "brief.generate.1",
        period_start: str | None = None,
        period_end: str | None = None,
        topic_risk_ids: tuple[str, ...] | None = None,
    ):
        return DecisionBriefService().generate(
            receipt_id=self.receipt.receipt_id,
            receipt_repository=self.receipts,
            risk_confirmation_id=self.confirmation.confirmation_id,
            risk_repository=self.risks,
            brief_repository=self.briefs,
            brief_type=brief_type,
            template_ref=TEMPLATE,
            template_approval_id=self.approval.approval_id,
            template_registry=self.templates,
            generated_at=GENERATED_AT,
            actor_id="CERT-OWNER",
            event_id=event_id,
            period_start=period_start,
            period_end=period_end,
            topic_risk_ids=topic_risk_ids,
        )


class DecisionBriefGenerationTests(unittest.TestCase):
    def test_all_three_types_generate_four_traceable_sections(self):
        for brief_type in BriefType:
            with self.subTest(brief_type=brief_type), tempfile.TemporaryDirectory() as tmp:
                harness = Harness(Path(tmp))
                kwargs = {}
                if brief_type is BriefType.RISK_TOPIC:
                    # AC-5: risk-topic briefs are focused on explicit topic risks.
                    kwargs["topic_risk_ids"] = ("risk.high",)
                brief = harness.generate(brief_type=brief_type, **kwargs)
                content = brief.current.content
                self.assertTrue(content.overall_progress)
                self.assertTrue(content.important_changes)
                self.assertEqual(1, len(content.high_risk_items))
                self.assertEqual(1, len(content.pending_decisions))
                self.assertEqual(harness.receipt.receipt_id, brief.current.source_receipt_id)
                for section in content.sections:
                    for conclusion in section:
                        self.assertTrue(conclusion.sources)
                        self.assertEqual(
                            tuple(sorted(
                                conclusion.sources,
                                key=lambda source: (
                                    source.kind.value, source.reference_id,
                                ),
                            )),
                            conclusion.sources,
                        )

    def test_high_risk_boundary_and_output_are_stable(self):
        risks = (
            _risk("risk.3", 3),
            _risk("risk.4", HIGH_RISK_MIN_SEVERITY),
            _risk("risk.5", 5),
        )
        with tempfile.TemporaryDirectory() as tmp:
            first_harness = Harness(Path(tmp), risks=risks)
            first = first_harness.generate(brief_type=BriefType.PERIODIC)
            replay = first_harness.generate(brief_type=BriefType.PERIODIC)
            self.assertEqual(first, replay)
            self.assertEqual(
                ("risk.risk.4", "risk.risk.5"),
                tuple(item.conclusion_id for item in first.current.content.high_risk_items),
            )

    def test_bare_or_forged_risk_report_cannot_reach_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            common = dict(
                receipt_id=harness.receipt.receipt_id,
                receipt_repository=harness.receipts,
                risk_confirmation_id=harness.confirmation.confirmation_id,
                brief_repository=harness.briefs,
                brief_type=BriefType.STAGE,
                template_ref=TEMPLATE,
                template_approval_id=harness.approval.approval_id,
                template_registry=harness.templates,
                generated_at=GENERATED_AT,
                actor_id="CERT-OWNER",
                event_id="brief.forgery",
            )
            with self.assertRaises(DecisionBriefValidationError):
                DecisionBriefService().generate(
                    risk_repository=object(),
                    **common,
                )
            forged = dataclasses.replace(
                harness.report,
                risks=(_risk("risk.injected", 5),),
            )
            stored_confirmation = next(iter(harness.risks._items.values()))
            object.__setattr__(stored_confirmation, "report", forged)
            with self.assertRaisesRegex(
                DecisionBriefValidationError, "(digest|binding) mismatch"
            ):
                DecisionBriefService().generate(
                    risk_repository=harness.risks,
                    **common,
                )

    def test_confirmation_binds_latest_receipt_snapshot_and_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            report = dataclasses.replace(
                harness.report, merge_reporter_package_id="forged.package"
            )
            with self.assertRaises(DecisionBriefValidationError):
                harness.risks.confirm(
                    receipt_id=harness.receipt.receipt_id,
                    receipt_repository=harness.receipts,
                    risk_report=report,
                    confirmed_at=CONFIRMED_AT,
                    confirmed_by="CERT-OWNER",
                    event_id="risk.bad.package",
                )
            stored_confirmation = next(iter(harness.risks._items.values()))
            object.__setattr__(stored_confirmation, "snapshot_digest", "0" * 64)
            with self.assertRaisesRegex(
                DecisionBriefValidationError, "binding mismatch"
            ):
                harness.generate(event_id="brief.bad.snapshot")

    def test_stale_project_receipt_is_rejected(self):
        first = committed()
        first_receipt = first.receipt
        assert first_receipt is not None
        from tests.unit.test_merge_commit_receipt import report
        second = committed(
            current_baseline=first.proposal.new_baseline,
            manifest=report(version=2, sequence_no=2),
            store=first.proposal.record.store_post,
            receipt_repository=repository_for(first),
        )
        stale_report = RiskReport(
            merge_reporter_package_id=first_receipt.package_id,
            project_id=first_receipt.project_id,
            analysed_at="2026-08-21T00:00:00Z",
            risks=(),
            coordination_meeting_recommended=False,
        )
        with self.assertRaisesRegex(DecisionBriefValidationError, "latest"):
            RiskConfirmationRepository(signing_authority()).confirm(
                receipt_id=first_receipt.receipt_id,
                receipt_repository=repository_for(second),
                risk_report=stale_report,
                confirmed_at=CONFIRMED_AT,
                confirmed_by="CERT-OWNER",
                event_id="risk.stale",
            )

    def test_confirmation_requires_owner_identity_on_actor_and_key(self):
        _, receipt, receipts, report = _fixture()
        owner_authority = signing_authority()
        owner_repository = RiskConfirmationRepository(owner_authority)
        with self.assertRaisesRegex(DecisionBriefValidationError, "identities"):
            owner_repository.confirm(
                receipt_id=receipt.receipt_id,
                receipt_repository=receipts,
                risk_report=report,
                confirmed_at=CONFIRMED_AT,
                confirmed_by="CERT-ATTACKER",
                event_id="risk.attacker.actor",
            )
        self.assertFalse(owner_repository._items)
        self.assertFalse(owner_repository._events)
        self.assertFalse(owner_authority.service.audit_trail)

        other_reference = dataclasses.replace(
            owner_authority.reference,
            bound_certificate_id="CERT-ATTACKER",
        )
        other_authority = dataclasses.replace(
            owner_authority,
            reference=other_reference,
            signer_certificate_id="CERT-ATTACKER",
        )
        other_repository = RiskConfirmationRepository(other_authority)
        with self.assertRaisesRegex(DecisionBriefValidationError, "identities"):
            other_repository.confirm(
                receipt_id=receipt.receipt_id,
                receipt_repository=receipts,
                risk_report=report,
                confirmed_at=CONFIRMED_AT,
                confirmed_by="CERT-OWNER",
                event_id="risk.attacker.key",
            )
        self.assertFalse(other_repository._items)
        self.assertFalse(other_repository._events)
        self.assertFalse(other_authority.service.audit_trail)

    def test_unknown_affected_task_is_rejected_atomically(self):
        _, receipt, receipts, report = _fixture(
            risks=(_risk("risk.unknown", 5, affected_tasks=("TASK-UNKNOWN",)),)
        )
        authority = signing_authority()
        repository = RiskConfirmationRepository(authority)
        with self.assertRaisesRegex(
            DecisionBriefValidationError, "outside the confirmed baseline"
        ):
            repository.confirm(
                receipt_id=receipt.receipt_id,
                receipt_repository=receipts,
                risk_report=report,
                confirmed_at=CONFIRMED_AT,
                confirmed_by="CERT-OWNER",
                event_id="risk.unknown.task",
            )
        self.assertFalse(repository._items)
        self.assertFalse(repository._events)
        self.assertFalse(authority.service.audit_trail)


class BriefTypeContentTests(unittest.TestCase):
    def test_periodic_brief_includes_period_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            brief = harness.generate(
                brief_type=BriefType.PERIODIC,
                period_start="2026-08-01T00:00:00Z",
                period_end="2026-08-31T00:00:00Z",
                event_id="brief.generate.periodic.1",
            )
            content = brief.current.content
            self.assertIn(
                "2026-08-01T00:00:00Z -> 2026-08-31T00:00:00Z", content.title
            )
            self.assertIn(
                "for report period 2026-08-01T00:00:00Z to 2026-08-31T00:00:00Z",
                content.overall_progress[0].text,
            )

    def test_risk_topic_brief_focuses_topic_risks(self):
        risks = (
            _risk("risk.high", 4),
            _risk("risk.low", 3, kind=RiskKind.LONG_SILENCE),
            _risk("risk.topic", 5),
        )
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp), risks=risks)
            brief = harness.generate(
                brief_type=BriefType.RISK_TOPIC,
                topic_risk_ids=("risk.topic",),
                event_id="brief.generate.topic.1",
            )
            content = brief.current.content
            self.assertIn("[risk.topic]", content.title)
            ids = tuple(
                item.conclusion_id
                for section in content.sections
                for item in section
            )
            self.assertIn("decision.risk.topic", ids)
            self.assertIn("risk.risk.topic", ids)
            self.assertNotIn("risk.high", " ".join(ids))
            self.assertNotIn("risk.low", " ".join(ids))
            for section in content.sections:
                for conclusion in section:
                    self.assertNotIn("risk.low", conclusion.text)

    def test_risk_topic_requires_existing_topic_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.RISK_TOPIC,
                    topic_risk_ids=("risk.ghost",),
                    event_id="brief.generate.bad-topic.1",
                )
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.RISK_TOPIC,
                    topic_risk_ids=("risk.high", "risk.high"),
                    event_id="brief.generate.dup-topic.1",
                )

    def test_periodic_requires_both_bounds_and_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.PERIODIC,
                    period_start="2026-08-01T00:00:00Z",
                    event_id="brief.generate.partial.1",
                )
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.PERIODIC,
                    period_start="2026-08-31T00:00:00Z",
                    period_end="2026-08-01T00:00:00Z",
                    event_id="brief.generate.inverted.1",
                )

    def test_cross_type_parameters_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.STAGE,
                    topic_risk_ids=("risk.high",),
                    event_id="brief.generate.stage-topic.1",
                )
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.PERIODIC,
                    topic_risk_ids=("risk.high",),
                    event_id="brief.generate.periodic-topic.1",
                )
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.RISK_TOPIC,
                    period_start="2026-08-01T00:00:00Z",
                    topic_risk_ids=("risk.high",),
                    event_id="brief.generate.topic-period.1",
                )
            with self.assertRaises(DecisionBriefValidationError):
                harness.generate(
                    brief_type=BriefType.RISK_TOPIC,
                    event_id="brief.generate.topic-missing.1",
                )


class ResourceLimitTests(unittest.TestCase):
    def test_risk_count_and_total_string_caps_fail_before_brief_allocation(self):
        too_many = tuple(
            _risk(f"risk.{index:04d}", 1) for index in range(MAX_RISK_COUNT + 1)
        )
        oversized = _risk(
            "risk.big",
            5,
            recommendation="界" * (MAX_RISK_STRING_BYTES // 3 + 1),
        )
        for risks in (too_many, (oversized,)):
            with self.subTest(count=len(risks)), tempfile.TemporaryDirectory() as tmp:
                _, receipt, receipts, report = _fixture(risks=risks)
                repository = RiskConfirmationRepository(signing_authority())
                with self.assertRaisesRegex(DecisionBriefValidationError, "exceeds"):
                    repository.confirm(
                        receipt_id=receipt.receipt_id,
                        receipt_repository=receipts,
                        risk_report=report,
                        confirmed_at=CONFIRMED_AT,
                        confirmed_by="CERT-OWNER",
                        event_id="risk.limit",
                    )

    def test_affected_task_cap_is_enforced(self):
        tasks = tuple(f"TASK-{index:04d}" for index in range(
            MAX_AFFECTED_TASKS_PER_RISK + 1
        ))
        report_risk = _risk("risk.tasks", 5, affected_tasks=tasks)
        _, receipt, receipts, report = _fixture(risks=(report_risk,))
        with self.assertRaisesRegex(DecisionBriefValidationError, "task count"):
            RiskConfirmationRepository(signing_authority()).confirm(
                receipt_id=receipt.receipt_id,
                receipt_repository=receipts,
                risk_report=report,
                confirmed_at=CONFIRMED_AT,
                confirmed_by="CERT-OWNER",
                event_id="risk.task.limit",
            )


class TemplateRegistryTests(unittest.TestCase):
    def test_request_binds_approval_digest_and_is_copy_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            request = harness.generate().wps_request
            self.assertEqual(WPS_TOOL_ID, request.tool_id)
            self.assertEqual(harness.approval.approval_id, request.template_approval_id)
            self.assertEqual(harness.approval.template_digest, request.template_digest)
            self.assertEqual("generate_copy", request.operation)
            self.assertEqual("new_version", request.save_mode)
            self.assertFalse(request.macros_allowed)
            self.assertTrue(request.requires_user_confirmation)
            with self.assertRaises(DecisionBriefValidationError):
                dataclasses.replace(request, macros_allowed=True)

    def test_changed_macro_nonzip_and_unapproved_templates_are_rejected(self):
        cases = ("changed", "macro", "nonzip", "unapproved")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                harness = Harness(root)
                if case == "changed":
                    _write_docx(root / TEMPLATE)
                    with (root / TEMPLATE).open("ab") as stream:
                        stream.write(b"changed")
                elif case == "macro":
                    _write_docx(root / TEMPLATE, macro=True)
                elif case == "nonzip":
                    (root / TEMPLATE).write_bytes(b"not a DOCX")
                elif case == "unapproved":
                    harness.approval = dataclasses.replace(
                        harness.approval, approval_id="missing"
                    )
                with self.assertRaises(DecisionBriefValidationError):
                    harness.generate(event_id=f"brief.template.{case}")

    def test_symlink_template_is_rejected_when_platform_allows_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_docx(root / "real.docx")
            (root / "templates").mkdir()
            link = root / TEMPLATE
            try:
                os.symlink(root / "real.docx", link)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            registry = ApprovedTemplateRegistry(root)
            with self.assertRaisesRegex(DecisionBriefValidationError, "links"):
                registry.approve(approval_id="approval.link", template_ref=TEMPLATE)

    def test_revision_reverifies_template_and_failure_is_atomic(self):
        for attack in ("tamper", "macro"):
            with self.subTest(attack=attack), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                harness = Harness(root)
                brief = harness.generate()
                if attack == "tamper":
                    with (root / TEMPLATE).open("ab") as stream:
                        stream.write(b"changed-after-generation")
                else:
                    _write_docx(root / TEMPLATE, macro=True)
                with self.assertRaises(DecisionBriefValidationError):
                    DecisionBriefService().revise(
                        brief_id=brief.brief_id,
                        brief_repository=harness.briefs,
                        content=dataclasses.replace(
                            brief.current.content, title="must not persist"
                        ),
                        editor_id="USER-OWNER",
                        edit_reason="template attack",
                        edited_at="2026-08-22T01:00:00Z",
                        expected_revision=1,
                        expected_head_digest=brief.head_digest,
                        event_id=f"brief.revise.template.{attack}",
                        template_registry=harness.templates,
                    )
                current = harness.briefs.get(brief.brief_id)
                self.assertEqual(1, current.current.revision)
                self.assertEqual(brief.head_digest, current.head_digest)
                self.assertNotIn(
                    f"brief.revise.template.{attack}", harness.briefs._events
                )

    def test_revision_rejects_substitute_registry_with_changed_approval_bytes(self):
        with (
            tempfile.TemporaryDirectory() as approved_tmp,
            tempfile.TemporaryDirectory() as substitute_tmp,
        ):
            harness = Harness(Path(approved_tmp))
            brief = harness.generate()
            substitute_root = Path(substitute_tmp)
            substitute_path = substitute_root / TEMPLATE
            _write_docx(substitute_path)
            with zipfile.ZipFile(
                substitute_path, "a", compression=zipfile.ZIP_DEFLATED
            ) as archive:
                archive.writestr("word/styles.xml", "<styles/>")
            substitute_registry = ApprovedTemplateRegistry(substitute_root)
            substitute_registry.approve(
                approval_id=brief.wps_request.template_approval_id,
                template_ref=brief.wps_request.template_ref,
            )
            with self.assertRaisesRegex(
                DecisionBriefValidationError, "does not match"
            ):
                DecisionBriefService().revise(
                    brief_id=brief.brief_id,
                    brief_repository=harness.briefs,
                    content=dataclasses.replace(
                        brief.current.content, title="must not persist"
                    ),
                    editor_id="USER-OWNER",
                    edit_reason="substitute template registry",
                    edited_at="2026-08-22T01:00:00Z",
                    expected_revision=brief.current.revision,
                    expected_head_digest=brief.head_digest,
                    event_id="brief.revise.substitute.registry",
                    template_registry=substitute_registry,
                )
            current = harness.briefs.get(brief.brief_id)
            self.assertEqual(brief.head_digest, current.head_digest)
            self.assertNotIn(
                "brief.revise.substitute.registry", harness.briefs._events
            )


class RevisionRepositoryTests(unittest.TestCase):
    def test_cas_prevents_forks_and_idempotent_event_replay_is_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            brief = harness.generate()
            service = DecisionBriefService()
            edited = dataclasses.replace(
                brief.current.content, title="Reviewed stage brief"
            )
            kwargs = dict(
                brief_id=brief.brief_id,
                brief_repository=harness.briefs,
                content=edited,
                editor_id="USER-OWNER",
                edit_reason="clarified title",
                edited_at="2026-08-22T01:00:00Z",
                expected_revision=brief.current.revision,
                expected_head_digest=brief.head_digest,
                event_id="brief.revise.1",
                template_registry=harness.templates,
            )
            v2 = service.revise(**kwargs)
            self.assertEqual(v2, service.revise(**kwargs))
            self.assertEqual(brief.head_digest, v2.current.previous_version_digest)
            self.assertNotEqual(brief.head_digest, v2.head_digest)
            with self.assertRaisesRegex(DecisionBriefConflictError, "stale"):
                service.revise(
                    **{
                        **kwargs,
                        "event_id": "brief.revise.fork",
                        "content": dataclasses.replace(edited, title="Fork"),
                    }
                )
            with self.assertRaisesRegex(DecisionBriefConflictError, "event ID"):
                service.revise(
                    **{
                        **kwargs,
                        "content": dataclasses.replace(edited, title="Replay attack"),
                    }
                )

    def test_version_content_and_hash_chain_tampering_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = Harness(Path(tmp)).generate()
            changed = dataclasses.replace(
                brief.current.content, title="tampered"
            )
            with self.assertRaisesRegex(
                DecisionBriefValidationError, "content digest"
            ):
                dataclasses.replace(brief.current, content=changed)
            with self.assertRaisesRegex(
                DecisionBriefValidationError, "version digest"
            ):
                dataclasses.replace(brief.current, previous_version_digest="1" * 64)

    def test_old_create_and_revision_events_cannot_replay_over_new_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            service = DecisionBriefService()
            v1 = harness.generate(event_id="brief.create.old")
            v2 = service.revise(
                brief_id=v1.brief_id,
                brief_repository=harness.briefs,
                content=dataclasses.replace(v1.current.content, title="version two"),
                editor_id="USER-OWNER",
                edit_reason="first edit",
                edited_at="2026-08-22T01:00:00Z",
                expected_revision=1,
                expected_head_digest=v1.head_digest,
                event_id="brief.revise.old",
                template_registry=harness.templates,
            )
            with self.assertRaisesRegex(DecisionBriefConflictError, "stale"):
                harness.generate(event_id="brief.create.old")
            self.assertEqual(v2.head_digest, harness.briefs.get(v1.brief_id).head_digest)

            v3 = service.revise(
                brief_id=v2.brief_id,
                brief_repository=harness.briefs,
                content=dataclasses.replace(v2.current.content, title="version three"),
                editor_id="USER-OWNER",
                edit_reason="second edit",
                edited_at="2026-08-22T02:00:00Z",
                expected_revision=2,
                expected_head_digest=v2.head_digest,
                event_id="brief.revise.new",
                template_registry=harness.templates,
            )
            old_event_count = len(harness.briefs._events)
            with self.assertRaisesRegex(DecisionBriefConflictError, "stale"):
                service.revise(
                    brief_id=v1.brief_id,
                    brief_repository=harness.briefs,
                    content=dataclasses.replace(v1.current.content, title="version two"),
                    editor_id="USER-OWNER",
                    edit_reason="first edit",
                    edited_at="2026-08-22T01:00:00Z",
                    expected_revision=1,
                    expected_head_digest=v1.head_digest,
                    event_id="brief.revise.old",
                    template_registry=harness.templates,
                )
            current = harness.briefs.get(v1.brief_id)
            self.assertEqual(v3.head_digest, current.head_digest)
            self.assertEqual(old_event_count, len(harness.briefs._events))

    def test_revision_cannot_introduce_unverified_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Harness(Path(tmp))
            brief = harness.generate()
            original = brief.current.content
            forged = dataclasses.replace(
                original,
                overall_progress=(
                    dataclasses.replace(
                        original.overall_progress[0],
                        sources=(SourceReference(
                            BriefSourceKind.TASK, "TASK-NOT-CONFIRMED"
                        ),),
                    ),
                ),
            )
            with self.assertRaisesRegex(
                DecisionBriefValidationError, "unverified source"
            ):
                DecisionBriefService().revise(
                    brief_id=brief.brief_id,
                    brief_repository=harness.briefs,
                    content=forged,
                    editor_id="USER-OWNER",
                    edit_reason="unsupported conclusion",
                    edited_at="2026-08-22T01:00:00Z",
                    expected_revision=1,
                    expected_head_digest=brief.head_digest,
                    event_id="brief.revise.forged",
                    template_registry=harness.templates,
                )


class ModelAndAuditTests(unittest.TestCase):
    def test_conclusions_reject_missing_duplicate_and_unstable_sources(self):
        task = SourceReference(BriefSourceKind.TASK, "TASK-001")
        risk = SourceReference(BriefSourceKind.RISK, "risk.1")
        for sources in ((), (task, task), (task, risk)):
            with self.subTest(sources=sources), self.assertRaises(
                DecisionBriefValidationError
            ):
                BriefConclusion(conclusion_id="c.1", text="text", sources=sources)

    def test_audit_projection_excludes_sensitive_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = Harness(Path(tmp)).generate()
            record = DecisionBriefService().to_audit_record(brief)
            self.assertEqual(BRIEF_SCHEMA, record["schema_version"])
            self.assertTrue(record["requires_user_review"])
            self.assertFalse(record["formally_released"])
            self.assertEqual(brief.head_digest, record["head_digest"])
            rendered = repr(record).lower()
            for forbidden in (
                "sensitive basis",
                "sensitive recommendation",
                "sensitive rationale",
                "latest task status",
                "decision required",
                "title",
                "text",
            ):
                self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
