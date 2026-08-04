from __future__ import annotations

import json
from typing import Any

from src.coevo.app.demo_support import DEMO_PROFILE  # noqa: E402
from src.coevo.identity.models import Actor  # noqa: E402
from src.coevo.identity.service import StaticAuthorizer  # noqa: E402
from src.coevo.talent.models import AvailabilityWindow  # noqa: E402
from src.coevo.talent.recommender import TaskRequirement  # noqa: E402
from src.coevo.task_decomposition.baseline import build_baseline  # noqa: E402

from ._core import ROOT, _require_param
from ..contract import ErrorCode, ServiceError  # noqa: E402


def identity_describe(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """返回角色档案、证书与授权策略（US-0 概览）。"""
    roles = ctx["roles_data"]
    return {
        "project": roles["project"],
        "actors": [
            {
                "actor_id": actor["actor_id"],
                "display_name": actor["display_name"],
                "project_role": actor["project_role"],
                "cert_id": actor["cert_id"],
            }
            for actor in roles["actors"]
        ],
        "grants": {
            actor: sorted(grants) for actor, grants in roles["grants"].items()
        },
        "pki_profile": DEMO_PROFILE,
        "provider": ctx["provider"].name,
    }
def identity_register(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """注册一个身份档案（US-0，经 IdentityService 审计入库）。"""
    actor_id = _require_param(request, "actor_id")
    display_name = _require_param(request, "display_name")
    organization = _require_param(request, "organization")
    role_code = _require_param(request, "role_code")
    cert_id = _require_param(request, "cert_id")
    uid = actor_id.replace(".", "-")
    cert_der = (ROOT / "loop" / "audit-signing-public.cer").read_bytes()
    payload = {
        "organization": {
            "organization_id": f"org-{actor_id}",
            "code": actor_id.upper().replace(".", "-"),
            "name": organization,
        },
        "user": {
            "user_id": uid,
            "organization_id": f"org-{actor_id}",
            "display_name": display_name,
        },
        "client": {
            "client_id": f"cli-{uid}",
            "organization_id": f"org-{actor_id}",
            "assigned_user_id": uid,
            "display_name": f"{display_name} 离线终端",
        },
        "certificate": {
            "certificate_id": cert_id,
            "owner_user_id": uid,
            "bound_client_id": f"cli-{uid}",
            "certificate_der": cert_der,
            "revoked": False,
        },
        "roles": [
            {"project_id": "PRJ001", "user_id": uid, "role_code": role_code}
        ],
    }
    with ctx["store_lock"]:
        try:
            result = ctx["identity_service"].register_identity_bundle(
                Actor("u.auditor"),
                f"req.identity.{actor_id}",
                payload,
            )
        except Exception as exc:
            raise ServiceError(
                ErrorCode.CONFLICT, f"identity registration rejected: {exc}"
            ) from exc
    return {
        "user_id": result.user_id,
        "certificate_id": result.certificate_id,
        "replayed": result.replayed,
    }
def flow_understand(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """解析并映射单位流程（US-1：canonical/tabular/tree 三种 schema）。"""
    raw = _require_param(request, "raw")
    understanding = ctx["flow_service"].understand(raw)
    return {
        "unit_id": understanding.flow.unit_id,
        "version": understanding.flow.version,
        "stages": [stage.stage_id for stage in understanding.flow.stages],
        "mapping": {
            node.node.node_id: node.standard_stage.value
            for node in understanding.mapped.nodes
        },
        "roles": [role.role_id for role in understanding.flow.roles],
    }
def decomposition_propose(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """根据流程理解 + 项目输入生成结构化基线（US-2）。"""
    project_input = _require_param(request, "project_input")
    raw_flow = _require_param(request, "flow")
    understanding = ctx["flow_service"].understand(
        {**raw_flow, "format": "canonical"}
    )
    proposal = ctx["decomp_service"].propose(understanding, project_input)
    baseline = build_baseline(proposal, now=request.ts)
    if request.params.get("store_as_current", True):
        ctx["project_state"]["baseline"] = baseline
    return {
        "project_id": baseline.project_id,
        "version": baseline.version,
        "work_packages": [
            {
                "id": wp.work_package_id,
                "standard_stage": wp.standard_stage,
                "task_count": len(wp.tasks),
            }
            for wp in baseline.work_packages
        ],
        "dependencies": [
            {"predecessor": edge.predecessor_task_id, "successor": edge.successor_task_id}
            for edge in baseline.dependencies
        ],
    }
def talent_recommend(request: Any, ctx: dict[str, Any]) -> dict[str, Any]:
    """按任务要求推荐脱敏人才（US-3）。"""
    requirements = _require_param(request, "requirements")
    parsed_requirements = tuple(
        TaskRequirement(
            task_type=str(item["task_type"]),
            required_skill_tags=tuple(item["required_skill_tags"]),
            required_credentials=tuple(item.get("required_credentials", [])),
            window=AvailabilityWindow(
                item["window"]["start"], item["window"]["end"]
            ),
        )
        for item in requirements
    )
    recs = ctx["recommender"].recommend_for_requirements(
        ctx["pool"], parsed_requirements,
    )
    return {
        "recommendations": [
            {
                "talent_code": rec.talent.talent_code,
                "score": rec.score,
                "rank": rec.rank,
                "alerts": [alert.reason.value for alert in rec.alerts],
            }
            for rec in recs
        ]
    }
