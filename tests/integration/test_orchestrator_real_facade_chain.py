"""US-4-AC-2 guarded real-chain integration tests."""
from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path

from src.coevo.identity.models import Actor
from src.coevo.identity.service import StaticAuthorizer, UnauthorizedError
from src.coevo.orchestrator import (
    AgentCapability, AgentRegistration, AgentRegistry, AgentSpec, AgentStatus,
    MVP_FIXED_CHAIN, OrchestrationEvent, OrchestrationEventKind,
    OrchestrationOutcome, OrchestrationStepResult, Orchestrator,
    OrchestratorConflictError, OrchestratorValidationError, RealChainExecutor,
    RealChainStore, canonical_digest,
)
from src.coevo.talent.models import (
    AvailabilityWindow, RedactedIdentity, SkillTag, Talent, TalentPool,
)
from src.coevo.talent.service import TalentRecommenderService
from src.coevo.task_decomposition.service import TaskDecompositionService
from src.coevo.task_flow.service import FlowUnderstandingService
from src.coevo.workspace.models import WorkspaceEntry
from tests.support_identity import TestFreshnessAuthority, TestSigner


NOW = "2026-08-01T04:00:00Z"
REVISION = "PRJ001-R0001"


def project_input() -> dict:
    return {
        "schema_version": "1.0", "base_revision": REVISION,
        "project_id": "PRJ001", "task_id": "t.1", "title": "Sensitive title",
        "objective": "Sensitive objective", "plan_start": "2026-08-01T00:00:00Z",
        "plan_end": "2026-08-31T00:00:00Z", "responsible_units": ["unit_a"],
        "recipient_cert_id": "CERT-RECIPIENT", "sender_cert_id": "CERT-SENDER",
        "package_type": "TASK_ASSIGNMENT", "payload_digest": "b" * 64,
        "flow": {"unit_id": "unit_a", "title": "Sensitive flow", "stages": [{
            "stage_id": "execution", "name": "execution", "nodes": [{
                "node_id": "n1", "title": "Sensitive node", "stage_hint": "execution",
                "inputs": ["requirement"], "outputs": ["result"],
                "review_criteria": ["approved"], "responsible_roles": ["tech:python"],
            }],
        }], "roles": [{"role_id": "tech.python", "name": "developer",
                        "responsibility": "delivery"}]},
    }


def event(data: dict | None = None) -> OrchestrationEvent:
    data = project_input() if data is None else data
    return OrchestrationEvent(
        "ev.001", OrchestrationEventKind.DISPATCH, "PRJ001", "t.1",
        {"schema_version": data["schema_version"], "base_revision": data["base_revision"],
         "project_input_digest": canonical_digest(data)}, NOW,
    )


def workspace() -> WorkspaceEntry:
    return WorkspaceEntry("PRJ001", "a.pm", "pkg.input", REVISION)


def registry() -> AgentRegistry:
    values = (
        ("agent.task_flow_understanding", AgentCapability.TASK_FLOW_UNDERSTANDING),
        ("agent.task_decomposition", AgentCapability.TASK_DECOMPOSITION),
        ("agent.team_recommendation", AgentCapability.TEAM_RECOMMENDATION),
        ("agent.task_package_build", AgentCapability.TASK_PACKAGE_BUILD),
    )
    result = AgentRegistry.empty()
    for agent_id, capability in values:
        result = result.register(AgentRegistration(AgentSpec(
            agent_id, capability, capability.value, ("input",), ("output",)
        )))
    return result


def executor() -> RealChainExecutor:
    talent = Talent(
        "talent.1", (SkillTag("tech:python"),), (), 0, 2,
        AvailabilityWindow("2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"),
        RedactedIdentity("pool.1", "T-1", "a" * 64),
    )
    return RealChainExecutor(
        FlowUnderstandingService(), TaskDecompositionService(),
        TalentRecommenderService(), TalentPool("pool.1", "1.0", (talent,)),
    )


def grants(actor: str, action: str) -> StaticAuthorizer:
    return StaticAuthorizer({actor: frozenset({f"orchestrator:{action}:PRJ001"})})


class GuardedChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.signer = TestSigner()
        self.freshness = TestFreshnessAuthority()
        self._next_store = 0

    def new_store(self, name: str | None = None) -> RealChainStore:
        self._next_store += 1
        path = Path(self.temporary.name) / (name or f"store-{self._next_store}.db")
        store = RealChainStore.create(
            path, signer=self.signer, freshness=self.freshness,
        )
        self.addCleanup(store.close)
        return store

    def reopen(self, path: Path) -> RealChainStore:
        store = RealChainStore.open(
            path, signer=self.signer, freshness=self.freshness,
        )
        self.addCleanup(store.close)
        return store

    def dispatch(self, store: RealChainStore, data: dict | None = None):
        data = project_input() if data is None else data
        return Orchestrator.dispatch_event_with_real_facades(
            registry(), MVP_FIXED_CHAIN, event(data), workspace=workspace(),
            executor=executor(), project_input=data, store=store, now=NOW,
        )

    def confirm(self, store: RealChainStore, held, actor_id: str = "owner.1"):
        return Orchestrator.confirm_real_chain(
            held, preview=held.package_preview, actor=Actor(actor_id),
            authorizer=grants(actor_id, "confirm-package"), store=store, now=NOW,
        )

    def test_dispatch_calls_us123_and_holds_with_frozen_preview(self) -> None:
        held = self.dispatch(self.new_store())
        self.assertEqual(OrchestrationOutcome.HELD_AT_CONFIRM, held.orch_report.outcome)
        self.assertTrue(dataclasses.is_dataclass(held.package_preview))
        self.assertEqual(REVISION, held.package_preview.base_revision)
        self.assertEqual([OrchestrationStepResult.OK] * 3 + [OrchestrationStepResult.HELD_AT_CONFIRM],
                         [item.result for item in held.orch_report.trace])

    def test_generic_confirm_is_blocked_and_authorizer_is_required(self) -> None:
        store = self.new_store()
        held = self.dispatch(store)
        with self.assertRaises(OrchestratorConflictError):
            Orchestrator.confirm_human(held.orch_report, step_index=3,
                                       confirmed_by="owner.1", now=NOW)
        with self.assertRaises(UnauthorizedError):
            Orchestrator.confirm_real_chain(
                held, preview=held.package_preview, actor=Actor("owner.1"),
                authorizer=StaticAuthorizer({}), store=store, now=NOW,
            )
        self.assertIn(
            ("confirmation_authorization", "unauthorized"),
            [(row.action, row.result) for row in store.audit_entries],
        )

    def test_confirmation_binds_preview_actor_and_held_context(self) -> None:
        store = self.new_store()
        held = self.dispatch(store)
        tampered = dataclasses.replace(held.package_preview, recipient_cert_id="CERT-OTHER")
        with self.assertRaises(OrchestratorValidationError):
            Orchestrator.confirm_real_chain(
                held, preview=tampered, actor=Actor("owner.1"),
                authorizer=grants("owner.1", "confirm-package"), store=store, now=NOW,
            )
        confirmed = self.confirm(store, held)
        self.assertEqual(OrchestrationOutcome.CONFIRMED_PENDING_PACKAGE,
                         confirmed.orch_report.outcome)
        self.assertEqual(held.package_preview, confirmed.package_preview)

    def test_confirmation_is_bound_to_store_identity(self) -> None:
        first = self.new_store()
        second = self.new_store()
        held_from_first = self.dispatch(first)
        self.dispatch(second)
        with self.assertRaises(OrchestratorValidationError):
            self.confirm(second, held_from_first)

    def test_resume_checks_step4_available_before_crypto_failure(self) -> None:
        store = self.new_store()
        held = self.dispatch(store)
        confirmed = self.confirm(store, held)
        disabled = registry().set_status("agent.task_package_build", AgentStatus.DISABLED)
        with self.assertRaises(OrchestratorValidationError):
            Orchestrator.resume_real_chain(
                confirmed, registry=disabled, chain=MVP_FIXED_CHAIN, event=event(),
                workspace=workspace(), executor=executor(), store=store, now=NOW,
            )

    def test_no_approved_crypto_returns_stable_failure_and_never_completed(self) -> None:
        store = self.new_store()
        confirmed = self.confirm(store, self.dispatch(store))
        result = Orchestrator.resume_real_chain(
            confirmed, registry=registry(), chain=MVP_FIXED_CHAIN, event=event(),
            workspace=workspace(), executor=executor(), store=store, now=NOW,
        )
        self.assertEqual(OrchestrationOutcome.ESCALATED, result.orch_report.outcome)
        self.assertEqual("CRYPTO_CAPABILITY_UNAVAILABLE", result.orch_report.trace[-1].detail)
        self.assertEqual((), result.package_summary)
        self.assertIn(("package", "CRYPTO_CAPABILITY_UNAVAILABLE"),
                      [(row.action, row.result) for row in store.audit_entries])

    def test_sqlite_reopen_preserves_replay_and_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "real-chain.db"
            first = RealChainStore.create(
                path, signer=self.signer, freshness=self.freshness,
            )
            held = self.dispatch(first)
            first.close()
            reopened = self.reopen(path)
            self.assertEqual(held, self.dispatch(reopened))
            changed = project_input(); changed["title"] = "changed"
            with self.assertRaises(OrchestratorValidationError):
                self.dispatch(reopened, changed)
            self.assertTrue(reopened.verify_audit_chain())
            reopened.close()

    def test_sqlite_reopen_replays_confirmed_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "confirmed.db"
            first = RealChainStore.create(
                path, signer=self.signer, freshness=self.freshness,
            )
            confirmed = self.confirm(first, self.dispatch(first))
            first.close()
            reopened = self.reopen(path)
            self.assertEqual(confirmed, self.dispatch(reopened))
            reopened.close()

    def test_interrupted_state_requires_authorized_manual_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "recovery.db"
            first = RealChainStore.create(
                path, signer=self.signer, freshness=self.freshness,
            )
            data = project_input(); ev = event(data)
            digest = canonical_digest({"event_id": ev.event_id, "kind": ev.kind.value,
                                       "project_id": ev.project_id, "task_id": ev.task_id,
                                       "payload": ev.payload, "triggered_at": ev.triggered_at})
            first.begin_dispatch(ev.event_id, digest, ev.project_id, NOW)
            first.close()
            reopened = self.reopen(path)
            self.assertEqual("RECOVERY_REQUIRED", reopened.recovery_context(ev.event_id).state)
            with self.assertRaises(UnauthorizedError):
                Orchestrator.recover_real_chain(
                    ev.event_id, actor=Actor("operator.1"), authorizer=StaticAuthorizer({}),
                    store=reopened, now=NOW,
                )
            self.assertIn(
                ("recovery_authorization", "unauthorized"),
                [(row.action, row.result) for row in reopened.audit_entries],
            )
            result = Orchestrator.recover_real_chain(
                ev.event_id, actor=Actor("operator.1"),
                authorizer=grants("operator.1", "recover-package"),
                store=reopened, now=NOW,
            )
            self.assertEqual("ESCALATED", result.state)
            reopened.close()

    def test_interrupted_package_build_is_not_retried_after_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "package-recovery.db"
            first = RealChainStore.create(
                path, signer=self.signer, freshness=self.freshness,
            )
            confirmed = self.confirm(first, self.dispatch(first))
            resume_digest = canonical_digest({
                "event_digest": confirmed.event_digest,
                "confirmation_digest": confirmed.confirmation_digest,
                "chain_id": confirmed.chain_id,
                "package_preview": dataclasses.asdict(confirmed.package_preview),
            })
            first.begin_resume(confirmed.event_id, confirmed.event_digest,
                               resume_digest, NOW)
            first.close()
            reopened = self.reopen(path)
            self.assertEqual(
                "RECOVERY_REQUIRED",
                reopened.recovery_context(confirmed.event_id).state,
            )
            result = Orchestrator.recover_real_chain(
                confirmed.event_id, actor=Actor("operator.1"),
                authorizer=grants("operator.1", "recover-package"),
                store=reopened, now=NOW,
            )
            self.assertEqual("ESCALATED", result.state)
            reopened.close()


if __name__ == "__main__":
    unittest.main()
