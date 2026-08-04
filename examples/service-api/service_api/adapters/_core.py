from __future__ import annotations

import base64
import dataclasses
import datetime as _dt
import hashlib
import json
import re
import sys
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
SCENARIO = ROOT / "examples" / "tool-dev-project" / "scenario"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples" / "shared"))

from coevo_demo_utils import build_and_verify_package, encrypt_and_verify, write_docx  # noqa: E402
from src.coevo.app.demo_support import (  # noqa: E402
    DEMO_PROFILE,
    DemoFreshnessAuthority,
    DemoSigner,
    ensure_demo_profile,
)
from src.coevo.audit_governance import (  # noqa: E402
    AuditEvent,
    AuditEventSource,
    AuditExportFormat,
    AuditQuery,
    AuditStreamHub,
    SecurityAuditFacade,
)
from src.coevo.cockpit import (  # noqa: E402
    ArtifactSummary,
    CockpitHttpConfig,
    CockpitHttpServer,
    MilestoneSummary,
    RoleView,
    TaskSummary,
    WorkspaceView,
)
from src.coevo.crypto import GmsslPrototypeProvider  # noqa: E402
from src.coevo.decision_brief import (  # noqa: E402
    ApprovedTemplateRegistry,
    BriefType,
    DecisionBriefRepository,
    DecisionBriefService,
    RiskConfirmationRepository,
)
from src.coevo.identity import (  # noqa: E402
    IdentityRepository,
    IdentityService,
    PrivateKeyReference,
    PrivateKeyService,
)
from src.coevo.identity.models import Actor  # noqa: E402
from src.coevo.identity.service import StaticAuthorizer  # noqa: E402
from src.coevo.knowledge_base import (  # noqa: E402
    KnowledgeBaseFacade,
    KnowledgeStore,
    ReviewDecision,
    ReviewDecisionKind,
)
from src.coevo.merge import MergeEngine  # noqa: E402
from src.coevo.merge.receipt import ReceiptSigningAuthority  # noqa: E402
from src.coevo.merge.repository import MergeReceiptRepository  # noqa: E402
from src.coevo.orchestrator import (  # noqa: E402
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
from src.coevo.progress_capture import (  # noqa: E402
    EvidenceInput,
    EvidenceKind,
    EvidenceRef,
    ProgressCaptureService,
)
from src.coevo.protocol import (  # noqa: E402
    PackageImportService,
    ProcessedPackage,
    ProcessedPackageStore,
    ReplayDecision,
    ReplayOutcome,
    build_envelope_template,
    check_replay,
    open_encrypted_package,
    parse_package_bytes,
)
from src.coevo.protocol.sm2_sign import compute_sm3_digest  # noqa: E402
from src.coevo.report import ReportManifest, ReportStatus  # noqa: E402
from src.coevo.risk import merge_and_analyze  # noqa: E402
from src.coevo.supervision import SupervisionCoordinator  # noqa: E402
from src.coevo.talent.models import (  # noqa: E402
    AvailabilityWindow,
    RedactedIdentity,
    SkillTag,
    Talent,
    TalentPool,
)
from src.coevo.talent.recommender import TaskRequirement  # noqa: E402
from src.coevo.talent.service import TalentRecommenderService  # noqa: E402
from src.coevo.task_decomposition.baseline import build_baseline  # noqa: E402
from src.coevo.task_decomposition.service import TaskDecompositionService  # noqa: E402
from src.coevo.task_flow.service import FlowUnderstandingService  # noqa: E402
from src.coevo.workspace.init_service import WorkspaceInitService  # noqa: E402
from src.coevo.workspace.models import WorkspaceEntry, WorkspaceRegistry  # noqa: E402

from ..contract import ErrorCode, ServiceError  # noqa: E402

OWNER_CERT = "CERT-OWNER"
AUDITOR_CERT = "CERT-AUD"
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-]{0,63}$")


class _InMemorySigningStore:
    """演示用签名存储（生产为受保护密钥句柄；仅用于离线示例）。"""

    def use(self, reference, payload):
        return hashlib.sha256(reference.key_id.encode() + bytes(payload)).digest()

    def verify(self, reference, payload, signature, *, parent_pinned_thumbprint):
        return (
            parent_pinned_thumbprint == "PIN-ROOT"
            and signature == self.use(reference, payload)
        )

    def verify_handle(self, reference):
        return None

    def destroy(self, reference):
        return None

    def revoke(self, reference, *, reason):
        return None

    def store(self, certificate_id, payload, *, parent_pinned_thumbprint=None):
        raise AssertionError("not used")
def build_context(runtime_dir: Path) -> dict[str, Any]:
    """装配共享上下文：PKI、授权、领域服务、人才库、编排要素、审计等。"""
    runtime_dir = Path(runtime_dir)
    ensure_demo_profile()
    provider = GmsslPrototypeProvider(ROOT)
    roles_data = json.loads((SCENARIO / "roles.json").read_text(encoding="utf-8"))
    authorizer = StaticAuthorizer(
        {actor: frozenset(grants) for actor, grants in roles_data["grants"].items()}
    )
    pool_data = json.loads((SCENARIO / "talent-pool.json").read_text(encoding="utf-8"))
    talents = tuple(
        Talent(
            talent_code=item["talent_code"],
            skill_tags=tuple(SkillTag(tag) for tag in item["skill_tags"]),
            credentials=tuple(item["credentials"]),
            current_task_count=item["current_task_count"],
            max_parallel_tasks=item["max_parallel_tasks"],
            availability=AvailabilityWindow(
                item["availability"]["start"], item["availability"]["end"]
            ),
            redacted_identity=RedactedIdentity(
                item["redacted_identity"]["pool_code"],
                item["redacted_identity"]["display_hint"],
                item["redacted_identity"]["identity_hash"],
            ),
        )
        for item in pool_data["talents"]
    )
    pool = TalentPool(pool_data["pool_code"], pool_data["schema_version"], talents)
    flow_service = FlowUnderstandingService()
    decomp_service = TaskDecompositionService()
    recommender = TalentRecommenderService()

    registry = AgentRegistry.empty()
    for agent_id, capability in (
        ("agent.task_flow_understanding", AgentCapability.TASK_FLOW_UNDERSTANDING),
        ("agent.task_decomposition", AgentCapability.TASK_DECOMPOSITION),
        ("agent.team_recommendation", AgentCapability.TEAM_RECOMMENDATION),
        ("agent.task_package_build", AgentCapability.TASK_PACKAGE_BUILD),
    ):
        registry = registry.register(
            AgentRegistration(AgentSpec(
                agent_id, capability, capability.value, ("input",), ("output",)
            ))
        )
    executor = RealChainExecutor(flow_service, decomp_service, recommender, pool)

    identity_repo = IdentityRepository.create(
        runtime_dir / "identity.db",
        signer=DemoSigner(),
        freshness=DemoFreshnessAuthority(),
    )
    identity_service = IdentityService(
        identity_repo,
        StaticAuthorizer({"u.auditor": frozenset({"identity:write"})}),
    )

    # 合并/简报/知识所需的生产仓库与模板
    receipt_authority = ReceiptSigningAuthority(
        service=PrivateKeyService(_InMemorySigningStore()),
        reference=PrivateKeyReference(
            key_id="CoevoPrivateKey-" + "a" * 32,
            algorithm_oid="1.2.840.113549.1.1.1",
            key_public_sha256="b" * 64,
            valid_from=_dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc),
            valid_to=_dt.datetime(2027, 1, 1, tzinfo=_dt.timezone.utc),
            bound_certificate_id=OWNER_CERT,
            revoked=False,
            handle_token_hint="a" * 16,
        ),
        signer_certificate_id=OWNER_CERT,
        parent_pinned_thumbprint="PIN-ROOT",
    )
    receipt_repository = MergeReceiptRepository.create(
        runtime_dir / "receipts.sqlite3",
        receipt_authority,
        signer=DemoSigner(),
        freshness=DemoFreshnessAuthority(),
    )
    merge_engine = MergeEngine(
        receipt_repository=receipt_repository,
        receipt_authority=receipt_authority,
    )
    template_ref = "templates/decision-brief.docx"
    template_path = runtime_dir / template_ref
    template_path.parent.mkdir(parents=True, exist_ok=True)
    write_docx(template_path)
    template_registry = ApprovedTemplateRegistry(runtime_dir)
    template_approval = template_registry.approve(
        approval_id="approval.service-api", template_ref=template_ref
    )

    audit_hub = AuditStreamHub()
    context: dict[str, Any] = {
        "runtime_dir": runtime_dir,
        "provider": provider,
        "roles_data": roles_data,
        "authorizer": authorizer,
        "pool": pool,
        "flow_service": flow_service,
        "decomp_service": decomp_service,
        "recommender": recommender,
        "agent_registry": registry,
        "chain_executor": executor,
        "identity_repo": identity_repo,
        "identity_service": identity_service,
        "receipt_repository": receipt_repository,
        "merge_engine": merge_engine,
        "template_registry": template_registry,
        "template_approval": template_approval,
        "template_ref": template_ref,
        "brief_repository": DecisionBriefRepository(),
        "risk_confirmation_repository": RiskConfirmationRepository(receipt_authority),
        "audit_hub": audit_hub,
        "audit_events": [],
        "chain_sessions": {},
        "knowledge_store": KnowledgeStore.create(runtime_dir / "knowledge.db"),
        "store_lock": threading.Lock(),
        "workspace_root": runtime_dir / "workspaces",
        "project_state": {"baseline": None, "risk_report": None, "receipt": None},
        "wps_views": None,
    }
    return context
def close_context(context: dict[str, Any]) -> None:
    """释放上下文中的持久化资源（框架关闭时调用）。"""
    context.get("identity_repo") and context["identity_repo"].close()
    context.get("knowledge_store") and context["knowledge_store"].close()
    for session in context.get("chain_sessions", {}).values():
        store = session.get("store")
        if store is not None:
            store.close()
    receipt_repo = context.get("receipt_repository")
    if receipt_repo is not None:
        receipt_repo.close()
def _param(request: Any, name: str, default: Any = None) -> Any:
    return request.params.get(name, default)
def _require_param(request: Any, name: str) -> Any:
    value = request.params.get(name)
    if value is None or value == "":
        raise ServiceError(ErrorCode.VALIDATION, f"missing required param {name!r}")
    return value
def _require_safe_id(value: Any, name: str) -> str:
    """安全标识校验：字母/数字/下划线/点/连字符（防路径注入）。"""
    if not isinstance(value, str) or not _SAFE_ID_RE.fullmatch(value):
        raise ServiceError(
            ErrorCode.VALIDATION,
            f"{name} must be a safe identifier (alnum/_-.)",
        )
    return value
def _cert_handle(provider: GmsslPrototypeProvider, cert_id: str, role: str) -> Any:
    if role == "sender":
        return provider.sender_handle(DEMO_PROFILE, cert_id)
    return provider.recipient_handle(DEMO_PROFILE, cert_id)
