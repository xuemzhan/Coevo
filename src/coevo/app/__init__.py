"""Offline Coevo demo composition root (MVP closed loop).

This is the application-level wiring the MVP previously lacked: it
composes the pure facades into one runnable offline pipeline:

1. ensure the locked GmSSL test PKI profile exists;
2. run the real five-step orchestration chain (US-1/2/3 + human confirm
   + US-5 package build) against a real encrypted ``.agent`` package;
3. export the encrypted package to an outbox and verify it by parsing,
   decrypting and verifying the signature;
4. snapshot cockpit workspace/role views and (optionally) start the
   local HTTP cockpit;
5. aggregate a knowledge bundle and persist it into a fresh
   ``KnowledgeStore``;
6. publish audit events over an ``AuditStreamHub``.

Demo-only pieces (clearly non-production):
* :class:`DemoSigner` / :class:`DemoFreshnessAuthority` -- in-memory
  stand-ins for the audit anchor signer/freshness authority; production
  uses the Windows CNG-backed implementations and an approved
  private-key handle.
* The GmSSL 3.2.0 prototype provider is used under its locked
  ``mvp-prototype`` scope, never as an approved product.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.coevo.identity.audit_anchor import AuditAnchorError, canonical


ROOT = Path(__file__).resolve().parents[3]

DEMO_PROFILE: str = "demo"
DEMO_REVISION: str = "PRJ001-R0001"
DEMO_ACTOR: str = "u.pm"


def now_utc_iso_z() -> str:
    """Return the current UTC time as an ISO-8601 ``Z`` string."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Demo-only audit anchor support
# ---------------------------------------------------------------------------


class _DemoAuditAnchorError(AuditAnchorError):
    pass


class DemoSigner:
    """Demo-only HMAC signer (production: WindowsCertificateSigner)."""

    def __init__(self) -> None:
        self.secret = os.urandom(32)

    def sign(self, content: bytes) -> bytes:
        return hmac.new(self.secret, content, hashlib.sha256).digest()

    def verify(self, content: bytes, signature: bytes) -> None:
        if not hmac.compare_digest(self.sign(content), signature):
            raise _DemoAuditAnchorError("demo signature mismatch")


class DemoFreshnessAuthority:
    """In-memory stand-in for the identity freshness authority."""

    def __init__(self) -> None:
        self._markers: dict[str, tuple[dict, bytes]] = {}
        self._known: dict[str, tuple[dict, bytes]] = {}
        self._certificates: set[str] = set()
        self._keys: set[str] = set()
        self._retired: dict[str, bytes] = {}
        self._retirements: dict[str, tuple[bytes, bytes, bytes | None]] = {}

    def create_marker(self, store_id: str, generation: int, binding: str) -> dict:
        token = os.urandom(20).hex().upper()
        key_id = "CoevoDemoMarker-" + os.urandom(16).hex()
        marker = {
            "store_id": store_id,
            "generation": generation,
            "binding_sha256": binding,
            "token": token,
            "key_id": key_id,
            "key_public_sha256": os.urandom(32).hex(),
            "transition_id": str(uuid.uuid4()),
        }
        stored = (dict(marker), os.urandom(32))
        self._markers[token] = stored
        self._known[token] = stored
        self._certificates.add(token)
        self._keys.add(key_id)
        return marker

    def _stored(self, marker: dict) -> tuple[dict, bytes]:
        stored = self._known.get(marker.get("token"))
        if stored is None or stored[0] != marker:
            raise _DemoAuditAnchorError("demo freshness marker mismatch")
        return stored

    def verify_marker(self, marker: dict) -> None:
        self._stored(marker)
        token = marker["token"]
        if token not in self._certificates or marker["key_id"] not in self._keys:
            raise _DemoAuditAnchorError("demo freshness marker is unavailable")

    def delete_marker(self, marker: dict) -> None:
        self._stored(marker)
        self._keys.discard(marker["key_id"])
        self._certificates.discard(marker["token"])
        self._retired[marker["token"]] = self._markers.pop(marker["token"], (None, b""))[1]

    def verify_retired(self, marker: dict) -> None:
        self._stored(marker)
        if marker["key_id"] in self._keys or marker["token"] in self._certificates:
            raise _DemoAuditAnchorError("demo retirement is incomplete")

    def sign(self, content: bytes, marker: dict) -> bytes:
        self.verify_marker(marker)
        return hmac.new(self._markers[marker["token"]][1], content, hashlib.sha256).digest()

    def verify_signature(self, content: bytes, signature: bytes, marker: dict) -> None:
        stored = self._known.get(marker.get("token"))
        secret = stored[1] if stored is not None else self._retired.get(marker.get("token"))
        if secret is None or not hmac.compare_digest(
            hmac.new(secret, content, hashlib.sha256).digest(), signature
        ):
            raise _DemoAuditAnchorError("demo marker signature mismatch")

    def store_retirement(
        self,
        tombstone: dict,
        main_signature: bytes,
        survivor_signature: bytes | None,
    ) -> None:
        token = tombstone["target_marker"]["token"]
        value = (canonical(tombstone), main_signature, survivor_signature)
        if token in self._retirements and self._retirements[token] != value:
            raise _DemoAuditAnchorError("conflicting demo retirement tombstone")
        self._retirements[token] = value

    def load_retirement(self, tombstone: dict) -> tuple[bytes, bytes, bytes | None]:
        try:
            return self._retirements[tombstone["target_marker"]["token"]]
        except KeyError as exc:
            raise _DemoAuditAnchorError("demo retirement tombstone is missing") from exc


# ---------------------------------------------------------------------------
# Sample project input (canonical US-1 flow schema)
# ---------------------------------------------------------------------------


def sample_project_input() -> dict[str, Any]:
    """A valid cross-unit task input for the demo fixed chain."""
    return {
        "schema_version": "1.0",
        "base_revision": DEMO_REVISION,
        "project_id": "PRJ001",
        "task_id": "t.1",
        "title": "Ship offline MVP demo",
        "objective": "Prove the distributed task management loop offline",
        "plan_start": "2026-08-01T00:00:00Z",
        "plan_end": "2026-08-31T00:00:00Z",
        "responsible_units": ["unit_a"],
        "recipient_cert_id": "CERT-RECIPIENT",
        "sender_cert_id": "CERT-SENDER",
        "package_type": "TASK_ASSIGNMENT",
        "payload_digest": "b" * 64,
        "flow": {
            "unit_id": "unit_a",
            "title": "Offline MVP flow",
            "stages": [{
                "stage_id": "execution",
                "name": "execution",
                "nodes": [{
                    "node_id": "n1",
                    "title": "Implement demo",
                    "stage_hint": "execution",
                    "inputs": ["requirement"],
                    "outputs": ["result"],
                    "review_criteria": ["approved"],
                    "responsible_roles": ["tech:python"],
                }],
            }],
            "roles": [{
                "role_id": "tech.python",
                "name": "developer",
                "responsibility": "delivery",
            }],
        },
    }


# ---------------------------------------------------------------------------
# Demo environment + pipeline
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DemoResult:
    """Everything the demo run produced, for verification and display."""

    runtime_dir: Path
    outcome: str
    package_path: Path | None
    package_wire_sha256: str
    knowledge_bundle_id: str
    audit_event_count: int
    cockpit_url: str
    store: Any
    hub: Any
    cockpit_server: Any | None = None


def ensure_demo_profile() -> Path:
    """Ensure the locked demo PKI profile exists (generates it offline)."""
    profile_dir = ROOT / "loop" / "runtime" / "sm2-test-pki" / DEMO_PROFILE
    if (profile_dir / "receipt.json").is_file():
        return profile_dir
    profile_dir.parent.mkdir(parents=True, exist_ok=True)
    powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / (
        "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    result = subprocess.run(
        [
            str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-File",
            str(ROOT / "scripts" / "generate-sm2-test-pki.ps1"),
            "-ProfileName", DEMO_PROFILE,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"demo PKI generation failed: {result.stderr[-2000:]}")
    return profile_dir


def run_demo_pipeline(
    runtime_dir: Path,
    *,
    now: str | None = None,
    with_cockpit: bool = False,
    cockpit_port: int = 12751,
) -> DemoResult:
    """Execute the whole offline MVP loop and return the results."""
    from src.coevo.crypto import GmsslPrototypeProvider
    from src.coevo.identity.models import Actor
    from src.coevo.identity.service import StaticAuthorizer
    from src.coevo.knowledge_base import (
        KnowledgeBaseFacade,
        KnowledgeStore,
    )
    from src.coevo.orchestrator import (
        MVP_FIXED_CHAIN,
        AgentCapability,
        AgentRegistration,
        AgentRegistry,
        AgentSpec,
        OrchestrationEvent,
        OrchestrationEventKind,
        OrchestrationOutcome,
        Orchestrator,
        RealChainExecutor,
        RealChainStore,
        canonical_digest,
    )
    from src.coevo.audit_governance import (
        AuditEvent,
        AuditEventSource,
        AuditStreamHub,
    )
    from src.coevo.cockpit import (
        ArtifactSummary,
        CockpitHttpConfig,
        CockpitHttpServer,
        MilestoneSummary,
        RoleView,
        TaskSummary,
        WorkspaceView,
    )
    from src.coevo.talent.models import (
        AvailabilityWindow,
        RedactedIdentity,
        SkillTag,
        Talent,
        TalentPool,
    )
    from src.coevo.talent.service import TalentRecommenderService
    from src.coevo.task_decomposition.service import TaskDecompositionService
    from src.coevo.task_flow.service import FlowUnderstandingService
    from src.coevo.workspace.models import WorkspaceEntry

    now = now or now_utc_iso_z()
    runtime_dir = Path(runtime_dir)
    run_dir = runtime_dir / f"run-{uuid.uuid4().hex[:12]}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Crypto provider + test PKI (mvp-prototype scope).
    ensure_demo_profile()
    provider = GmsslPrototypeProvider(ROOT)
    sender_handle = provider.sender_handle(DEMO_PROFILE, "CERT-SENDER")
    recipient_handle = provider.recipient_handle(DEMO_PROFILE, "CERT-RECIPIENT")

    # 2. Real chain environment.
    store = RealChainStore.create(
        run_dir / "real-chain.db",
        signer=DemoSigner(),
        freshness=DemoFreshnessAuthority(),
    )
    talent = Talent(
        "talent.1",
        (SkillTag("tech:python"),),
        (),
        0,
        2,
        AvailabilityWindow("2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"),
        RedactedIdentity("pool.1", "T-1", "a" * 64),
    )
    executor = RealChainExecutor(
        FlowUnderstandingService(),
        TaskDecompositionService(),
        TalentRecommenderService(),
        TalentPool("pool.1", "1.0", (talent,)),
    )
    registry = AgentRegistry.empty()
    for agent_id, capability in (
        ("agent.task_flow_understanding", AgentCapability.TASK_FLOW_UNDERSTANDING),
        ("agent.task_decomposition", AgentCapability.TASK_DECOMPOSITION),
        ("agent.team_recommendation", AgentCapability.TEAM_RECOMMENDATION),
        ("agent.task_package_build", AgentCapability.TASK_PACKAGE_BUILD),
    ):
        registry = registry.register(AgentRegistration(AgentSpec(
            agent_id, capability, capability.value, ("input",), ("output",)
        )))
    project_input = sample_project_input()
    event = OrchestrationEvent(
        "ev.demo.001",
        OrchestrationEventKind.DISPATCH,
        "PRJ001",
        "t.1",
        {
            "schema_version": project_input["schema_version"],
            "base_revision": project_input["base_revision"],
            "project_input_digest": canonical_digest(project_input),
        },
        now,
    )
    workspace = WorkspaceEntry("PRJ001", "a.pm", "pkg.input", DEMO_REVISION)

    # 3. Run the guarded five-step chain.
    held = Orchestrator.dispatch_event_with_real_facades(
        registry,
        MVP_FIXED_CHAIN,
        event,
        workspace=workspace,
        executor=executor,
        project_input=project_input,
        store=store,
        now=now,
    )
    confirmed = Orchestrator.confirm_real_chain(
        held,
        preview=held.package_preview,
        actor=Actor(DEMO_ACTOR),
        authorizer=StaticAuthorizer({
            DEMO_ACTOR: frozenset({"orchestrator:confirm-package:PRJ001"}),
        }),
        store=store,
        now=now,
    )
    completed = Orchestrator.resume_real_chain(
        confirmed,
        registry=registry,
        chain=MVP_FIXED_CHAIN,
        event=event,
        workspace=workspace,
        executor=executor,
        store=store,
        now=now,
        crypto_provider=provider,
        sender_handle=sender_handle,
        recipient_handle=recipient_handle,
    )
    if completed.orch_report.outcome != OrchestrationOutcome.COMPLETED:
        raise RuntimeError(
            f"demo chain did not complete: {completed.orch_report.outcome}"
        )
    wire_sha256 = (
        completed.package_summary[-1].split("sha256=", 1)[1].split(";", 1)[0]
        if completed.package_summary
        else ""
    )

    # 4. Export a real encrypted package to the outbox and verify it.
    from src.coevo.protocol import (
        build_encrypted_package,
        build_envelope_template,
        open_encrypted_package,
        parse_package_bytes,
    )
    outbox = run_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    envelope = build_envelope_template(
        sender_cert_id="CERT-SENDER",
        recipient_cert_id="CERT-RECIPIENT",
        project_id="PRJ001",
        package_type="TASK_ASSIGNMENT",
        sequence_no=1,
        payload_length=0,
        created_at=now,
        expires_at="2027-08-02T00:00:00Z",
    )
    manifest = {
        "event_id": "ev.demo.001",
        "project_id": "PRJ001",
        "task_id": "t.1",
        "base_revision": DEMO_REVISION,
        "payload_digest": project_input["payload_digest"],
    }
    content = json.dumps(
        {
            "title": project_input["title"],
            "objective": project_input["objective"],
            "flow_summary": list(completed.flow_understanding_summary),
            "baseline_summary": list(completed.baseline_summary),
            "recommendations": list(completed.recommendation_summary),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    package = build_encrypted_package(
        envelope=envelope,
        manifest=manifest,
        content=content,
        provider=provider,
        sender_handle=sender_handle,
        recipient_handle=recipient_handle,
        signed_at=now,
    )
    parsed = parse_package_bytes(package.to_bytes())
    opened = open_encrypted_package(
        parsed,
        provider=provider,
        recipient_handle=recipient_handle,
        sender_handle=sender_handle,
    )
    if opened.content != content:
        raise RuntimeError("demo package round-trip verification failed")
    package_path = outbox / (
        f"TASK_ASSIGNMENT_PRJ001_{parsed.envelope.package_id}.agent"
    )
    package_path.write_bytes(package.to_bytes())
    export_digest = hashlib.sha256(package.to_bytes()).hexdigest()

    # 5. Cockpit snapshot (views) + optional live server.
    workspace_view = WorkspaceView(
        "PRJ001",
        "Ship offline MVP demo",
        ("a.pm", "a.eng"),
        1,
        1,
        1,
    )
    role_view = RoleView(
        "a.eng",
        "PRJ001",
        "Engineering",
        (TaskSummary("t.1", "Implement demo", "in_progress",
                     "2026-08-31T00:00:00Z", "a.eng"),),
        (MilestoneSummary("m.1", "Demo ready", "2026-08-31T00:00:00Z", False),),
        (ArtifactSummary("docs/report.docx", "document",
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                         128, "0" * 64),),
    )
    cockpit_url = ""
    server = None
    if with_cockpit:
        server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=cockpit_port,
                request_timeout_sec=5,
                state_path=run_dir / "cockpit-state.json",
            ),
            workspace_views=(workspace_view,),
            role_views=(role_view,),
        )
        server.start()
        cockpit_url = server.url

    # 6. Knowledge bundle + persistent store.
    bundle = KnowledgeBaseFacade.aggregate(
        project_id="PRJ001",
        baseline={
            "title": "Ship offline MVP demo",
            "summary": "demo baseline",
            "stages": ["plan", "execute", "review"],
            "work_packages": ["wp.1"],
        },
        merge_records=(),
        risk_reports=(),
        meeting_conclusions=(),
        decision_briefs=(),
        progress_captures=(),
        model_summaries=({"id": "ms.1", "title": "demo model summary"},),
        now=now,
    )
    knowledge_store = KnowledgeStore.create(run_dir / "knowledge.db")
    knowledge_store.save(bundle, now=now)
    knowledge_store.close()

    # 7. Audit stream (push notifications).
    hub = AuditStreamHub()
    pushed: list[AuditEvent] = []
    hub.subscribe("u.auditor", pushed.append)
    for action, result in (
        ("chain.completed", "ok"),
        ("package.exported", "ok"),
        ("knowledge.stored", "ok"),
    ):
        hub.publish(
            AuditEvent.from_audit_record(
                {
                    "ts": now,
                    "actor": "u.pm",
                    "action": action,
                    "result": result,
                    "project_id": "PRJ001",
                    "task_id": "t.1",
                    "tool": "coevo.demo",
                },
                source=AuditEventSource.STATE,
            )
        )

    return DemoResult(
        runtime_dir=run_dir,
        outcome=completed.orch_report.outcome.value,
        package_path=package_path,
        package_wire_sha256=export_digest or wire_sha256,
        knowledge_bundle_id=bundle.bundle_id,
        audit_event_count=hub.event_count,
        cockpit_url=cockpit_url,
        store=store,
        hub=hub,
        cockpit_server=server,
    )
