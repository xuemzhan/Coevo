"""Coevo MVP 端到端演示运行脚本（examples/tool-dev-project）。

场景：跨单位“内部工时统计小工具开发”项目（PRJ001），分为任务/项目实际
负责人、研发工程师、测试工程师、文档工程师、评审专家与系统安全管理员等
角色，使用仓库已实现的 MVP 门面（src/coevo）完整走通：

    US-0  身份与信任（SM2 测试 PKI + 角色授权）
    US-1  两个单位任务流程解析与映射（canonical + tabular 两种输入）
    US-2  结构化任务分解与项目初始基线
    US-3  基于脱敏人才库的团队推荐（含负荷/时间冲突预警）
    US-4  运行中枢固定编排链（任务输入→流程理解→分解→推荐→确认→生成包）
    US-5  多接收人专属加密任务包生成与导出
    US-6  离线任务包导入（隔离区→验签→原子提交→工作区初始化）
    US-7  本地驾驶舱（环回绑定 + 多项目/角色视图）
    US-8  进展采集（证据识别、人工确认；拒绝仅凭文件时间判断）
    US-9  加密成果汇报包生成
    US-10 成果合并（版本审核、三方冲突、主版本更新、签名回执）
    US-11 风险预警（延期识别 + 关联影响 + 会议建议）
    US-12 督办与会议协同（督办事项、会议提案、结论转任务）
    US-13 决策简报（仅使用已确认状态 + WPS 模板请求）
    US-14 成果沉淀（知识包、复盘草稿、审批入库）
    US-15 安全审计（异常包拦截 + 全程留痕 + 摘要链校验）

运行方式（仓库根目录）：
    python examples\\tool-dev-project\\scripts\\run_example.py

产物写入 examples/tool-dev-project/output/run-<时间戳>/，全部离线执行。
任一环节的关键不变量未满足即抛错并以非零退出码结束。
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import html as _html
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
import xml.sax.saxutils as _xml
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXAMPLES_DIR = ROOT / "examples" / "tool-dev-project"
SCENARIO_DIR = EXAMPLES_DIR / "scenario"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
except Exception:  # pragma: no cover - 非控制台环境
    pass

from src.coevo.app.demo_support import (  # noqa: E402
    DEMO_PROFILE,
    DemoFreshnessAuthority,
    DemoSigner,
    ensure_demo_profile,
)
from src.coevo.audit_governance import (  # noqa: E402
    AuditEvent,
    AuditEventResult,
    AuditEventSource,
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
from src.coevo.cockpit.wps import WpsLauncher  # noqa: E402
from src.coevo.crypto import GmsslPrototypeProvider  # noqa: E402
from src.coevo.decision_brief import (  # noqa: E402
    ApprovedTemplateRegistry,
    BriefType,
    DecisionBriefRepository,
    DecisionBriefService,
    RiskConfirmationRepository,
)
from src.coevo.identity import (  # noqa: E402
    ConflictError,
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
    MVP_FIXED_CHAIN,
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    AgentStatus,
    OrchestrationEvent,
    OrchestrationEventKind,
    OrchestrationOutcome,
    Orchestrator,
    RealChainExecutor,
    RealChainStore,
    canonical_digest,
)
from src.coevo.orchestrator._real_chain import (  # noqa: E402
    project_baseline_to_requirements,
)
from src.coevo.progress_capture import (  # noqa: E402
    EvidenceInput,
    EvidenceKind,
    EvidenceRef,
    ProgressCaptureService,
    WorkspaceWatcher,
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
from src.coevo.report import ReportArtifact, ReportManifest, ReportStatus  # noqa: E402
from src.coevo.risk import merge_and_analyze  # noqa: E402
from src.coevo.supervision import SupervisionCoordinator  # noqa: E402
from src.coevo.talent.models import (  # noqa: E402
    AvailabilityWindow,
    RedactedIdentity,
    SkillTag,
    Talent,
    TalentPool,
)
from src.coevo.talent.service import TalentRecommenderService  # noqa: E402
from src.coevo.task_decomposition.baseline import build_baseline  # noqa: E402
from src.coevo.task_decomposition.service import TaskDecompositionService  # noqa: E402
from src.coevo.task_flow.models import Override  # noqa: E402
from src.coevo.task_flow.service import FlowUnderstandingService  # noqa: E402
from src.coevo.workspace.init_service import WorkspaceInitService  # noqa: E402
from src.coevo.workspace.models import WorkspaceEntry, WorkspaceRegistry  # noqa: E402

sys.path.insert(0, str(ROOT / "examples" / "shared"))
from coevo_demo_utils import (  # noqa: E402
    _store_factory,
    build_and_verify_package,
    encrypt_and_verify,
    free_port,
    json_dump,
    jsonable,
    run_chain_guarded,
    sm3_hex,
    ts,
    with_recovery,
    write_docx,
)

PROJECT_ID = "PRJ001"
TASK_ID = "t.1"
BASE_REV = "PRJ001-R0001"
OWNER_CERT = "CERT-OWNER"
AUDITOR_CERT = "CERT-AUD"
MEMBERS = {
    "u.dev": ("CERT-DEV", "研发工程师", "unit_a"),
    "u.qa": ("CERT-QA", "测试工程师", "unit_b"),
    "u.doc": ("CERT-DOC", "文档工程师", "unit_a"),
    "u.review": ("CERT-REV", "评审专家", "unit_b"),
}
SCENARIO_MEMBER_DIR = {
    "u.dev": "dev",
    "u.qa": "qa",
    "u.doc": "doc",
    "u.review": "review",
}


class Tee:
    """同时输出到控制台与 NARRATIVE.md。"""

    def __init__(self, path: Path) -> None:
        self._file = path.open("w", encoding="utf-8")

    def write(self, line: str = "") -> None:
        print(line)
        self._file.write(line + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def step_banner(out: Tee, interactive: bool, num: int, title: str) -> None:
    """打印步骤横幅；交互模式下等待演示者按回车再继续。"""
    out.write("")
    out.write("=" * 78)
    out.write(f"[{num}] {title}")
    out.write("=" * 78)
    if interactive:
        try:
            input("    演示暂停：按回车继续下一步（Ctrl+C 结束演示）…")
        except (EOFError, KeyboardInterrupt):
            raise SystemExit(0)


def write_brief_docx(brief: Any, path: Path) -> None:
    """把已确认的决策简报渲染为无宏 DOCX（WPS 可直接打开的交付物）。"""
    content = brief.current.content
    paragraphs = [
        content.title,
        f"修订版本：{brief.current.revision}（来源回执 {brief.current.source_receipt_id}）",
        "一、总体进展",
        *[f"- {c.text}" for c in content.overall_progress],
        "二、重要变化",
        *[f"- {c.text}" for c in content.important_changes],
        "三、高风险事项",
        *[f"- {c.text}" for c in content.high_risk_items],
        "四、待决策事项",
        *[f"- {c.text}" for c in content.pending_decisions],
    ]
    body = "".join(
        "<w:p><w:r><w:t xml:space=\"preserve\">"
        + _xml.escape(text)
        + "</w:t></w:r></w:p>"
        for text in paragraphs
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{body}</w:body></w:document>",
        )


def _cockpit_api(
    server: Any,
    token: str,
    path: str,
    *,
    post_body: dict[str, Any] | None = None,
) -> tuple[int, str]:
    """调用环回驾驶舱 API 并返回 (HTTP 状态码, 响应文本)。"""
    url = server.url.rstrip("/") + path
    headers = {"X-Cockpit-Token": token}
    data = None
    if post_body is not None:
        data = json.dumps(post_body).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
        headers["Origin"] = server.url.rstrip("/")
        headers["X-Requested-With"] = "coevo-cockpit"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body


def _render_html_report(run_dir: Path, summary: dict[str, Any]) -> Path:
    """把本次演示整理为一份自包含、离线可打开的 HTML 演示报告。"""
    narrative = (run_dir / "NARRATIVE.md").read_text(encoding="utf-8")
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    narrative_lines = narrative.splitlines()
    for index, line in enumerate(narrative_lines):
        if line.startswith("=" * 10):
            # 横幅块为 ==== / [N] 标题 / ====，只有后一行是标题的那条才开新节
            next_is_title = (
                index + 1 < len(narrative_lines)
                and narrative_lines[index + 1].strip().startswith("[")
            )
            if next_is_title:
                if current is not None:
                    sections.append(current)
                current = {"title": "", "lines": []}
            continue
        if current is not None:
            if not current["title"] and line.strip():
                current["title"] = line.strip()
            else:
                current["lines"].append(line)
    if current is not None:
        sections.append(current)

    cards = [
        ("项目", summary.get("project", "-")),
        (
            "项目状态",
            "已结项（验收通过）"
            if summary.get("project_status") == "closed"
            else "进行中",
        ),
        ("流程模型", "unit_a v2 / unit_b v2"),
        ("初始基线", "PRJ001-R0001"),
        ("最终主版本", summary.get("master_revision_final", "-")),
        ("任务包", "4 个角色专属加密包"),
        ("合并回执", str(len(summary.get("merge_receipts", [])))),
        ("风险预警", "deadline_overrun 等 3 项"),
        ("督办事项", str(len(summary.get("supervision_items", [])))),
        ("决策简报", summary.get("decision_brief", "-")),
        ("知识包", summary.get("knowledge_bundle", "-")),
        ("审计事件", str(summary.get("audit_event_count", 0))),
        ("身份注册", "6 项（IdentityService）"),
        ("API 巡检", str(summary.get("cockpit_api_probes", 0)) + " 项"),
        ("WPS 决策", str(summary.get("wps_launch_decisions", 0)) + " 项"),
        ("复用项目", "PRJ002 基线草案"),
    ]
    cards_html = "".join(
        f'<div class="card"><div class="k">{_html.escape(k)}</div>'
        f'<div class="v">{_html.escape(str(v))}</div></div>'
        for k, v in cards
    )

    toc_items = "".join(
        f'<li><a href="#sec-{i}">{_html.escape(section["title"])}</a></li>'
        for i, section in enumerate(sections)
    )
    section_html = ""
    for i, section in enumerate(sections):
        lines = "".join(
            _html.escape(line) + "\n" for line in section["lines"]
        )
        section_html += (
            f'<section id="sec-{i}"><h2>{_html.escape(section["title"])}</h2>'
            f'<pre>{lines}</pre></section>'
        )

    artifact_rows = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in {".db", ".lock", ".p7s", ".marker", ".pyc"}:
            continue
        rel = path.relative_to(run_dir).as_posix()
        if rel.startswith("quarantine/"):
            continue
        artifact_rows.append(
            f"<tr><td>{_html.escape(rel)}</td>"
            f"<td>{path.stat().st_size}</td></tr>"
        )
    artifacts_html = "".join(artifact_rows)

    def chain_html(nodes: list[str]) -> str:
        parts: list[str] = []
        for index, node in enumerate(nodes):
            if index:
                parts.append('<span class="arrow">→</span>')
            parts.append(
                f'<span class="node">{_html.escape(node)}</span>'
            )
        return '<div class="chain">' + "".join(parts) + "</div>"

    chains_html = (
        '<section id="chains"><h2>两条固定编排链（本示例实际执行的业务闭环）</h2>'
        '<p class="chain-label">任务下发链（US-4，含负责人人工确认节点）</p>'
        + chain_html(
            ["任务输入", "流程理解", "任务分解", "人才推荐", "负责人确认", "加密任务包"]
        )
        + '<p class="chain-label">成果回传链（US-10 → US-14）</p>'
        + chain_html(
            ["成果包导入", "版本差异审核", "主版本更新", "风险预警", "决策简报", "知识沉淀"]
        )
        + "</section>"
    )

    timeline_entries = [
        (
            "08-01",
            "任务输入 → 双单位流程理解 → 基线 R0001 → 4 角色专属加密任务包下发",
        ),
        ("08-10", "研发完成汇报合并 → 主版本 R0002"),
        ("08-19", "测试旧基线汇报三方冲突挂起，TASK_CHANGE 变更包下发"),
        (
            "08-21",
            "测试按新基线回传 → R0003；风险预警 → 督办会议 → 决策简报 → 知识包",
        ),
        (
            "08-22",
            "会议结论转整改任务 → R0004；文档/验收全员回传 → R0006；阶段/风险专题/周期三类简报；PRJ002 复用模板跑通下发链",
        ),
    ]
    timeline_html = (
        '<section id="timeline"><h2>演示时间轴</h2><div class="timeline">'
        + "".join(
            '<div class="tl-item"><span class="tl-date">'
            + _html.escape(date)
            + '</span><span class="tl-text">'
            + _html.escape(text)
            + "</span></div>"
            for date, text in timeline_entries
        )
        + "</div></section>"
    )

    def safe_json(rel: str) -> dict[str, Any] | None:
        path = run_dir / rel
        if not path.is_file():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # pragma: no cover - 产物缺失/损坏时跳过该表
            return None
        return value if isinstance(value, dict) else None

    results_sections: list[str] = []
    merge_data = safe_json("merge/merge-records-final.json")
    if merge_data and merge_data.get("merges"):
        merge_rows = "".join(
            "<tr><td>"
            + _html.escape(str(entry.get("reporter", "")))
            + "</td><td>"
            + _html.escape(str(entry.get("task", "")))
            + "</td><td>"
            + ("是" if entry.get("accepted") else "否")
            + "</td><td>"
            + _html.escape(
                str(entry.get("merged_version") or entry.get("reason") or "")
            )
            + "</td></tr>"
            for entry in merge_data["merges"]
        )
        results_sections.append(
            '<section id="results-merges"><h2>合并记录（主版本连续至 '
            + _html.escape(str(summary.get("master_revision_final", "-")))
            + '）</h2><table><thead><tr><th>汇报人</th><th>任务</th><th>合并</th>'
            + f"<th>版本 / 原因</th></tr></thead><tbody>{merge_rows}</tbody></table></section>"
        )
    risk_data = safe_json("risk/risk-report.json")
    if risk_data and risk_data.get("risks"):
        risk_rows = "".join(
            "<tr><td>"
            + _html.escape(str(risk.get("kind", "")))
            + "</td><td>"
            + _html.escape(str(risk.get("severity", "")))
            + "</td><td>"
            + _html.escape(str(risk.get("source", "")))
            + "</td><td>"
            + _html.escape(str(len(risk.get("affected_tasks", []))))
            + "</td></tr>"
            for risk in risk_data["risks"]
        )
        results_sections.append(
            '<section id="results-risks"><h2>风险预警明细</h2>'
            "<table><thead><tr><th>风险类型</th><th>严重度</th><th>来源</th>"
            + f"<th>影响任务数</th></tr></thead><tbody>{risk_rows}</tbody></table></section>"
        )
    brief_ids = [
        ("阶段简报", summary.get("decision_brief", "-")),
        ("风险专题简报", summary.get("risk_topic_brief", "-")),
        ("周期简报", summary.get("periodic_brief", "-")),
    ]
    brief_rows = "".join(
        "<tr><td>"
        + _html.escape(label)
        + "</td><td>"
        + _html.escape(str(brief_id))
        + "</td></tr>"
        for label, brief_id in brief_ids
    )
    results_sections.append(
        '<section id="results-briefs"><h2>决策简报（三种类型）</h2>'
        f"<table><thead><tr><th>类型</th><th>简报 ID</th></tr></thead><tbody>{brief_rows}</tbody></table></section>"
    )

    # 角色行动轨迹（按审计事件聚合）
    actor_names = {
        "u.pm": "任务/项目实际负责人",
        "u.dev": "研发工程师",
        "u.qa": "测试工程师",
        "u.doc": "文档工程师",
        "u.review": "评审专家",
        "u.auditor": "系统安全管理员",
    }
    actor_actions: dict[str, list[str]] = {}
    audit_path = run_dir / "audit" / "audit-events.jsonl"
    if audit_path.is_file():
        for line in audit_path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except Exception:  # pragma: no cover - 容忍单行损坏
                continue
            actor = str(record.get("actor", "?"))
            action = str(record.get("action", "?"))
            actor_actions.setdefault(actor, []).append(action)
    actor_rows = "".join(
        "<tr><td>"
        + _html.escape(actor_names.get(actor, actor))
        + "</td><td>"
        + str(len(actions))
        + "</td><td>"
        + _html.escape("、".join(actions))
        + "</td></tr>"
        for actor, actions in sorted(actor_actions.items())
    )
    results_sections.append(
        '<section id="results-actors"><h2>角色行动轨迹（按审计事件聚合）</h2>'
        "<table><thead><tr><th>角色</th><th>动作数</th><th>动作</th></tr></thead>"
        + f"<tbody>{actor_rows}</tbody></table></section>"
    )

    # 步骤 → MVP 能力对照
    step_map = [
        ("[1]", "US-0 身份与信任：身份注册、防证书复用、授权策略"),
        ("[2]", "US-1 流程理解：双单位流程解析与映射"),
        ("[3]", "US-2 任务分解：基线 R0001"),
        ("[4]", "US-3 团队组建：脱敏人才推荐"),
        ("[5]", "US-4 运行中枢：编排链 + 失败升级"),
        ("[6]", "US-5 任务下发：多接收人专属加密包"),
        ("[7]", "US-6 工作区初始化 + 重放拦截"),
        ("[8]", "US-7 驾驶舱：API/前端/重启/WPS"),
        ("[9]", "US-8 进展采集：watcher 感知 + 人工确认"),
        ("[10]", "US-9 成果回传：加密汇报包"),
        ("[11]", "US-10 状态合并：冲突审核 + 版本更新"),
        ("[12]", "US-11 风险预警"),
        ("[13]", "US-12 督办会议 + 会议决策包"),
        ("[14]", "US-13 阶段决策简报"),
        ("[14b]", "第二轮任务循环（整改任务下发→回传→合并）"),
        ("[14c]", "US-13 风险专题简报"),
        ("[14d]", "全员成果回传与结项 + 周期简报"),
        ("[15]", "US-14 知识沉淀与复用（PRJ002）"),
        ("[16]", "US-15 安全审计与真实拒绝路径"),
        ("[17]", "汇总与演示报告"),
    ]
    step_rows = "".join(
        "<tr><td>"
        + _html.escape(label)
        + "</td><td>"
        + _html.escape(capability)
        + "</td></tr>"
        for label, capability in step_map
    )
    results_sections.append(
        '<section id="results-steps"><h2>步骤 → MVP 能力对照</h2>'
        "<table><thead><tr><th>步骤</th><th>演示能力</th></tr></thead>"
        + f"<tbody>{step_rows}</tbody></table></section>"
    )
    results_html = "".join(results_sections)

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Coevo MVP 端到端演示报告 - {_html.escape(str(summary.get('title', '')))}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; margin: 0; background: #f4f6f9; color: #1f2937; }}
  header {{ background: #0f2a43; color: #fff; padding: 28px 40px; }}
  header h1 {{ margin: 0 0 8px; font-size: 24px; }}
  header p {{ margin: 2px 0; color: #b9c8d8; font-size: 13px; }}
  main {{ max-width: 1080px; margin: 24px auto; padding: 0 24px 48px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 20px 0 28px; }}
  .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; }}
  .card .k {{ font-size: 12px; color: #64748b; }}
  .card .v {{ font-size: 13px; font-weight: 600; margin-top: 4px; word-break: break-all; }}
  .chain-label {{ font-size: 12px; color: #475569; margin: 14px 0 6px; font-weight: 600; }}
  .chain {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 6px; }}
  .chain .node {{ background: #0f2a43; color: #fff; border-radius: 8px; padding: 6px 10px; font-size: 12px; }}
  .chain .arrow {{ color: #64748b; font-weight: 700; }}
  .timeline {{ border-left: 2px solid #0f2a43; margin: 12px 4px 6px 10px; padding-left: 18px; }}
  .tl-item {{ margin-bottom: 10px; font-size: 12.5px; }}
  .tl-date {{ display: inline-block; min-width: 62px; font-weight: 700; color: #0f2a43; }}
  .tl-text {{ color: #334155; }}
  nav.toc {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 20px; margin-bottom: 24px; }}
  nav.toc ul {{ columns: 2; margin: 0; padding-left: 20px; font-size: 13px; }}
  section {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 18px; overflow: hidden; }}
  section h2 {{ margin: 0; padding: 12px 18px; font-size: 15px; background: #eef3f8; border-bottom: 1px solid #e2e8f0; }}
  section pre {{ margin: 0; padding: 14px 18px; font-family: Consolas, "Courier New", monospace; font-size: 12.5px; line-height: 1.55; white-space: pre-wrap; word-break: break-word; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
  th, td {{ border: 1px solid #e2e8f0; padding: 6px 10px; text-align: left; }}
  th {{ background: #eef3f8; }}
  footer {{ text-align: center; color: #94a3b8; font-size: 12px; margin-top: 32px; }}
</style>
</head>
<body>
<header>
  <h1>Coevo MVP 端到端演示报告</h1>
  <p>{_html.escape(str(summary.get('title', '')))}（{_html.escape(str(summary.get('project', '')))}）</p>
  <p>运行目录：{_html.escape(str(run_dir))}</p>
  <p>本报告由示例脚本基于已确认的项目状态生成，全程离线、无外部资源。</p>
</header>
<main>
  <div class="cards">{cards_html}</div>
  {chains_html}
  {timeline_html}
  {results_html}
  <nav class="toc"><ul>{toc_items}</ul></nav>
  {section_html}
  <section>
    <h2>产物清单</h2>
    <table><thead><tr><th>文件（相对运行目录）</th><th>字节</th></tr></thead>
    <tbody>{artifacts_html}</tbody></table>
  </section>
</main>
<footer>生成时间：{_html.escape(_dt.datetime.now().isoformat(timespec="seconds"))} · 演示脚本：examples/tool-dev-project/scripts/run_example.py</footer>
</body>
</html>
"""
    report_path = run_dir / "demo-report.html"
    report_path.write_text(page, encoding="utf-8")
    return report_path


def import_package_committed(
    package: Any,
    wire: bytes,
    *,
    sender_cert: str,
    recipient_cert: str,
    project_id: str,
    sequence_no: int,
    base_revision: str,
    current_revision: str,
    processed_at: str,
) -> Any:
    """重放检测（ACCEPT）→ 原子导入（COMMITTED）。"""
    digest = compute_sm3_digest(wire)
    candidate = ProcessedPackage(
        package_id=package.envelope.package_id,
        package_digest=digest,
        sender_cert_id=sender_cert,
        recipient_cert_id=recipient_cert,
        project_id=project_id,
        sequence_no=sequence_no,
    )
    replay = check_replay(candidate=candidate, registry=())
    if replay.outcome is not ReplayOutcome.ACCEPT:
        raise RuntimeError(f"replay gate rejected package: {replay.outcome.value}")
    imported = PackageImportService().import_package(
        package=package,
        replay_decision=ReplayDecision(replay.outcome, replay.previous_sequence_no, replay.detail),
        store=ProcessedPackageStore.empty(),
        base_revision=base_revision,
        current_revision=current_revision,
        processed_at=processed_at,
    )
    if imported.transaction.step.value != "committed":
        raise RuntimeError(f"import did not commit: {imported.transaction.step.value}")
    return imported


def _signing_authority() -> ReceiptSigningAuthority:
    """合并回执的签名权威（演示用内存签名实现；生产为受保护密钥句柄）。"""

    class InMemorySigningStore:
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

    reference = PrivateKeyReference(
        key_id="CoevoPrivateKey-" + "a" * 32,
        algorithm_oid="1.2.840.113549.1.1.1",
        key_public_sha256="b" * 64,
        valid_from=_dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc),
        valid_to=_dt.datetime(2027, 1, 1, tzinfo=_dt.timezone.utc),
        bound_certificate_id=OWNER_CERT,
        revoked=False,
        handle_token_hint="a" * 16,
    )
    return ReceiptSigningAuthority(
        service=PrivateKeyService(InMemorySigningStore()),
        reference=reference,
        signer_certificate_id=OWNER_CERT,
        parent_pinned_thumbprint="PIN-ROOT",
    )


def _projection_baseline(baseline: Any) -> dict[str, Any]:
    return {
        "project_id": baseline.project_id,
        "version": baseline.version,
        "title": baseline.title,
        "objective": baseline.objective,
        "plan_start": baseline.plan_start,
        "plan_end": baseline.plan_end,
        "responsible_units": list(baseline.responsible_units),
        "work_packages": [
            {
                "id": wp.work_package_id,
                "standard_stage": wp.standard_stage,
                "title": wp.title,
                "tasks": [
                    {
                        "id": task.task_id,
                        "title": task.title,
                        "responsible_role": task.responsible_role,
                        "deliverables": [d.title for d in task.deliverables],
                        "acceptance_criteria": [
                            c
                            for d in task.deliverables
                            for c in d.acceptance_criteria
                        ],
                    }
                    for task in wp.tasks
                ],
            }
            for wp in baseline.work_packages
        ],
        "dependencies": [
            {"predecessor": e.predecessor_task_id, "successor": e.successor_task_id}
            for e in baseline.dependencies
        ],
        "milestones": [
            {"id": m.milestone_id, "title": m.title, "target_date": m.target_date}
            for m in baseline.milestones
        ],
    }


def _audit_record(now: str, actor: str, action: str, result: str, *, task_id: str = TASK_ID) -> dict[str, Any]:
    return {
        "ts": now,
        "actor": actor,
        "action": action,
        "result": result,
        "project_id": PROJECT_ID,
        "task_id": task_id,
        "tool": "coevo.example.tool-dev-project",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo MVP 端到端示例（内部工时统计小工具开发）")
    parser.add_argument(
        "--output-dir",
        default=str(EXAMPLES_DIR / "output"),
        help="运行产物父目录（默认 examples/tool-dev-project/output）",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互演示模式：每个步骤暂停，按回车继续（适合现场讲解）",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="跑完整个演示后保持本地驾驶舱服务运行（Ctrl+C 退出）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=12751,
        help="--serve 模式下驾驶舱监听端口（默认 12751）",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="运行结束后用默认浏览器打开 HTML 演示报告",
    )
    args = parser.parse_args(argv)
    interactive = args.interactive
    output_parent = Path(args.output_dir)
    run_dir = output_parent / f"run-{_dt.datetime.now():%Y%m%d-%H%M%S}-demo"
    run_dir.mkdir(parents=True, exist_ok=True)
    for sub in (
        "identity", "flows", "baseline", "talent", "orchestration", "outbox",
        "quarantine", "workspaces", "cockpit", "reports", "merge", "risk",
        "supervision", "brief", "knowledge", "audit",
    ):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    out = Tee(run_dir / "NARRATIVE.md")
    audit_hub = AuditStreamHub()
    pushed: list[AuditEvent] = []
    audit_hub.subscribe("u.auditor", pushed.append)

    def audit(now: str, actor: str, action: str, result: str = "ok") -> None:
        audit_hub.publish(
            AuditEvent.from_audit_record(
                _audit_record(now, actor, action, result),
                source=AuditEventSource.STATE,
            )
        )

    real_chain_store: RealChainStore | None = None
    receipt_repository: MergeReceiptRepository | None = None
    knowledge_store: KnowledgeStore | None = None
    summary: dict[str, Any] = {"run_dir": str(run_dir)}

    try:
        # ------------------------------------------------------------------
        # [1] US-0 身份与信任
        # ------------------------------------------------------------------
        step_banner(out, interactive, 1, "US-0 身份与信任：角色档案 + SM2 测试 PKI + 授权策略")
        roles_data = json.loads((SCENARIO_DIR / "roles.json").read_text(encoding="utf-8"))
        ensure_demo_profile()
        provider = GmsslPrototypeProvider(ROOT)
        authorizer = StaticAuthorizer(
            {a: frozenset(p) for a, p in roles_data["grants"].items()}
        )
        for actor in roles_data["actors"]:
            out.write(
                f"  - {actor['actor_id']:<10} {actor['display_name']:<8} "
                f"{actor['project_role']:<14} 证书 {actor['cert_id']}（{actor['organization']}）"
            )
        out.write("  - 私钥与口令不落明文：SM2 测试 PKI 由 DPAPI 保护的密钥文件承载，")
        out.write("    加解密只经一次性 GmSSL 助手返回结果（仓库锁定的 GmSSL 3.2.0）。")
        out.write("  - 权限策略（StaticAuthorizer）：u.pm 拥有编排确认/合并/风险/简报/知识库审批权；")
        out.write("    u.auditor 拥有审计读取权与身份注册权。")
        # 通过 IdentityService 实际注册身份档案（组织/用户/终端/证书/项目角色）
        identity_repo = IdentityRepository.create(
            run_dir / "identity" / "identity.db",
            signer=DemoSigner(),
            freshness=DemoFreshnessAuthority(),
        )
        identity_service = IdentityService(
            identity_repo,
            StaticAuthorizer({"u.auditor": frozenset({"identity:write"})}),
        )
        demo_cert = ROOT / "loop" / "runtime" / "sm2-test-pki" / DEMO_PROFILE
        cert_sources = {
            "u.pm": ROOT / "loop" / "audit-signing-public.cer",
            "u.dev": demo_cert / "sender-cert.der",
            "u.qa": demo_cert / "recipient-cert.der",
            "u.doc": demo_cert / "recipient-companion-sign-cert.der",
            "u.review": ROOT / "loop" / "audit-signing-public-F7132638B319851806DD55E826B34BC8952D41B2.cer",
            "u.auditor": demo_cert / "root-ca-cert.der",
        }
        role_code_map = {
            "u.pm": "project_owner",
            "u.dev": "project_member",
            "u.qa": "project_member",
            "u.doc": "project_member",
            "u.review": "project_member",
            "u.auditor": "project_member",
        }
        registrations: list[dict[str, Any]] = []

        def identity_payload_for(actor: dict[str, Any], cert_der: bytes) -> dict[str, Any]:
            uid = actor["actor_id"].replace(".", "-")
            org_id = f"org-{actor['actor_id']}"
            return {
                "organization": {
                    "organization_id": org_id,
                    "code": actor["actor_id"].upper().replace(".", "-"),
                    "name": actor["organization"],
                },
                "user": {
                    "user_id": uid,
                    "organization_id": org_id,
                    "display_name": actor["display_name"],
                },
                "client": {
                    "client_id": f"cli-{uid}",
                    "organization_id": org_id,
                    "assigned_user_id": uid,
                    "display_name": f"{actor['display_name']} 离线终端",
                },
                "certificate": {
                    "certificate_id": actor["cert_id"],
                    "owner_user_id": uid,
                    "bound_client_id": f"cli-{uid}",
                    "certificate_der": cert_der,
                    "revoked": False,
                },
                "roles": [
                    {
                        "project_id": PROJECT_ID,
                        "user_id": uid,
                        "role_code": role_code_map[actor["actor_id"]],
                    }
                ],
            }

        try:
            for actor in roles_data["actors"]:
                payload = identity_payload_for(
                    actor, cert_sources[actor["actor_id"]].read_bytes()
                )
                result = identity_service.register_identity_bundle(
                    Actor("u.auditor"),
                    f"req.identity.{actor['actor_id']}",
                    payload,
                )
                registrations.append(
                    {
                        "actor": actor["actor_id"],
                        "cert_id": actor["cert_id"],
                        "request_id": result.request_id,
                        "user_id": result.user_id,
                        "certificate_id": result.certificate_id,
                        "replayed": result.replayed,
                    }
                )
                out.write(
                    f"  - 身份注册：{actor['actor_id']}（{actor['display_name']}）→ "
                    f"{result.user_id} / {result.certificate_id}（角色 {role_code_map[actor['actor_id']]}）"
                )
            # 防证书复用：同一证书指纹不得注册第二个身份
            dev_actor = next(a for a in roles_data["actors"] if a["actor_id"] == "u.dev")
            try:
                identity_service.register_identity_bundle(
                    Actor("u.auditor"),
                    "req.identity.cert-reuse",
                    identity_payload_for(dev_actor, cert_sources["u.dev"].read_bytes()),
                )
            except ConflictError:
                out.write(
                    "  - 安全演示：同一证书指纹被第二个身份复用时注册被拒绝"
                    "（trusted_certificates.fingerprint_sha256 UNIQUE，防证书复用）"
                )
            else:
                raise RuntimeError("证书指纹复用未被拦截")
            # 重放幂等：同一请求号再次提交不重复入库
            pm_actor = next(a for a in roles_data["actors"] if a["actor_id"] == "u.pm")
            replay_result = identity_service.register_identity_bundle(
                Actor("u.auditor"),
                "req.identity.u.pm",
                identity_payload_for(pm_actor, cert_sources["u.pm"].read_bytes()),
            )
            out.write(
                f"  - 重放幂等演示：同一请求号再次提交 → replayed={replay_result.replayed}（不重复入库）"
            )
        finally:
            identity_repo.close()
        json_dump(registrations, run_dir / "identity" / "registrations.json")
        json_dump(roles_data, run_dir / "identity" / "roles.json")
        json_dump(
            {"profile": DEMO_PROFILE, "provider": provider.name, "scope": provider.scope.value},
            run_dir / "identity" / "pki-profile.json",
        )
        audit(ts(1, 1), "u.auditor", "identity.init")
        audit(ts(1, 1), "u.auditor", "identity.registered")

        # ------------------------------------------------------------------
        # [2] US-1 任务流程理解：两个单位流程解析与映射
        # ------------------------------------------------------------------
        step_banner(out, interactive, 2, "US-1 任务流程理解：unit_a（canonical）+ unit_b（tabular）")
        flow_service = FlowUnderstandingService()
        unit_a_raw = json.loads((SCENARIO_DIR / "flows" / "unit-a-flow.json").read_text(encoding="utf-8"))
        unit_b_raw = json.loads((SCENARIO_DIR / "flows" / "unit-b-flow.json").read_text(encoding="utf-8"))

        understanding_a = flow_service.understand(unit_a_raw)
        understanding_b = flow_service.understand(unit_b_raw)
        confirmed_a = flow_service.confirm(
            understanding_a.flow,
            (Override(
                target_path="stages[0].nodes[0].stage_hint",
                original_value="方案策划",
                edited_value="方案策划",
                reason="负责人确认：需求澄清属于方案策划阶段",
            ),),
            ts(2, 10),
        )
        confirmed_b = flow_service.confirm(
            understanding_b.flow,
            (Override(
                target_path="roles[1].responsibility",
                original_value="验收评审与交付确认",
                edited_value="验收评审与交付确认（双人复核）",
                reason="负责人确认：验收结论需要双人复核",
            ),),
            ts(2, 20),
        )
        for label, understanding, confirmed in (
            ("unit_a（研发流程）", understanding_a, confirmed_a),
            ("unit_b（测试交付流程）", understanding_b, confirmed_b),
        ):
            mapped = {
                node.node.node_id: node.standard_stage.value
                for node in understanding.mapped.nodes
            }
            out.write(f"  - {label}：unit={understanding.flow.unit_id} "
                      f"version {understanding.flow.version} → 确认后 version {confirmed.version}")
            out.write(f"    阶段={[s.stage_id for s in understanding.flow.stages]} "
                      f"节点映射={json.dumps(mapped, ensure_ascii=False)}")
            reviewer = understanding.reviewer_view
            out.write(
                f"    溯源示例：flow.title ← {reviewer.source_mapping_lookup('flow.title')}；"
                f"stages[0].nodes[0].title 置信度 "
                f"{reviewer.confidence_for('stages[0].nodes[0].title')}"
            )
        json_dump(
            {
                "unit_a": {
                    "version": confirmed_a.version,
                    "stages": [s.stage_id for s in confirmed_a.stages],
                    "roles": [r.role_id for r in confirmed_a.roles],
                    "overrides": [
                        {"target_path": o.target_path, "edited_value": o.edited_value, "reason": o.reason}
                        for o in confirmed_a.overrides
                    ],
                },
                "unit_b": {
                    "version": confirmed_b.version,
                    "stages": [s.stage_id for s in confirmed_b.stages],
                    "roles": [r.role_id for r in confirmed_b.roles],
                    "overrides": [
                        {"target_path": o.target_path, "edited_value": o.edited_value, "reason": o.reason}
                        for o in confirmed_b.overrides
                    ],
                },
            },
            run_dir / "flows" / "confirmed-models.json",
        )
        audit(ts(2, 30), "u.pm", "task_flow.understanding.confirmed")

        # 两单位流程合并为跨单位任务流程（供 US-2/US-4 使用）
        def _unit_b_canonical_nodes() -> list[dict[str, Any]]:
            return [
                {
                    "node_id": row["node_id"],
                    "title": row["title"],
                    "stage_hint": row["stage_hint"],
                    "inputs": row["inputs"],
                    "outputs": row["outputs"],
                    "review_criteria": row["review_criteria"],
                    "responsible_roles": row["responsible_roles"],
                }
                for row in unit_b_raw["rows"]
            ]

        merged_flow = {
            "format": "canonical",
            "flow": {
                "unit_id": "prj001_combined",
                "title": "PRJ001 跨单位任务流程（unit_a 研发 + unit_b 测试交付）",
                "stages": [
                    {
                        "stage_id": "planning_stage",
                        "name": "需求与方案",
                        "nodes": [unit_a_raw["flow"]["stages"][0]["nodes"][0]],
                    },
                    {
                        "stage_id": "design_review_stage",
                        "name": "测试设计与评审",
                        "nodes": [_unit_b_canonical_nodes()[0]],
                    },
                    {
                        "stage_id": "execution_stage",
                        "name": "开发与测试执行",
                        "nodes": [
                            unit_a_raw["flow"]["stages"][1]["nodes"][0],
                            unit_a_raw["flow"]["stages"][1]["nodes"][1],
                            _unit_b_canonical_nodes()[1],
                        ],
                    },
                    {
                        "stage_id": "closure_stage",
                        "name": "文档收尾",
                        "nodes": [unit_a_raw["flow"]["stages"][2]["nodes"][0]],
                    },
                    {
                        "stage_id": "delivery_stage",
                        "name": "验收交付",
                        "nodes": [_unit_b_canonical_nodes()[2]],
                    },
                ],
                "roles": list(unit_a_raw["flow"]["roles"]) + list(unit_b_raw["roles"]),
            },
        }
        understanding_merged = flow_service.understand(merged_flow)
        out.write(
            f"  - 两单位流程合并为跨单位流程（{understanding_merged.flow.unit_id} v"
            f"{understanding_merged.flow.version}，{len(understanding_merged.flow.stages)} 个阶段，"
            f"{sum(len(s.nodes) for s in understanding_merged.flow.stages)} 个节点）"
        )
        json_dump(
            {
                "unit_id": understanding_merged.flow.unit_id,
                "version": understanding_merged.flow.version,
                "mapping": {
                    node.node.node_id: node.standard_stage.value
                    for node in understanding_merged.mapped.nodes
                },
            },
            run_dir / "flows" / "merged-flow.json",
        )

        # ------------------------------------------------------------------
        # [3] US-2 任务分解：结构化任务与项目初始基线
        # ------------------------------------------------------------------
        step_banner(out, interactive, 3, "US-2 任务分解：结构化任务、工作包、里程碑与依赖")
        project_input = json.loads((SCENARIO_DIR / "project-input.json").read_text(encoding="utf-8"))
        project_input["flow"] = merged_flow["flow"]  # 编排链使用跨单位合并流程
        decomp_service = TaskDecompositionService()
        proposal = decomp_service.propose(understanding_merged, project_input)
        baseline_v1 = build_baseline(proposal, now=ts(2, 40))
        out.write(f"  - 项目基线 v{baseline_v1.version}：{baseline_v1.title}")
        for wp in baseline_v1.work_packages:
            out.write(f"    · 工作包 {wp.work_package_id}（{wp.standard_stage}）：")
            for task in wp.tasks:
                out.write(
                    f"      - {task.task_id} {task.title}（角色 {task.responsible_role}，"
                    f"交付物 {[d.title for d in task.deliverables]}）"
                )
        out.write(f"  - 依赖（阶段顺序种子）：{[(e.predecessor_task_id, e.successor_task_id) for e in baseline_v1.dependencies]}")
        out.write(f"  - 里程碑：{[(m.milestone_id, m.title) for m in baseline_v1.milestones]}")
        json_dump(_projection_baseline(baseline_v1), run_dir / "baseline" / "PRJ001-R0001.json")
        audit(ts(2, 50), "u.pm", "task_decomposition.baseline.confirmed")

        # ------------------------------------------------------------------
        # [4] US-3 团队组建：脱敏人才库推荐
        # ------------------------------------------------------------------
        step_banner(out, interactive, 4, "US-3 团队组建：脱敏人才库推荐（含负荷/时间冲突预警）")
        pool_data = json.loads((SCENARIO_DIR / "talent-pool.json").read_text(encoding="utf-8"))
        talents = tuple(
            Talent(
                talent_code=t["talent_code"],
                skill_tags=tuple(SkillTag(v) for v in t["skill_tags"]),
                credentials=tuple(t["credentials"]),
                current_task_count=t["current_task_count"],
                max_parallel_tasks=t["max_parallel_tasks"],
                availability=AvailabilityWindow(
                    t["availability"]["start"], t["availability"]["end"]
                ),
                redacted_identity=RedactedIdentity(
                    t["redacted_identity"]["pool_code"],
                    t["redacted_identity"]["display_hint"],
                    t["redacted_identity"]["identity_hash"],
                ),
            )
            for t in pool_data["talents"]
        )
        pool = TalentPool(pool_data["pool_code"], pool_data["schema_version"], talents)
        requirements = project_baseline_to_requirements(baseline_v1)
        recommender = TalentRecommenderService()
        recommendations = recommender.recommend_for_requirements(pool, requirements)
        requirement_list = list(requirements)
        chunk = len(pool.talents)
        per_requirement = [
            recommendations[i * chunk:(i + 1) * chunk]
            for i in range(len(requirement_list))
        ]
        for requirement, recs in zip(requirement_list, per_requirement):
            top = recs[0]
            alerts = [f"{a.reason.value}:{a.detail}" for a in top.alerts]
            out.write(
                f"  - 任务类型 {requirement.task_type}（需 {requirement.required_skill_tags}）→ "
                f"推荐 {top.talent.talent_code}（{top.talent.redacted_identity.display_hint}）"
                f" 得分 {top.score} 排名 {top.rank}"
            )
            for alert in alerts:
                out.write(f"    预警：{alert}")
        json_dump(
            [
                {
                    "task_type": requirement.task_type,
                    "top": {
                        "talent_code": recs[0].talent.talent_code,
                        "score": recs[0].score,
                        "alerts": [a.reason.value for a in recs[0].alerts],
                    },
                }
                for requirement, recs in zip(requirement_list, per_requirement)
            ],
            run_dir / "talent" / "recommendations.json",
        )
        # US-3 AC-6/AC-8：负责人人工替换推荐并记录操作（含时间冲突预警）
        override_record = {
            "task_type": "task.n.impl_core",
            "original_talent": "t.dev1",
            "replaced_by": "t.dev2",
            "reason": "负责人评估 t.dev1 当期负载后临时改派",
            "alert": (
                "t.dev2 可用窗口 2026-08-21..2026-08-31 与任务窗口 "
                "2026-08-01..2026-08-20 不重叠（WINDOW_CONFLICT），需错峰安排"
            ),
            "decided_by": "u.pm",
            "decided_at": ts(3, 1),
        }
        json_dump(override_record, run_dir / "talent" / "assignment-override.json")
        out.write(
            "  - 人工替换记录（US-3 AC-6/AC-8）：task.n.impl_core 由 t.dev1 改派 "
            "t.dev2，命中时间冲突预警，需错峰安排；责任人 u.pm 已留痕"
        )
        audit(ts(3, 0), "u.pm", "talent.recommendation")

        # ------------------------------------------------------------------
        # [5] US-4 运行中枢：固定编排链（任务下发链）
        # ------------------------------------------------------------------
        step_banner(out, interactive, 5, "US-4 运行中枢：任务下发链（流程理解→分解→推荐→人工确认→生成包）")
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
        executor = RealChainExecutor(
            flow_service,
            decomp_service,
            recommender,
            pool,
        )
        event = OrchestrationEvent(
            "ev.tool.001",
            OrchestrationEventKind.DISPATCH,
            PROJECT_ID,
            TASK_ID,
            {
                "schema_version": project_input["schema_version"],
                "base_revision": project_input["base_revision"],
                "project_input_digest": canonical_digest(project_input),
            },
            ts(1, 2),
        )
        workspace = WorkspaceEntry(PROJECT_ID, "u.pm", "pkg.input", BASE_REV)
        def main_chain_run(store: RealChainStore) -> Any:
            held = with_recovery(
                store,
                lambda: Orchestrator.dispatch_event_with_real_facades(
                    registry,
                    MVP_FIXED_CHAIN,
                    event,
                    workspace=workspace,
                    executor=executor,
                    project_input=project_input,
                    store=store,
                    now=ts(1, 2),
                ),
            )
            out.write(f"  - 前 3 步结束：outcome={held.orch_report.outcome.value}")
            for line in held.flow_understanding_summary:
                out.write(f"    · {line}")
            for line in held.baseline_summary:
                out.write(f"    · {line}")
            for line in held.recommendation_summary:
                out.write(f"    · {line}")
            out.write("  - 第 4 步为人工确认节点（高影响操作），等待负责人授权…")
            confirmed = with_recovery(
                store,
                lambda: Orchestrator.confirm_real_chain(
                    held,
                    preview=held.package_preview,
                    actor=Actor("u.pm"),
                    authorizer=authorizer,
                    store=store,
                    now=ts(1, 3),
                ),
            )
            out.write("  - u.pm 授权确认通过（orchestrator:confirm-package:PRJ001）")
            completed = with_recovery(
                store,
                lambda: Orchestrator.resume_real_chain(
                    confirmed,
                    registry=registry,
                    chain=MVP_FIXED_CHAIN,
                    event=event,
                    workspace=workspace,
                    executor=executor,
                    store=store,
                    now=ts(1, 4),
                    crypto_provider=provider,
                    sender_handle=provider.sender_handle(DEMO_PROFILE, OWNER_CERT),
                    recipient_handle=provider.recipient_handle(DEMO_PROFILE, MEMBERS["u.dev"][0]),
                ),
            )
            if completed.orch_report.outcome is not OrchestrationOutcome.COMPLETED:
                raise RuntimeError(
                    f"chain did not complete: {completed.orch_report.outcome.value}"
                )
            out.write("  - 编排链完成：")
            for line in completed.package_summary:
                out.write(f"    · {line}")
            json_dump(
                {
                    "chain_id": completed.chain_id,
                    "event_id": completed.event_id,
                    "outcome": completed.orch_report.outcome.value,
                    "traces": [
                        {
                            "step": t.step_index,
                            "agent": t.agent_id,
                            "result": t.result.value if hasattr(t.result, "value") else str(t.result),
                            "detail": t.detail,
                            "confirmed_by": t.confirmed_by,
                        }
                        for t in completed.orch_report.trace
                    ],
                    "package_summary": list(completed.package_summary),
                },
                run_dir / "orchestration" / "chain-report.json",
            )
            return completed

        real_chain_store, completed = run_chain_guarded(
            _store_factory(run_dir / "orchestration" / "real-chain.db"),
            main_chain_run,
        )
        audit(ts(1, 5), "u.pm", "orchestrator.chain.completed")

        # US-4 AC-6 失败处理：智能体不可用时编排不自动执行，直接升级人工
        registry_busy = registry.set_status(
            "agent.task_flow_understanding", AgentStatus.BUSY
        )
        event_fail = OrchestrationEvent(
            "ev.tool.fail.001",
            OrchestrationEventKind.DISPATCH,
            PROJECT_ID,
            TASK_ID,
            event.payload,
            ts(1, 5),
        )

        def fail_chain_run(store: RealChainStore) -> Any:
            held_fail = with_recovery(
                store,
                lambda: Orchestrator.dispatch_event_with_real_facades(
                    registry_busy,
                    MVP_FIXED_CHAIN,
                    event_fail,
                    workspace=workspace,
                    executor=executor,
                    project_input=project_input,
                    store=store,
                    now=ts(1, 5),
                ),
            )
            if held_fail.orch_report.outcome.value != "escalated":
                raise RuntimeError("agent-busy escalation did not trigger")
            out.write(
                "  - 失败升级演示（US-4 AC-6）：agent.task_flow_understanding 为 BUSY 时，"
                "编排不自动执行，直接升级人工"
            )
            for trace in held_fail.orch_report.trace:
                out.write(
                    f"    · step{trace.step_index} {trace.agent_id}: "
                    f"{trace.result.value}（{trace.detail}）"
                )
            return held_fail

        fail_store, _ = run_chain_guarded(
            _store_factory(run_dir / "orchestration" / "fail-chain.db"),
            fail_chain_run,
        )
        fail_store.close()
        audit(ts(1, 5), "u.auditor", "orchestrator.escalated", result="blocked")

        # ------------------------------------------------------------------
        # [6] US-5 任务下发：多接收人专属加密任务包
        # ------------------------------------------------------------------
        step_banner(out, interactive, 6, "US-5 任务下发：为 4 个角色生成接收人专属加密 .agent 任务包")
        task_packages: dict[str, tuple[Any, bytes]] = {}
        for member_id, (cert_id, role_name, _org) in MEMBERS.items():
            content = json.dumps(
                {
                    "title": project_input["title"],
                    "objective": project_input["objective"],
                    "base_revision": BASE_REV,
                    "role": role_name,
                    "flow_summary": list(completed.flow_understanding_summary),
                    "baseline_summary": list(completed.baseline_summary),
                    "recommendation_summary": list(completed.recommendation_summary),
                    "deliverable_requirements": {
                        "u.dev": "交付可运行工具代码、报表模块与自测记录",
                        "u.qa": "交付测试用例与测试报告",
                        "u.doc": "交付用户手册与交付说明",
                        "u.review": "交付验收评审意见与验收结论",
                    }[member_id],
                    "template_ref": "templates/工作包模板.docx",
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            package, wire = build_and_verify_package(
                provider=provider,
                sender_cert=OWNER_CERT,
                recipient_cert=cert_id,
                package_type="TASK_ASSIGNMENT",
                project_id=PROJECT_ID,
                task_id=TASK_ID,
                base_revision=BASE_REV,
                sequence_no=1,
                manifest={
                    "event_id": event.event_id,
                    "project_id": PROJECT_ID,
                    "task_id": TASK_ID,
                    "base_revision": BASE_REV,
                    "payload_digest": project_input["payload_digest"],
                },
                content=content,
                signed_at=ts(1, 6),
                expires_at="2027-08-01T00:00:00Z",
            )
            task_packages[member_id] = (package, wire)
            filename = (
                f"TASK_ASSIGNMENT_{PROJECT_ID}_{package.envelope.package_id}.agent"
            )
            (run_dir / "outbox" / filename).write_bytes(wire)
            out.write(
                f"  - {member_id}（{role_name}，{cert_id}）：{filename} "
                f"（sha256={hashlib.sha256(wire).hexdigest()[:16]}…，"
                f"{len(wire)} 字节，已解密回读校验）"
            )
        json_dump(
            {
                member: {
                    "package_id": pkg.envelope.package_id,
                    "sha256": hashlib.sha256(wire).hexdigest(),
                }
                for member, (pkg, wire) in task_packages.items()
            },
            run_dir / "outbox" / "manifest.json",
        )
        audit(ts(1, 7), "u.pm", "package.exported")

        # ------------------------------------------------------------------
        # [7] US-6 工作区初始化：隔离区→验签→原子导入→工作区释放
        # ------------------------------------------------------------------
        step_banner(out, interactive, 7, "US-6 工作区初始化：离线导入与项目/角色工作区创建")
        workspace_entries: dict[str, WorkspaceEntry] = {}
        member_registries: dict[str, WorkspaceRegistry] = {}
        init_service = WorkspaceInitService(
            quarantine_root=str(run_dir / "quarantine"),
            workspace_root=str(run_dir / "workspaces"),
        )
        for member_id, (cert_id, role_name, _org) in MEMBERS.items():
            package, wire = task_packages[member_id]
            quarantine_file = (
                run_dir / "quarantine" / f"{package.envelope.package_id}.agent"
            )
            quarantine_file.write_bytes(wire)
            imported = import_package_committed(
                package,
                wire,
                sender_cert=OWNER_CERT,
                recipient_cert=cert_id,
                project_id=PROJECT_ID,
                sequence_no=1,
                base_revision=BASE_REV,
                current_revision=BASE_REV,
                processed_at=ts(1, 8),
            )
            init = init_service.init_from_import(
                imported,
                WorkspaceRegistry.empty(),
                role_id=member_id,
                revision=imported.record.revision,
            )
            if not init.created or init.entry is None:
                raise RuntimeError(f"workspace init failed for {member_id}: {init.failure_reason}")
            workspace_entries[member_id] = init.entry
            member_registries[member_id] = init.registry
            ws_root = Path(init.paths.workspace.as_posix())
            ws_root.mkdir(parents=True, exist_ok=True)
            (ws_root / "任务说明.md").write_text(
                f"# 任务说明\n\n项目：{project_input['title']}\n角色：{role_name}\n"
                f"基线：{BASE_REV}\n目标：{project_input['objective']}\n",
                encoding="utf-8",
            )
            (ws_root / "流程要求.md").write_text(
                "流程要求：按已确认的单位流程模型执行（unit_a v2 / unit_b v2），"
                "阶段映射见 confirmed-models.json。\n",
                encoding="utf-8",
            )
            (ws_root / "交付物要求.md").write_text(
                "交付物要求：任务包中声明的角色交付物 + 验收标准；"
                "成果需关联证据并经负责人确认后回传。\n",
                encoding="utf-8",
            )
            template_dir = ws_root / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            write_docx(template_dir / "工作包模板.docx")
            evidence_dir = ws_root / "evidence"
            evidence_dir.mkdir(parents=True, exist_ok=True)
            evidence_src = (
                SCENARIO_DIR / "members" / SCENARIO_MEMBER_DIR[member_id] / "evidence"
            )
            for evidence in evidence_src.glob("*.md"):
                (evidence_dir / evidence.name).write_bytes(evidence.read_bytes())
            out.write(
                f"  - {member_id}（{role_name}）：包 {init.entry.package_id[:12]}… "
                f"提交成功，工作区 {init.paths.workspace.as_posix()} 已释放"
            )
            out.write(
                "    释放内容：任务说明、流程要求、交付物要求、工作包模板、证据目录"
            )
        # 重放拒绝演示：同一任务包再次导入必须被拦截（协议 §17 / US-15 AC-1）
        replay_candidate = ProcessedPackage(
            package_id=task_packages["u.dev"][0].envelope.package_id,
            package_digest=compute_sm3_digest(task_packages["u.dev"][1]),
            sender_cert_id=OWNER_CERT,
            recipient_cert_id=MEMBERS["u.dev"][0],
            project_id=PROJECT_ID,
            sequence_no=1,
        )
        replay_again = check_replay(
            candidate=replay_candidate,
            registry=(replay_candidate,),
        )
        replay_intercept = SecurityAuditFacade.evaluate_interception(
            package_id=replay_candidate.package_id,
            envelope_status="ok",
            signature_status="valid",
            expiration_ts="2027-08-01T00:00:00Z",
            now=ts(1, 9),
            replay_status="duplicate",
            envelope_recipient_cert_id=MEMBERS["u.dev"][0],
            expected_recipient_cert_id=MEMBERS["u.dev"][0],
        )
        out.write(
            f"  - 重放拦截演示：u.dev 同一任务包再次导入 → {replay_again.outcome.value}"
            f"（{replay_again.detail}）；审计判定 intercepted="
            f"{replay_intercept.intercepted}，reasons="
            f"{[r.value for r in replay_intercept.reasons]}"
        )
        audit(ts(1, 9), "u.dev", "workspace.init")
        audit(ts(1, 9), "u.auditor", "package.replay.rejected", result="rejected")

        # ------------------------------------------------------------------
        # [8] US-7 本地驾驶舱：环回绑定 + 多项目/角色视图
        # ------------------------------------------------------------------
        step_banner(out, interactive, 8, "US-7 本地驾驶舱：环回服务、API 巡检与项目/角色工作视图")
        ws_view = WorkspaceView(
            PROJECT_ID,
            project_input["title"],
            tuple(MEMBERS.keys()),
            7,
            5,
            4,
        )
        role_views = []
        for member_id, (cert_id, role_name, _org) in MEMBERS.items():
            evidence_dir = (
                run_dir / "workspaces" / PROJECT_ID / member_id / "evidence"
            )
            artifacts = []
            for evidence in sorted(evidence_dir.glob("*.md")):
                artifacts.append(ArtifactSummary(
                    f"evidence/{evidence.name}",
                    "document",
                    "text/markdown",
                    evidence.stat().st_size,
                    "0" * 64,
                ))
            role_views.append(RoleView(
                member_id,
                PROJECT_ID,
                role_name,
                (TaskSummary("t.1", project_input["title"], "in_progress",
                             project_input["plan_end"], member_id),),
                (MilestoneSummary("m.1", "工具可用版本", project_input["plan_end"], False),),
                tuple(artifacts),
            ))
        port = free_port()
        cockpit_server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=port,
                request_timeout_sec=5,
                state_path=run_dir / "cockpit" / "cockpit-state.json",
                lock_path=run_dir / "cockpit" / "cockpit.lock",
            ),
            workspace_views=(ws_view,),
            role_views=tuple(role_views),
        )
        cockpit_api_results: dict[str, Any] = {}
        try:
            cockpit_server.start()
            token = cockpit_server.session_manager.create()
            page_url = cockpit_server.url + "?token=" + token
            with urllib.request.urlopen(page_url, timeout=20) as resp:
                page_status = resp.status
                page_html = resp.read().decode("utf-8", errors="replace")
            if page_status >= 400:
                raise RuntimeError(f"cockpit page returned {page_status}")
            # US-7 AC-3/AC-4：前端页面必须本地化、不得引用任何外部资源
            external_refs = sorted(
                {m.group(0) for m in re.finditer(r"https?://", page_html)}
            )
            if external_refs:
                raise RuntimeError(f"cockpit page references external resources: {external_refs}")
            frontend_dir = run_dir / "cockpit" / "frontend"
            frontend_dir.mkdir(parents=True, exist_ok=True)
            (frontend_dir / "index.html").write_text(page_html, encoding="utf-8")
            for asset in ("style.css", "app.js"):
                asset_status, asset_body = _cockpit_api(
                    cockpit_server, token, f"/static/{asset}"
                )
                if asset_status != 200:
                    raise RuntimeError(f"cockpit static asset {asset} returned {asset_status}")
                (frontend_dir / asset).write_text(asset_body, encoding="utf-8")
                out.write(f"    · 前端资源 /static/{asset}: HTTP {asset_status}（已保存）")
            probes = [
                ("health", "/api/health", None),
                ("list_projects", f"/api/list_projects?project_id={PROJECT_ID}", None),
                ("list_roles", f"/api/list_roles?project_id={PROJECT_ID}", None),
                ("project_view", f"/api/project_view?project_id={PROJECT_ID}", None),
                (
                    "role_view",
                    f"/api/role_view?role_id=u.dev&project_id={PROJECT_ID}",
                    None,
                ),
                (
                    "task_view",
                    f"/api/task_view?task_id=t.1&role_id=u.dev&project_id={PROJECT_ID}",
                    None,
                ),
                (
                    "milestone_view",
                    f"/api/milestone_view?task_id=m.1&project_id={PROJECT_ID}",
                    None,
                ),
                (
                    "wps_open_allowed",
                    "/api/wps_open",
                    {
                        "artifact_path": "templates/工作包模板.docx",
                        "project_id": PROJECT_ID,
                        "confirm": True,
                    },
                ),
                (
                    "wps_open_denied",
                    "/api/wps_open",
                    {
                        "artifact_path": "evidence/开发进展说明.md",
                        "project_id": PROJECT_ID,
                        "confirm": True,
                    },
                ),
            ]
            for label, api_path, body in probes:
                api_status, api_body = _cockpit_api(
                    cockpit_server, token, api_path, post_body=body
                )
                cockpit_api_results[label] = {"status": api_status, "body": api_body}
                out.write(f"    · {label}: HTTP {api_status}")
            if cockpit_api_results["wps_open_allowed"]["status"] != 200:
                raise RuntimeError("WPS 允许列表放行探测未返回 200")
            if cockpit_api_results["wps_open_denied"]["status"] != 403:
                raise RuntimeError("WPS 允许列表拒绝探测未返回 403")
            # API 响应内容校验：负载字段与预期一致（前端渲染依赖这些字段）
            list_body = json.loads(cockpit_api_results["list_projects"]["body"])
            if PROJECT_ID not in list_body.get("payload", {}).get("projects", []):
                raise RuntimeError("list_projects 响应缺少 PRJ001")
            role_body = json.loads(cockpit_api_results["role_view"]["body"])
            if role_body.get("payload", {}).get("role_id") != "u.dev":
                raise RuntimeError("role_view 响应缺少 u.dev")
            task_body = json.loads(cockpit_api_results["task_view"]["body"])
            if task_body.get("payload", {}).get("task_id") != "t.1":
                raise RuntimeError("task_view 响应缺少 t.1")
            milestone_body = json.loads(cockpit_api_results["milestone_view"]["body"])
            if milestone_body.get("payload", {}).get("milestone_id") != "m.1":
                raise RuntimeError("milestone_view 响应缺少 m.1")
            out.write(
                "    · API 响应内容校验：项目/角色/任务/里程碑负载字段与预期一致"
            )
            failed = [
                label
                for label, result in cockpit_api_results.items()
                if label != "wps_open_denied" and result["status"] >= 400
            ]
            if failed:
                raise RuntimeError(f"cockpit api probe failed: {failed}")
            out.write(
                f"  - 驾驶舱仅绑定环回地址：{cockpit_server.url}，页面 HTTP {page_status}；"
                f"工作区视图 1 个、角色视图 {len(role_views)} 个；API 巡检 "
                f"{len(probes)} 项（含 WPS 允许列表放行/拒绝对比）"
            )
            out.write("  - 前端离线性校验：页面无任何外部 http(s) 引用，静态资源全部本地化")
        finally:
            cockpit_server.stop()
        json_dump(cockpit_api_results, run_dir / "cockpit" / "api-responses.json")

        # US-7 AC-8 / “开悟”工具适配：WPS 启动器 dry-run 决策
        wps_launcher = WpsLauncher(run_dir / "workspaces", dry_run=True)
        wps_cases = [
            ("工作包模板.docx（允许）", "PRJ001/u.dev/templates/工作包模板.docx"),
            ("开发进展说明.md（拒绝-扩展名）", "PRJ001/u.dev/evidence/开发进展说明.md"),
            ("越权路径（拒绝-路径穿越）", "PRJ001/u.dev/../../../secret.docx"),
        ]
        wps_decisions: list[dict[str, Any]] = []
        for label, wps_path in wps_cases:
            result = wps_launcher.launch(wps_path)
            wps_decisions.append(
                {
                    "case": label,
                    "path": wps_path,
                    "decision": result.decision.value,
                    "detail": result.detail,
                }
            )
            out.write(
                f"    · WPS 适配层（dry-run）：{label} → {result.decision.value}"
                f"（{result.detail}）"
            )
        json_dump(wps_decisions, run_dir / "cockpit" / "wps-decisions.json")

        # US-7 AC-9：驾驶舱重启后从状态文件恢复项目/角色视图
        restart_server = CockpitHttpServer(
            CockpitHttpConfig(
                bind_port=free_port(),
                request_timeout_sec=5,
                state_path=run_dir / "cockpit" / "cockpit-state.json",
                lock_path=run_dir / "cockpit" / "cockpit-restart.lock",
            ),
        )
        try:
            restart_server.start()
            restart_token = restart_server.session_manager.create()
            restart_status, restart_body = _cockpit_api(
                restart_server,
                restart_token,
                f"/api/list_projects?project_id={PROJECT_ID}",
            )
            if restart_status != 200:
                raise RuntimeError(f"cockpit restart persistence failed: {restart_status} {restart_body}")
            out.write(
                f"  - 重启持久化验证（US-7 AC-9）：驾驶舱重启后从状态文件恢复视图，"
                f"项目列表 HTTP {restart_status}"
            )
        finally:
            restart_server.stop()
        audit(ts(1, 11), "u.dev", "cockpit.served")

        # ------------------------------------------------------------------
        # [9] US-8 进展采集：证据识别 + 人工确认（拒绝仅凭文件时间）
        # ------------------------------------------------------------------
        step_banner(out, interactive, 9, "US-8 进展采集：从成果证据识别进展并人工确认")
        dev_ws = workspace_entries["u.dev"]
        dev_ws_root = run_dir / "workspaces" / PROJECT_ID / "u.dev"
        dev_note = dev_ws_root / "evidence" / "开发进展说明.md"

        # US-8 AC-1：工作区文件感知（watcher 只发文件变更事件，不判定任务完成）
        watcher = WorkspaceWatcher(
            dev_ws_root,
            allow_extensions=frozenset({".md", ".docx"}),
            stability_checks=1,
        )
        watcher.scan(now=ts(10, 7))  # 基线快照
        watcher.drain()  # 丢弃基线快照事件
        with dev_note.open("a", encoding="utf-8") as note_file:
            note_file.write("\n- 补充：报表导出样例数据验证通过记录\n")
        watcher_events_all = watcher.scan(now=ts(10, 8))
        watcher_events = [
            event
            for event in watcher_events_all
            if event.relative_path == "evidence/开发进展说明.md"
        ]
        if not watcher_events:
            raise RuntimeError("watcher 未识别到证据文件变更")
        out.write(
            f"  - 工作区感知（US-8 AC-1）：成员更新成果文件后，watcher 识别到 "
            f"{len(watcher_events_all)} 条文件事件，聚焦成果证据 {len(watcher_events)} 条"
        )
        for watcher_event in watcher_events:
            out.write(
                f"    · {watcher_event.kind.value} {watcher_event.relative_path} "
                f"（{watcher_event.size_bytes} 字节，digest "
                f"{watcher_event.digest_hex[:12]}…）"
            )
        watcher_capture = ProgressCaptureService.extract_progress(
            dev_ws,
            tuple(
                EvidenceInput(
                    task_id="n.impl_core",
                    kind=EvidenceKind.DOCUMENT_CONTENT,
                    source_ref=watcher_event.relative_path,
                    text="工作区感知到成果文件更新（watcher 自动发现）",
                    confidence=0.8,
                    evidence_refs=(EvidenceRef(
                        path=watcher_event.relative_path,
                        role="document",
                        media_type=watcher_event.media_type,
                        digest_hex=watcher_event.digest_hex,
                        size_bytes=watcher_event.size_bytes,
                    ),),
                )
                for watcher_event in watcher_events
            ),
            now=ts(10, 8),
        )
        out.write(
            f"  - 感知结果转为 {len(watcher_capture.progress_items)} 条 PROPOSED 进展，"
            "仍需成员确认（AC-7：watcher 不判定完成）"
        )
        json_dump(
            {
                "events": [
                    {
                        "kind": event.kind.value,
                        "relative_path": event.relative_path,
                        "size_bytes": event.size_bytes,
                        "digest_hex": event.digest_hex,
                        "media_type": event.media_type,
                    }
                    for event in watcher_events
                ],
                "proposed_item_count": len(watcher_capture.progress_items),
            },
            run_dir / "reports" / "watcher-events.json",
        )

        dev_bytes = dev_note.read_bytes()
        capture = ProgressCaptureService.extract_progress(
            dev_ws,
            (
                EvidenceInput(
                    task_id="n.impl_core",
                    kind=EvidenceKind.DOCUMENT_CONTENT,
                    source_ref="evidence/开发进展说明.md",
                    text="核心统计功能已完成并通过样例数据自测",
                    confidence=0.9,
                    evidence_refs=(EvidenceRef(
                        path="evidence/开发进展说明.md",
                        role="document",
                        media_type="text/markdown",
                        digest_hex=sm3_hex(provider, dev_bytes),
                        size_bytes=len(dev_bytes),
                    ),),
                ),
                EvidenceInput(
                    task_id="n.impl_report",
                    kind=EvidenceKind.ARTIFACT_FILE,
                    source_ref="evidence/开发进展说明.md",
                    text="报表导出模块完成",
                    confidence=0.85,
                    evidence_refs=(EvidenceRef(
                        path="evidence/开发进展说明.md",
                        role="artifact",
                        media_type="text/markdown",
                        digest_hex=sm3_hex(provider, dev_bytes),
                        size_bytes=len(dev_bytes),
                    ),),
                ),
            ),
            now=ts(10, 8),
        )
        out.write(f"  - 识别到 {len(capture.progress_items)} 条进展（capture={capture.capture_id}），"
                  f"全部为 PROPOSED，需用户确认")
        revised = ProgressCaptureService.revise(
            capture,
            capture.progress_items[0].item_id,
            new_text="核心统计功能已完成，样例数据自测通过（人工复核）",
            reason="u.dev 复核识别结果并修正表述",
            now=ts(10, 8),
        )
        accepted = ProgressCaptureService.accept(
            revised,
            accepted_by="u.dev",
            now=ts(10, 9),
        )
        draft = ProgressCaptureService.to_report_draft(accepted)
        out.write(f"  - u.dev 确认后正式接受（formally_accepted=True），"
                  f"汇报草稿已生成（completed={len(draft.completed_work)}）")
        # US-8 AC-5 驳回路径：低置信度条目被成员驳回，不计入正式汇报
        reject_demo = ProgressCaptureService.extract_progress(
            dev_ws,
            (
                EvidenceInput(
                    task_id="n.impl_report",
                    kind=EvidenceKind.DOCUMENT_CONTENT,
                    source_ref="evidence/开发进展说明.md",
                    text="（低置信度条目）报表模块状态待核实",
                    confidence=0.55,
                    evidence_refs=(EvidenceRef(
                        path="evidence/开发进展说明.md",
                        role="document",
                        media_type="text/markdown",
                        digest_hex=sm3_hex(provider, dev_bytes),
                        size_bytes=len(dev_bytes),
                    ),),
                ),
            ),
            now=ts(10, 8),
        )
        rejected_capture = ProgressCaptureService.reject(
            reject_demo,
            reject_demo.progress_items[0].item_id,
            reason="u.dev 驳回：置信度不足，需补充成果证据",
            now=ts(10, 8),
        )
        out.write(
            "  - 驳回路径（US-8 AC-5）：低置信度条目被 u.dev 驳回（REJECTED），"
            "不计入正式汇报"
        )
        try:
            ProgressCaptureService.extract_progress(
                dev_ws,
                (
                    EvidenceInput(
                        task_id="n.impl_core",
                        kind="file_mtime_only",  # type: ignore[arg-type]
                        source_ref="evidence/开发进展说明.md",
                        text="文件时间变化",
                        confidence=0.9,
                        evidence_refs=(EvidenceRef(
                            path="evidence/开发进展说明.md",
                            role="document",
                            media_type="text/markdown",
                            digest_hex="0" * 64,
                            size_bytes=1,
                        ),),
                    ),
                ),
                now=ts(10, 8),
            )
        except Exception as exc:
            out.write(f"  - AC-7 演示：仅凭文件修改时间的进展输入被拒收"
                      f"（{type(exc).__name__}）")
        else:
            raise RuntimeError("AC-7 fail-closed 未生效：仅凭文件时间不应被接受")
        json_dump(
            {
                "capture_id": accepted.capture_id,
                "items": [
                    {
                        "item_id": item.item_id,
                        "task_id": item.task_id,
                        "kind": item.kind.value,
                        "status": item.status.value,
                        "confidence": item.confidence,
                    }
                    for item in accepted.progress_items
                ],
            },
            run_dir / "reports" / "progress-capture.json",
        )
        audit(ts(10, 10), "u.dev", "progress_capture.accepted")

        # ------------------------------------------------------------------
        # [10] US-9 成果回传：加密成果汇报包（开发完成 + 测试延期两份）
        # ------------------------------------------------------------------
        step_banner(out, interactive, 10, "US-9 成果回传：生成真实加密 RESULT_SUBMISSION 汇报包")

        def build_report(
            *,
            member_id: str,
            task_id: str,
            base_revision: str,
            sequence_no: int,
            status: ReportStatus,
            submitted_at: str,
            completed_work: tuple[str, ...],
            pending_work: tuple[str, ...],
            next_steps: tuple[str, ...],
            risks: tuple[str, ...],
            progress_summary: str,
            artifact_path: str,
            artifact_size: int,
            artifact_digest: str,
        ) -> tuple[Any, bytes, ReportManifest]:
            cert_id = MEMBERS[member_id][0]
            envelope = build_envelope_template(
                sender_cert_id=cert_id,
                recipient_cert_id=OWNER_CERT,
                project_id=PROJECT_ID,
                package_type="RESULT_SUBMISSION",
                sequence_no=sequence_no,
                payload_length=0,
                created_at=submitted_at,
                expires_at="2027-08-01T00:00:00Z",
            )
            manifest = ReportManifest(
                schema_version="1.0",
                package_id=envelope.package_id,
                package_type="RESULT_SUBMISSION",
                project_id=PROJECT_ID,
                task_id=task_id,
                base_revision=base_revision,
                sequence_no=sequence_no,
                submitted_at=submitted_at,
                sender_user_id=member_id.upper().replace(".", "-"),
                sender_client_id=f"CLI-{member_id.upper().replace('.', '-')}",
                sender_organization_id="ORG-B" if member_id in ("u.qa", "u.review") else "ORG-A",
                sender_cert_id=cert_id,
                recipient_user_id="U-PM",
                recipient_client_id="CLI-PM",
                recipient_organization_id="ORG-A",
                recipient_cert_id=OWNER_CERT,
                status=status,
                progress_summary=progress_summary,
                completed_work=completed_work,
                pending_work=pending_work,
                next_steps=next_steps,
                risks=risks,
                artifacts=(ReportArtifact(
                    path=artifact_path,
                    role="artifact",
                    media_type="text/markdown",
                    size=artifact_size,
                    digest_hex=artifact_digest,
                    classification="INTERNAL",
                    required=True,
                ),),
            )
            package, wire = encrypt_and_verify(
                envelope=envelope,
                manifest={
                    "schema_version": "1.0",
                    "package_id": manifest.package_id,
                    "package_type": manifest.package_type,
                    "project_id": manifest.project_id,
                    "task_id": manifest.task_id,
                    "base_revision": manifest.base_revision,
                    "sequence_no": manifest.sequence_no,
                    "status": manifest.status.value,
                    "sender_cert_id": cert_id,
                    "recipient_cert_id": OWNER_CERT,
                },
                content=json.dumps(
                    {
                        "progress_summary": progress_summary,
                        "completed_work": list(completed_work),
                        "pending_work": list(pending_work),
                        "next_steps": list(next_steps),
                        "risks": list(risks),
                        "artifacts": [
                            {
                                "path": artifact_path,
                                "digest_hex": artifact_digest,
                                "size": artifact_size,
                            }
                        ],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8"),
                provider=provider,
                sender_cert=cert_id,
                recipient_cert=OWNER_CERT,
                signed_at=submitted_at,
            )
            return package, wire, manifest

        dev_evidence = (run_dir / "workspaces" / PROJECT_ID / "u.dev" / "evidence" / "开发进展说明.md")
        dev_pkg, dev_wire, dev_manifest = build_report(
            member_id="u.dev",
            task_id="n.impl_core",
            base_revision=BASE_REV,
            sequence_no=1,
            status=ReportStatus.COMPLETED,
            submitted_at=ts(10, 11),
            completed_work=("核心统计功能实现", "报表导出功能实现", "样例数据自测"),
            pending_work=(),
            next_steps=(),
            risks=(),
            progress_summary="开发任务已完成并通过自测",
            artifact_path="evidence/开发进展说明.md",
            artifact_size=dev_evidence.stat().st_size,
            artifact_digest=sm3_hex(provider, dev_evidence.read_bytes()),
        )
        qa_stale_pkg, qa_stale_wire, qa_stale_manifest = build_report(
            member_id="u.qa",
            task_id="n.test_exec",
            base_revision=BASE_REV,  # 测试组仍引用旧基线（演示三方冲突）
            sequence_no=1,
            status=ReportStatus.AT_RISK,
            submitted_at=ts(19, 9),
            completed_work=("测试用例设计", "功能测试执行"),
            pending_work=("回归测试执行",),
            next_steps=("等待协调资源完成回归测试",),
            risks=("回归测试超出计划期",),
            progress_summary="功能测试通过，回归测试延期，请求协调",
            artifact_path="evidence/测试报告.md",
            artifact_size=(run_dir / "workspaces" / PROJECT_ID / "u.qa" / "evidence" / "测试报告.md").stat().st_size,
            artifact_digest=sm3_hex(
                provider,
                (run_dir / "workspaces" / PROJECT_ID / "u.qa" / "evidence" / "测试报告.md").read_bytes(),
            ),
        )
        for name, pkg, wire in (
            ("u.dev 完成汇报", dev_pkg, dev_wire),
            ("u.qa 延期汇报(旧基线)", qa_stale_pkg, qa_stale_wire),
        ):
            filename = (
                f"RESULT_SUBMISSION_{PROJECT_ID}_{pkg.envelope.package_id}.agent"
            )
            (run_dir / "reports" / filename).write_bytes(wire)
            out.write(f"  - {name}：{filename}（sha256={hashlib.sha256(wire).hexdigest()[:16]}…）")
        audit(ts(10, 12), "u.dev", "report.exported")

        # ------------------------------------------------------------------
        # [11] US-10 状态合并：版本审核、三方冲突与主版本更新
        # ------------------------------------------------------------------
        step_banner(out, interactive, 11, "US-10 状态合并：成果审核、冲突识别与项目主版本更新")
        authority = _signing_authority()
        receipt_repository = MergeReceiptRepository.create(
            run_dir / "merge" / "receipts.sqlite3",
            authority,
            signer=DemoSigner(),
            freshness=DemoFreshnessAuthority(),
        )
        merge_engine = MergeEngine(
            receipt_repository=receipt_repository,
            receipt_authority=authority,
        )
        current_baseline = baseline_v1

        def owner_merge(package: Any, wire: bytes, manifest: ReportManifest, *, now: str, decided_at: str) -> Any:
            imported = import_package_committed(
                package,
                wire,
                sender_cert=manifest.sender_cert_id,
                recipient_cert=manifest.recipient_cert_id,
                project_id=PROJECT_ID,
                sequence_no=manifest.sequence_no,
                base_revision=manifest.base_revision,
                current_revision=manifest.base_revision,
                processed_at=decided_at,
            )
            return merge_and_analyze(
                engine=merge_engine,
                import_outcome=imported,
                report=manifest,
                baseline=current_baseline,
                store=ProcessedPackageStore.empty(),
                receipt_repository=receipt_repository,
                decided_at=decided_at,
                now=now,
                authorized_recipient_certs=frozenset({OWNER_CERT}),
            )

        # 开发完成汇报：正常审核 → R0002
        outcome_dev = owner_merge(
            dev_pkg, dev_wire, dev_manifest,
            now=ts(10, 13), decided_at=ts(10, 12),
        )
        if not outcome_dev.commit.proposal.accepted:
            raise RuntimeError(
                "dev merge rejected: "
                f"accepted={outcome_dev.commit.proposal.accepted} "
                f"has_conflict={outcome_dev.commit.proposal.record.has_conflict} "
                f"reason={outcome_dev.commit.proposal.rejection_reason} "
                f"field_merges={[fm.to_dict() for fm in outcome_dev.commit.proposal.record.field_merges]}"
            )
        assert outcome_dev.commit.receipt is not None
        current_baseline = outcome_dev.commit.proposal.new_baseline
        out.write(f"  - u.dev 完成汇报合并通过 → 主版本 {current_baseline.version} "
                  f"（{current_baseline.version:04d}）")
        out.write(f"    签名回执 {outcome_dev.commit.receipt.receipt_id}，"
                  f"package={outcome_dev.commit.receipt.package_id[:12]}…")
        out.write(
            f"    风险预检：{len(outcome_dev.risk_report.risks) if outcome_dev.risk_report else 0} 项"
            f"（{', '.join(r.kind.value for r in outcome_dev.risk_report.risks) if outcome_dev.risk_report else '-'}）"
        )

        # u.qa 旧基线汇报：三方冲突 → 暂不合并
        outcome_conflict = owner_merge(
            qa_stale_pkg, qa_stale_wire, qa_stale_manifest,
            now=ts(19, 11), decided_at=ts(19, 10),
        )
        if outcome_conflict.commit.proposal.accepted:
            raise RuntimeError("旧基线汇报不应被直接合并")
        out.write("  - u.qa 汇报引用旧基线（R0001 ≠ 当前主版本 R0002）→ 冲突挂起：")
        for fm in outcome_conflict.commit.proposal.record.field_merges[:5]:
            out.write(
                f"    字段 {fm.field_path}: 原基线={jsonable(fm.original_value)} "
                f"本地={jsonable(fm.current_value)} 提交={jsonable(fm.submitted_value)} "
                f"→ {fm.decision.value}"
            )
        out.write(f"    拒绝原因：{outcome_conflict.commit.proposal.rejection_reason}")

        # 负责人下发任务变更包（TASK_CHANGE，基线上移）给测试组
        task_change_content = json.dumps(
            {
                "change": "测试计划调整：请按新基线 R0002 提交测试进展，"
                          "回归测试计划截止时间不变",
                "base_revision": "PRJ001-R0002",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        change_pkg, change_wire = build_and_verify_package(
            provider=provider,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            package_type="TASK_CHANGE",
            project_id=PROJECT_ID,
            task_id=TASK_ID,
            base_revision="PRJ001-R0002",
            sequence_no=2,
            manifest={
                "event_id": "ev.tool.002",
                "project_id": PROJECT_ID,
                "task_id": TASK_ID,
                "base_revision": "PRJ001-R0002",
                "payload_digest": "0" * 64,
            },
            content=task_change_content,
            signed_at=ts(19, 12),
            expires_at="2027-08-01T00:00:00Z",
        )
        (run_dir / "outbox" / f"TASK_CHANGE_{PROJECT_ID}_{change_pkg.envelope.package_id}.agent").write_bytes(change_wire)
        imported_change = import_package_committed(
            change_pkg,
            change_wire,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            project_id=PROJECT_ID,
            sequence_no=2,
            base_revision="PRJ001-R0002",
            current_revision="PRJ001-R0002",
            processed_at=ts(19, 13),
        )
        init_again = init_service.init_from_import(
            imported_change,
            member_registries["u.qa"],
            role_id="u.qa",
            revision="PRJ001-R0002",
        )
        out.write("  - 任务变更包（TASK_CHANGE，新基线 R0002）已下发并导入；")
        out.write(
            f"    重复绑定检查：created={init_again.created}（AC-8 幂等：变更包不重建工作区，"
            f"仅更新客户端基线修订）；{init_again.failure_reason}"
        )

        # u.qa 按新基线重新提交 → R0003 + 风险分析（项目截止已过）
        qa_final_pkg, qa_final_wire, qa_final_manifest = build_report(
            member_id="u.qa",
            task_id="n.test_exec",
            base_revision="PRJ001-R0002",
            sequence_no=2,
            status=ReportStatus.COMPLETED,
            submitted_at=ts(21, 9),
            completed_work=("测试用例设计", "功能测试执行", "回归测试执行"),
            pending_work=(),
            next_steps=(),
            risks=(),
            progress_summary="测试全部完成，但项目整体已超过计划截止时间",
            artifact_path="evidence/测试报告.md",
            artifact_size=(run_dir / "workspaces" / PROJECT_ID / "u.qa" / "evidence" / "测试报告.md").stat().st_size,
            artifact_digest=sm3_hex(
                provider,
                (run_dir / "workspaces" / PROJECT_ID / "u.qa" / "evidence" / "测试报告.md").read_bytes(),
            ),
        )
        (run_dir / "reports" / f"RESULT_SUBMISSION_{PROJECT_ID}_{qa_final_pkg.envelope.package_id}.agent").write_bytes(qa_final_wire)
        outcome_qa = owner_merge(
            qa_final_pkg, qa_final_wire, qa_final_manifest,
            now=ts(21, 11), decided_at=ts(21, 10),
        )
        assert outcome_qa.commit.receipt is not None
        current_baseline = outcome_qa.commit.proposal.new_baseline
        final_risk = outcome_qa.risk_report
        out.write(f"  - u.qa 按新基线重新提交并合并 → 主版本 {current_baseline.version}（R0003）")
        out.write(f"    签名回执 {outcome_qa.commit.receipt.receipt_id}")
        json_dump(
            {
                "merges": [
                    {
                        "reporter": "u.dev",
                        "accepted": True,
                        "merged_version": "PRJ001-R0002",
                        "receipt_id": outcome_dev.commit.receipt.receipt_id,
                    },
                    {
                        "reporter": "u.qa",
                        "accepted": False,
                        "has_conflict": True,
                        "reason": outcome_conflict.commit.proposal.rejection_reason,
                        "field_merges": [
                            fm.to_dict()
                            for fm in outcome_conflict.commit.proposal.record.field_merges[:5]
                        ],
                    },
                    {
                        "reporter": "u.qa",
                        "accepted": True,
                        "merged_version": "PRJ001-R0003",
                        "receipt_id": outcome_qa.commit.receipt.receipt_id,
                    },
                ]
            },
            run_dir / "merge" / "merge-records.json",
        )
        audit(ts(21, 12), "u.pm", "merge.committed")

        # ------------------------------------------------------------------
        # [12] US-11 风险预警
        # ------------------------------------------------------------------
        step_banner(out, interactive, 12, "US-11 风险预警：合并后自动分析延期与关联影响")
        if final_risk is None:
            raise RuntimeError("缺少风险报告")
        for risk in final_risk.risks:
            out.write(
                f"  - {risk.risk_id} [{risk.source.value}] 严重度 {risk.severity}: "
                f"{risk.kind.value}"
            )
            out.write(f"    依据：{risk.basis}")
            out.write(f"    影响任务：{list(risk.affected_tasks)}")
            out.write(f"    处置建议：{risk.recommendation}（建议完成时间 {risk.suggested_deadline}）")
        out.write(f"  - 建议召开任务协同会议：{final_risk.coordination_meeting_recommended}")
        json_dump(final_risk.to_dict(), run_dir / "risk" / "risk-report.json")
        audit(ts(21, 13), "u.pm", "risk.analyzed")

        # ------------------------------------------------------------------
        # [13] US-12 督办与会议协同
        # ------------------------------------------------------------------
        step_banner(out, interactive, 13, "US-12 督办与会议协同：督办事项、会议提案、结论转任务")
        supervisor = SupervisionCoordinator()
        supervision = supervisor.coordinate(
            risk_report=final_risk,
            project_recipient_cert_id=OWNER_CERT,
            now=ts(21, 14),
        )
        for item in supervision.items:
            out.write(
                f"  - 督办事项 {item.item_id}: {item.risk_kind.value} → "
                f"责任主体 {item.responsible_subject}，截止 {item.due_at}，"
                f"关闭条件：{item.closing_condition}"
            )
        if supervision.meeting_proposal is not None:
            out.write(f"  - 会议提案 {supervision.meeting_proposal.proposal_id}（面向 {OWNER_CERT}）：")
            for agenda in supervision.meeting_proposal.agenda:
                out.write(f"    议题 {agenda.agenda_id}: {agenda.title}")
                out.write(f"      背景：{agenda.background}")
                for q in agenda.open_questions:
                    out.write(f"      待决策：{q}")
        for conclusion in supervision.conclusions:
            out.write(
                f"  - 会议结论转{conclusion.kind.value}: {conclusion.subject_ref} — {conclusion.note}"
            )
        json_dump(
            {
                "items": [
                    {
                        "item_id": i.item_id,
                        "project_id": i.project_id,
                        "risk_id": i.risk_id,
                        "risk_kind": i.risk_kind.value,
                        "responsible_subject": i.responsible_subject,
                        "due_at": i.due_at,
                        "closing_condition": i.closing_condition,
                        "affected_tasks": list(i.affected_tasks),
                        "created_at": i.created_at,
                    }
                    for i in supervision.items
                ],
                "meeting_proposal": (
                    {
                        "proposal_id": supervision.meeting_proposal.proposal_id,
                        "agenda": [
                            {"agenda_id": a.agenda_id, "title": a.title, "background": a.background}
                            for a in supervision.meeting_proposal.agenda
                        ],
                    }
                    if supervision.meeting_proposal is not None else None
                ),
                "conclusions": [c.to_dict() for c in supervision.conclusions],
            },
            run_dir / "supervision" / "supervision-outcome.json",
        )
        audit(ts(21, 15), "u.pm", "supervision.coordinated")

        # 会议结论转任务：以 MEETING_DECISION 任务包下发
        meeting_conclusions = [
            {"kind": c.kind.value, "subject": c.subject_ref, "note": c.note}
            for c in supervision.conclusions
        ]
        meeting_content = json.dumps(
            {
                "title": "测试计划协调会议结论",
                "conclusions": meeting_conclusions,
                "new_task": "n.test_exec 整改：补充回归结果复核并在 8/25 前完成验收评审准备",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        meeting_pkg, meeting_wire = build_and_verify_package(
            provider=provider,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            package_type="MEETING_DECISION",
            project_id=PROJECT_ID,
            task_id=TASK_ID,
            base_revision="PRJ001-R0003",
            sequence_no=3,
            manifest={
                "event_id": "ev.tool.003",
                "project_id": PROJECT_ID,
                "task_id": TASK_ID,
                "base_revision": "PRJ001-R0003",
                "payload_digest": "0" * 64,
            },
            content=meeting_content,
            signed_at=ts(21, 16),
            expires_at="2027-08-01T00:00:00Z",
        )
        (run_dir / "outbox" / f"MEETING_DECISION_{PROJECT_ID}_{meeting_pkg.envelope.package_id}.agent").write_bytes(meeting_wire)
        out.write(f"  - 会议决策包已下发（MEETING_DECISION，接收人 u.qa）："
                  f"{meeting_pkg.envelope.package_id[:12]}…")
        # 督办包（SUPERVISION_NOTICE）：确认的督办事项正式下发到责任主体
        supervision_notice_content = json.dumps(
            {
                "title": "测试延期整改督办",
                "responsible_subject": "u.qa",
                "items": [
                    {
                        "item_id": item.item_id,
                        "risk_kind": item.risk_kind.value,
                        "due_at": item.due_at,
                        "closing_condition": item.closing_condition,
                    }
                    for item in supervision.items
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        notice_pkg, notice_wire = build_and_verify_package(
            provider=provider,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            package_type="SUPERVISION_NOTICE",
            project_id=PROJECT_ID,
            task_id=TASK_ID,
            base_revision="PRJ001-R0003",
            sequence_no=4,
            manifest={
                "event_id": "ev.tool.notice.001",
                "project_id": PROJECT_ID,
                "task_id": TASK_ID,
                "base_revision": "PRJ001-R0003",
                "payload_digest": "0" * 64,
            },
            content=supervision_notice_content,
            signed_at=ts(21, 17),
            expires_at="2027-08-01T00:00:00Z",
        )
        (run_dir / "outbox" / f"SUPERVISION_NOTICE_{PROJECT_ID}_{notice_pkg.envelope.package_id}.agent").write_bytes(notice_wire)
        out.write(
            f"  - 督办包已下发（SUPERVISION_NOTICE，接收人 u.qa，"
            f"{len(supervision.items)} 项督办）：{notice_pkg.envelope.package_id[:12]}…"
        )

        # ------------------------------------------------------------------
        # [14] US-13 决策简报
        # ------------------------------------------------------------------
        step_banner(out, interactive, 14, "US-13 决策简报：仅使用已确认状态生成阶段简报（WPS 模板）")
        template_ref = "templates/decision-brief.docx"
        write_docx(run_dir / template_ref)
        templates = ApprovedTemplateRegistry(run_dir)
        approval = templates.approve(
            approval_id="approval.template.tool-demo",
            template_ref=template_ref,
        )
        risks_repo = RiskConfirmationRepository(authority)
        receipt = outcome_qa.commit.receipt
        assert receipt is not None
        confirmation = risks_repo.confirm(
            receipt_id=receipt.receipt_id,
            receipt_repository=receipt_repository,
            risk_report=final_risk,
            confirmed_at=ts(21, 17),
            confirmed_by=OWNER_CERT,
            event_id="risk.confirm.tool-demo",
        )
        briefs = DecisionBriefRepository()
        brief = DecisionBriefService().generate(
            receipt_id=receipt.receipt_id,
            receipt_repository=receipt_repository,
            risk_confirmation_id=confirmation.confirmation_id,
            risk_repository=risks_repo,
            brief_repository=briefs,
            brief_type=BriefType.STAGE,
            template_ref=template_ref,
            template_approval_id=approval.approval_id,
            template_registry=templates,
            generated_at=ts(21, 18),
            actor_id=OWNER_CERT,
            event_id="brief.generate.tool-demo",
        )
        out.write(f"  - 简报 {brief.brief_id}（{brief.brief_type.value}，修订 {brief.current.revision}）")
        out.write(f"    总体进展：{brief.current.content.overall_progress[0].text}")
        out.write(f"    高风险：{len(brief.current.content.high_risk_items)} 项；"
                  f"待决策：{len(brief.current.content.pending_decisions)} 项")
        out.write(
            f"    WPS 工具请求：{brief.wps_request.template_ref}（模板已批准 "
            f"{approval.template_digest[:12]}…）"
        )
        json_dump(
            {
                "brief_id": brief.brief_id,
                "brief_type": brief.brief_type.value,
                "revision": brief.current.revision,
                "overall_progress": [c.text for c in brief.current.content.overall_progress],
                "high_risk_items": [c.text for c in brief.current.content.high_risk_items],
                "pending_decisions": [c.text for c in brief.current.content.pending_decisions],
                "wps_request": dataclasses.asdict(brief.wps_request),
            },
            run_dir / "brief" / "decision-brief.json",
        )
        brief_docx = run_dir / "brief" / "决策简报-阶段.docx"
        write_brief_docx(brief, brief_docx)
        out.write(f"  - 简报 DOCX 已生成：{brief_docx.name}（无宏，WPS 允许列表内可打开）")
        brief_launcher = WpsLauncher(run_dir, dry_run=True)
        brief_open = brief_launcher.launch("brief/决策简报-阶段.docx")
        out.write(
            f"  - WPS 适配层打开简报文档（dry-run）：{brief_open.decision.value}"
            f"（{brief_open.detail}）"
        )
        audit(ts(21, 19), "u.pm", "decision_brief.generated")

        # 第二轮任务循环（MVP 演示闭环第 17 步）：
        # 会议结论转整改任务 → 任务包下发 → 成员回传 → 合并（回执链连续）
        out.write("")
        out.write("=" * 78)
        out.write("[14b] 第二轮任务循环：会议结论转整改任务、重新下发并回传合并")
        out.write("=" * 78)
        cycle2_content = json.dumps(
            {
                "title": "回归结果复核与验收评审准备",
                "base_revision": "PRJ001-R0003",
                "role": "测试工程师",
                "task_id": "n.test_exec",
                "origin": "meeting.PRJ001.协调会议结论转整改任务",
                "deliverable_requirements": "对 n.test_exec 补充回归结果复核，交付复核记录并经负责人确认",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        cycle2_pkg, cycle2_wire = build_and_verify_package(
            provider=provider,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            package_type="TASK_ASSIGNMENT",
            project_id=PROJECT_ID,
            task_id="n.test_exec",
            base_revision="PRJ001-R0003",
            sequence_no=5,
            manifest={
                "event_id": "ev.tool.004",
                "project_id": PROJECT_ID,
                "task_id": "n.test_exec",
                "base_revision": "PRJ001-R0003",
                "payload_digest": "0" * 64,
            },
            content=cycle2_content,
            signed_at=ts(22, 9),
            expires_at="2027-08-01T00:00:00Z",
        )
        (run_dir / "outbox" / f"TASK_ASSIGNMENT_{PROJECT_ID}_{cycle2_pkg.envelope.package_id}.agent").write_bytes(cycle2_wire)
        import_package_committed(
            cycle2_pkg,
            cycle2_wire,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            project_id=PROJECT_ID,
            sequence_no=5,
            base_revision="PRJ001-R0003",
            current_revision="PRJ001-R0003",
            processed_at=ts(22, 10),
        )
        out.write(
            f"  - 第二轮整改任务包已下发并导入（TASK_ASSIGNMENT / n.test_exec 回归复核，"
            f"基线 R0003）：{cycle2_pkg.envelope.package_id[:12]}…"
        )

        qa_evidence = run_dir / "workspaces" / PROJECT_ID / "u.qa" / "evidence" / "测试报告.md"
        qa2_pkg, qa2_wire, qa2_manifest = build_report(
            member_id="u.qa",
            task_id="n.test_exec",
            base_revision="PRJ001-R0003",
            sequence_no=3,
            status=ReportStatus.COMPLETED,
            submitted_at=ts(22, 12),
            completed_work=("回归结果复核完成", "验收评审准备完成"),
            pending_work=(),
            next_steps=(),
            risks=(),
            progress_summary="第二轮任务完成：回归复核与验收准备已就绪",
            artifact_path="evidence/测试报告.md",
            artifact_size=qa_evidence.stat().st_size,
            artifact_digest=sm3_hex(provider, qa_evidence.read_bytes()),
        )
        (run_dir / "reports" / f"RESULT_SUBMISSION_{PROJECT_ID}_{qa2_pkg.envelope.package_id}.agent").write_bytes(qa2_wire)
        outcome_c2 = owner_merge(
            qa2_pkg, qa2_wire, qa2_manifest,
            now=ts(22, 13), decided_at=ts(22, 12),
        )
        if not outcome_c2.commit.proposal.accepted:
            raise RuntimeError(
                "cycle2 merge rejected: "
                f"accepted={outcome_c2.commit.proposal.accepted} "
                f"has_conflict={outcome_c2.commit.proposal.record.has_conflict} "
                f"reason={outcome_c2.commit.proposal.rejection_reason} "
                f"field_merges={[fm.to_dict() for fm in outcome_c2.commit.proposal.record.field_merges]}"
            )
        assert outcome_c2.commit.receipt is not None
        current_baseline = outcome_c2.commit.proposal.new_baseline
        out.write(
            f"  - 第二轮成果回传合并通过 → 主版本 {current_baseline.version}"
            f"（R0004），签名回执 {outcome_c2.commit.receipt.receipt_id[:16]}…"
        )
        audit(ts(22, 13), "u.pm", "cycle2.merge.committed")

        # US-13 简报类型扩展：基于第二轮合并结果生成“风险专题”简报
        out.write("")
        out.write("=" * 78)
        out.write("[14c] US-13 简报类型扩展：风险专题简报")
        out.write("=" * 78)
        receipt_c2 = outcome_c2.commit.receipt
        assert receipt_c2 is not None
        assert outcome_c2.risk_report is not None
        confirmation_c2 = risks_repo.confirm(
            receipt_id=receipt_c2.receipt_id,
            receipt_repository=receipt_repository,
            risk_report=outcome_c2.risk_report,
            confirmed_at=ts(22, 14),
            confirmed_by=OWNER_CERT,
            event_id="risk.confirm.cycle2",
        )
        topic_brief = DecisionBriefService().generate(
            receipt_id=receipt_c2.receipt_id,
            receipt_repository=receipt_repository,
            risk_confirmation_id=confirmation_c2.confirmation_id,
            risk_repository=risks_repo,
            brief_repository=briefs,
            brief_type=BriefType.RISK_TOPIC,
            template_ref=template_ref,
            template_approval_id=approval.approval_id,
            template_registry=templates,
            generated_at=ts(22, 15),
            actor_id=OWNER_CERT,
            event_id="brief.generate.risk-topic",
            topic_risk_ids=(outcome_c2.risk_report.risks[0].risk_id,),
        )
        out.write(
            f"  - 风险专题简报 {topic_brief.brief_id}（{topic_brief.brief_type.value}，"
            f"修订 {topic_brief.current.revision}）"
        )
        out.write(
            f"    专题风险：{[c.text for c in topic_brief.current.content.high_risk_items]}"
        )
        json_dump(
            {
                "brief_id": topic_brief.brief_id,
                "brief_type": topic_brief.brief_type.value,
                "revision": topic_brief.current.revision,
                "topic_risk_ids": [outcome_c2.risk_report.risks[0].risk_id],
                "high_risk_items": [
                    c.text for c in topic_brief.current.content.high_risk_items
                ],
            },
            run_dir / "brief" / "risk-topic-brief.json",
        )
        write_brief_docx(topic_brief, run_dir / "brief" / "风险专题简报.docx")
        out.write("  - 风险专题简报 DOCX 已生成：风险专题简报.docx")
        audit(ts(22, 15), "u.pm", "decision_brief.risk_topic.generated")

        # [14d] 全员成果回传与结项：文档、验收评审报告合并（回执链连续至 R0006）
        out.write("")
        out.write("=" * 78)
        out.write("[14d] 全员成果回传与结项：文档、验收评审报告合并")
        out.write("=" * 78)
        # 先向文档/评审成员下发 TASK_CHANGE 同步最新基线（R0004）
        for member_id, task_ref in (
            ("u.doc", "n.docs_guide"),
            ("u.review", "n.acceptance"),
        ):
            change_content = json.dumps(
                {
                    "change": "基线同步：请按 PRJ001-R0004 完成交付物并回传",
                    "base_revision": "PRJ001-R0004",
                    "task_id": task_ref,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            change_pkg, change_wire = build_and_verify_package(
                provider=provider,
                sender_cert=OWNER_CERT,
                recipient_cert=MEMBERS[member_id][0],
                package_type="TASK_CHANGE",
                project_id=PROJECT_ID,
                task_id=task_ref,
                base_revision="PRJ001-R0004",
                sequence_no=2,
                manifest={
                    "event_id": f"ev.tool.change.{member_id}",
                    "project_id": PROJECT_ID,
                    "task_id": task_ref,
                    "base_revision": "PRJ001-R0004",
                    "payload_digest": "0" * 64,
                },
                content=change_content,
                signed_at=ts(22, 15),
                expires_at="2027-08-01T00:00:00Z",
            )
            (run_dir / "outbox" / f"TASK_CHANGE_{PROJECT_ID}_{change_pkg.envelope.package_id}.agent").write_bytes(change_wire)
            import_package_committed(
                change_pkg,
                change_wire,
                sender_cert=OWNER_CERT,
                recipient_cert=MEMBERS[member_id][0],
                project_id=PROJECT_ID,
                sequence_no=2,
                base_revision="PRJ001-R0004",
                current_revision="PRJ001-R0004",
                processed_at=ts(22, 15),
            )
            out.write(
                f"  - TASK_CHANGE 已下发并导入：{member_id} 基线同步至 R0004"
                f"（任务 {task_ref}）"
            )
        out.write("  - 文档与评审成员按最新主版本完成交付物并回传")

        doc_evidence = (
            run_dir / "workspaces" / PROJECT_ID / "u.doc" / "evidence" / "用户手册大纲.md"
        )
        doc_pkg, doc_wire, doc_manifest = build_report(
            member_id="u.doc",
            task_id="n.docs_guide",
            base_revision="PRJ001-R0004",
            sequence_no=1,
            status=ReportStatus.COMPLETED,
            submitted_at=ts(22, 16),
            completed_work=("用户手册初稿完成", "交付说明完成"),
            pending_work=(),
            next_steps=(),
            risks=(),
            progress_summary="文档交付完成：用户手册与交付说明已就绪",
            artifact_path="evidence/用户手册大纲.md",
            artifact_size=doc_evidence.stat().st_size,
            artifact_digest=sm3_hex(provider, doc_evidence.read_bytes()),
        )
        (run_dir / "reports" / f"RESULT_SUBMISSION_{PROJECT_ID}_{doc_pkg.envelope.package_id}.agent").write_bytes(doc_wire)
        outcome_doc = owner_merge(
            doc_pkg, doc_wire, doc_manifest,
            now=ts(22, 17), decided_at=ts(22, 16),
        )
        if not outcome_doc.commit.proposal.accepted:
            raise RuntimeError(f"doc merge rejected: {outcome_doc.commit.proposal.rejection_reason}")
        assert outcome_doc.commit.receipt is not None
        current_baseline = outcome_doc.commit.proposal.new_baseline
        out.write(
            f"  - u.doc 文档汇报合并通过 → 主版本 {current_baseline.version}"
            f"（R0005），签名回执 {outcome_doc.commit.receipt.receipt_id[:16]}…"
        )

        review_evidence = (
            run_dir / "workspaces" / PROJECT_ID / "u.review" / "evidence" / "评审意见.md"
        )
        review_pkg, review_wire, review_manifest = build_report(
            member_id="u.review",
            task_id="n.acceptance",
            base_revision="PRJ001-R0005",
            sequence_no=1,
            status=ReportStatus.COMPLETED,
            submitted_at=ts(22, 18),
            completed_work=("验收评审完成", "验收结论签署"),
            pending_work=(),
            next_steps=(),
            risks=(),
            progress_summary="验收评审通过，项目具备交付条件",
            artifact_path="evidence/评审意见.md",
            artifact_size=review_evidence.stat().st_size,
            artifact_digest=sm3_hex(provider, review_evidence.read_bytes()),
        )
        (run_dir / "reports" / f"RESULT_SUBMISSION_{PROJECT_ID}_{review_pkg.envelope.package_id}.agent").write_bytes(review_wire)
        outcome_review = owner_merge(
            review_pkg, review_wire, review_manifest,
            now=ts(22, 19), decided_at=ts(22, 18),
        )
        if not outcome_review.commit.proposal.accepted:
            raise RuntimeError(f"review merge rejected: {outcome_review.commit.proposal.rejection_reason}")
        assert outcome_review.commit.receipt is not None
        current_baseline = outcome_review.commit.proposal.new_baseline
        out.write(
            f"  - u.review 验收汇报合并通过 → 主版本 {current_baseline.version}"
            f"（R0006），签名回执 {outcome_review.commit.receipt.receipt_id[:16]}…"
        )
        out.write(
            "  - 全员成果回传完成：研发/测试/文档/评审四类角色均贡献成果，"
            "主版本连续至 R0006"
        )

        # 周期简报：US-13 三种简报类型全覆盖
        receipt_review = outcome_review.commit.receipt
        assert receipt_review is not None
        assert outcome_review.risk_report is not None
        confirmation_review = risks_repo.confirm(
            receipt_id=receipt_review.receipt_id,
            receipt_repository=receipt_repository,
            risk_report=outcome_review.risk_report,
            confirmed_at=ts(22, 20),
            confirmed_by=OWNER_CERT,
            event_id="risk.confirm.final",
        )
        periodic_brief = DecisionBriefService().generate(
            receipt_id=receipt_review.receipt_id,
            receipt_repository=receipt_repository,
            risk_confirmation_id=confirmation_review.confirmation_id,
            risk_repository=risks_repo,
            brief_repository=briefs,
            brief_type=BriefType.PERIODIC,
            template_ref=template_ref,
            template_approval_id=approval.approval_id,
            template_registry=templates,
            generated_at=ts(22, 21),
            actor_id=OWNER_CERT,
            event_id="brief.generate.periodic",
            period_start="2026-08-01T00:00:00Z",
            period_end="2026-08-31T00:00:00Z",
        )
        out.write(
            f"  - 周期简报 {periodic_brief.brief_id}（{periodic_brief.brief_type.value}，"
            f"修订 {periodic_brief.current.revision}）"
        )
        json_dump(
            {
                "brief_id": periodic_brief.brief_id,
                "brief_type": periodic_brief.brief_type.value,
                "revision": periodic_brief.current.revision,
                "overall_progress": [
                    c.text for c in periodic_brief.current.content.overall_progress
                ],
            },
            run_dir / "brief" / "periodic-brief.json",
        )
        write_brief_docx(periodic_brief, run_dir / "brief" / "周期简报.docx")
        out.write("  - 周期简报 DOCX 已生成：周期简报.docx")
        audit(ts(22, 21), "u.pm", "decision_brief.periodic.generated")

        # ------------------------------------------------------------------
        # [15] US-14 成果沉淀：知识包 + 复盘草稿 + 审批入库
        # ------------------------------------------------------------------
        step_banner(out, interactive, 15, "US-14 成果沉淀：知识包、复盘草稿与审批入库")
        risk_dict = final_risk.to_dict()
        risk_dict["title"] = "测试延期风险预警"
        risk_dict["summary"] = "回归测试超出项目计划截止时间，建议协调资源并召开会议"
        cycle2_risk_dict = outcome_c2.risk_report.to_dict()
        cycle2_risk_dict["title"] = "第二轮合并风险预检"
        cycle2_risk_dict["summary"] = "第二轮任务完成后对项目整体延期的持续跟踪"
        doc_risk_dict = outcome_doc.risk_report.to_dict()
        doc_risk_dict["title"] = "文档交付合并风险预检"
        doc_risk_dict["summary"] = "文档交付后的风险状态跟踪"
        review_risk_dict = outcome_review.risk_report.to_dict()
        review_risk_dict["title"] = "验收结项风险预检"
        review_risk_dict["summary"] = "验收评审通过后的结项风险跟踪"
        bundle = KnowledgeBaseFacade.aggregate(
            project_id=PROJECT_ID,
            baseline={
                "title": project_input["title"],
                "summary": project_input["objective"],
                "stages": [wp.standard_stage for wp in current_baseline.work_packages],
                "work_packages": [wp.work_package_id for wp in current_baseline.work_packages],
            },
            merge_records=(
                outcome_dev.commit.proposal.record.to_dict(),
                outcome_conflict.commit.proposal.record.to_dict(),
                outcome_qa.commit.proposal.record.to_dict(),
                outcome_c2.commit.proposal.record.to_dict(),
                outcome_doc.commit.proposal.record.to_dict(),
                outcome_review.commit.proposal.record.to_dict(),
            ),
            risk_reports=(risk_dict, cycle2_risk_dict, doc_risk_dict, review_risk_dict),
            decision_briefs=(
                {
                    "id": brief.brief_id,
                    "title": "阶段决策简报",
                    "summary": "基于已确认状态生成，包含高风险与待决策事项",
                },
                {
                    "id": topic_brief.brief_id,
                    "title": "风险专题简报",
                    "summary": "聚焦 deadline_overrun 风险的专题分析",
                },
                {
                    "id": periodic_brief.brief_id,
                    "title": "周期简报",
                    "summary": "2026-08 周期项目进展与决策事项汇总",
                },
            ),
            meeting_conclusions=tuple(
                {"id": f"conclusion.{i}", "title": c.kind.value, "summary": c.note}
                for i, c in enumerate(supervision.conclusions)
            ),
            progress_captures=(
                {
                    "id": accepted.capture_id,
                    "title": "研发进展采集",
                    "summary": "核心功能与报表模块完成，经 u.dev 确认",
                },
            ),
            model_summaries=(
                {
                    "id": "ms.1",
                    "title": "项目复盘模型总结",
                    "summary": "跨单位小工具开发以离线任务包协同可行；"
                               "测试任务需预留缓冲并尽早下发变更包",
                },
            ),
            now=ts(21, 20),
        )
        out.write(f"  - 知识包 {bundle.bundle_id}：{len(bundle.entries)} 条知识、"
                  f"{len(bundle.reusable_templates)} 个可复用模板、复盘草稿 "
                  f"{len(bundle.retrospective.body_sections)} 节")
        out.write(f"    密级：{bundle.bundle_classification.value}；"
                  f"模型总结条目需负责人审批（AC-7）")
        decisions = tuple(
            ReviewDecision(
                decision_id=f"rev.tool.{i}",
                entry_id=entry.entry_id,
                decision=ReviewDecisionKind.APPROVE,
                decided_by="u.pm",
                reason="负责人审批入库",
                decided_at=ts(21, 21),
            )
            for i, entry in enumerate(bundle.entries)
        )
        committed_bundle = KnowledgeBaseFacade.review(
            bundle,
            decisions=decisions,
            now=ts(21, 21),
        )
        out.write(
            f"  - 负责人审批通过，知识包正式入库（formally_committed="
            f"{committed_bundle.formally_committed}）"
        )
        knowledge_store = KnowledgeStore.create(run_dir / "knowledge" / "knowledge.db")
        knowledge_store.save(committed_bundle, now=ts(21, 22))
        reloaded = knowledge_store.load(committed_bundle.bundle_id)
        if reloaded is None:
            raise RuntimeError("knowledge bundle reload failed")
        out.write(f"  - 持久化并重载成功（bundle_id={reloaded.bundle_id}），"
                  f"审计链校验={knowledge_store.verify_audit_chain()}")
        json_dump(
            {
                "bundle_id": committed_bundle.bundle_id,
                "entry_count": len(committed_bundle.entries),
                "retrospective_sections": len(committed_bundle.retrospective.body_sections),
                "reusable_templates": [
                    {"id": t.template_id, "kind": t.kind.value, "scope": t.scope}
                    for t in committed_bundle.reusable_templates
                ],
                "formally_committed": committed_bundle.formally_committed,
                "committed_by": committed_bundle.committed_by,
            },
            run_dir / "knowledge" / "knowledge-bundle.json",
        )
        audit(ts(21, 23), "u.pm", "knowledge.committed")

        # US-14 AC-3 复用演示：用 PRJ001 知识包的可复用模板为相似项目 PRJ002 生成基线草案
        process_template = next(
            (
                t
                for t in committed_bundle.reusable_templates
                if t.kind.value == "process_template"
            ),
            None,
        )
        task_template = next(
            (
                t
                for t in committed_bundle.reusable_templates
                if t.kind.value == "task_template"
            ),
            None,
        )
        if process_template is None or task_template is None:
            raise RuntimeError("知识包缺少可复用模板")
        prj002_input = {
            "schema_version": "1.0",
            "base_revision": "PRJ002-R0001",
            "project_id": "PRJ002",
            "task_id": "t.1",
            "title": "会议纪要整理小工具开发（复用 PRJ001 任务模板）",
            "objective": "验证 PRJ001 沉淀的可复用流程/任务模板能快速搭建同类小工具项目",
            "plan_start": "2026-09-01T00:00:00Z",
            "plan_end": "2026-09-20T00:00:00Z",
            "responsible_units": ["unit_a", "unit_b"],
            "recipient_cert_id": "CERT-DEV",
            "sender_cert_id": "CERT-OWNER",
            "package_type": "TASK_ASSIGNMENT",
            "payload_digest": "0" * 64,
        }
        prj002_flow = {
            "format": "canonical",
            "flow": {
                "unit_id": "prj002_reused",
                "title": "PRJ002 复用流程（模板来源 PRJ001）",
                "stages": [
                    {
                        "stage_id": stage["stage_id"],
                        "name": f"{stage['name']}（复用）",
                        "nodes": [
                            {
                                "node_id": f"p2.{node['node_id']}",
                                "title": f"{node['title']}（PRJ002）",
                                "stage_hint": node["stage_hint"],
                                "inputs": node["inputs"],
                                "outputs": node["outputs"],
                                "review_criteria": node["review_criteria"],
                                "responsible_roles": node["responsible_roles"],
                            }
                            for node in stage["nodes"]
                        ],
                    }
                    for stage in merged_flow["flow"]["stages"]
                ],
                "roles": merged_flow["flow"]["roles"],
            },
        }
        understanding_p2 = flow_service.understand(prj002_flow)
        proposal_p2 = decomp_service.propose(understanding_p2, prj002_input)
        baseline_p2 = build_baseline(proposal_p2, now="2026-09-01T00:00:00Z")
        out.write(
            f"  - 知识复用（US-14 AC-3）：以模板 {process_template.template_id} / "
            f"{task_template.template_id} 为来源，为同类项目 PRJ002 生成基线草案 "
            f"v{baseline_p2.version}（{len(baseline_p2.work_packages)} 个工作包、"
            f"{sum(len(wp.tasks) for wp in baseline_p2.work_packages)} 个任务，节点 ID 已重编号）"
        )
        json_dump(
            {
                "source_templates": [
                    t.template_id for t in committed_bundle.reusable_templates
                ],
                "process_template_scope": process_template.scope,
                "task_template_scope": task_template.scope,
                "prj002_baseline": _projection_baseline(baseline_p2),
            },
            run_dir / "knowledge" / "reuse-prj002.json",
        )
        audit(ts(21, 24), "u.pm", "knowledge.reused")

        # PRJ002 完整跑通任务下发链（复用 PRJ001 模板 + 同一套服务/人才库）
        prj002_input["flow"] = prj002_flow["flow"]
        event_p2 = OrchestrationEvent(
            "ev.tool.005",
            OrchestrationEventKind.DISPATCH,
            "PRJ002",
            "t.1",
            {
                "schema_version": prj002_input["schema_version"],
                "base_revision": prj002_input["base_revision"],
                "project_input_digest": canonical_digest(prj002_input),
            },
            ts(22, 15),
        )
        workspace_p2 = WorkspaceEntry("PRJ002", "u.pm", "pkg.input", "PRJ002-R0001")
        authorizer_p2 = StaticAuthorizer(
            {"u.pm": frozenset({"orchestrator:confirm-package:PRJ002"})}
        )

        def prj002_chain_run(store: RealChainStore) -> Any:
            held_p2 = with_recovery(
                store,
                lambda: Orchestrator.dispatch_event_with_real_facades(
                    registry,
                    MVP_FIXED_CHAIN,
                    event_p2,
                    workspace=workspace_p2,
                    executor=executor,
                    project_input=prj002_input,
                    store=store,
                    now=ts(22, 15),
                ),
            )
            confirmed_p2 = with_recovery(
                store,
                lambda: Orchestrator.confirm_real_chain(
                    held_p2,
                    preview=held_p2.package_preview,
                    actor=Actor("u.pm"),
                    authorizer=authorizer_p2,
                    store=store,
                    now=ts(22, 16),
                ),
            )
            completed_p2 = with_recovery(
                store,
                lambda: Orchestrator.resume_real_chain(
                    confirmed_p2,
                    registry=registry,
                    chain=MVP_FIXED_CHAIN,
                    event=event_p2,
                    workspace=workspace_p2,
                    executor=executor,
                    store=store,
                    now=ts(22, 17),
                    crypto_provider=provider,
                    sender_handle=provider.sender_handle(DEMO_PROFILE, OWNER_CERT),
                    recipient_handle=provider.recipient_handle(DEMO_PROFILE, MEMBERS["u.dev"][0]),
                ),
            )
            if completed_p2.orch_report.outcome is not OrchestrationOutcome.COMPLETED:
                raise RuntimeError("PRJ002 chain did not complete")
            out.write(
                f"  - PRJ002 复用模板完整跑通任务下发链：outcome="
                f"{completed_p2.orch_report.outcome.value}"
            )
            for line in completed_p2.package_summary:
                out.write(f"    · {line}")
            return completed_p2

        store_p2, completed_p2 = run_chain_guarded(
            _store_factory(run_dir / "knowledge" / "prj002-real-chain.db"),
            prj002_chain_run,
        )
        prj002_content = json.dumps(
            {
                "title": prj002_input["title"],
                "objective": prj002_input["objective"],
                "base_revision": "PRJ002-R0001",
                "origin": "knowledge.reuse.PRJ001",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        prj002_pkg, prj002_wire = build_and_verify_package(
            provider=provider,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.dev"][0],
            package_type="TASK_ASSIGNMENT",
            project_id="PRJ002",
            task_id="t.1",
            base_revision="PRJ002-R0001",
            sequence_no=1,
            manifest={
                "event_id": "ev.tool.005",
                "project_id": "PRJ002",
                "task_id": "t.1",
                "base_revision": "PRJ002-R0001",
                "payload_digest": "0" * 64,
            },
            content=prj002_content,
            signed_at=ts(22, 17),
            expires_at="2027-08-01T00:00:00Z",
        )
        (run_dir / "outbox" / f"TASK_ASSIGNMENT_PRJ002_{prj002_pkg.envelope.package_id}.agent").write_bytes(prj002_wire)
        out.write(
            f"  - PRJ002 专属任务包已导出：TASK_ASSIGNMENT_PRJ002_"
            f"{prj002_pkg.envelope.package_id[:12]}….agent"
        )
        store_p2.close()
        audit(ts(22, 18), "u.pm", "prj002.chain.completed")

        # ------------------------------------------------------------------
        # [16] US-15 安全审计：异常包拦截 + 全程留痕
        # ------------------------------------------------------------------
        step_banner(out, interactive, 16, "US-15 安全审计：异常包拦截、审计流与摘要链校验")
        decisions_out: list[dict[str, Any]] = []
        for label, kwargs in (
            (
                "正常包",
                {
                    "package_id": "pkg.clean",
                    "envelope_status": "ok",
                    "signature_status": "valid",
                    "expiration_ts": "2027-08-01T00:00:00Z",
                    "now": ts(21, 0),
                    "replay_status": "new",
                    "envelope_recipient_cert_id": OWNER_CERT,
                    "expected_recipient_cert_id": OWNER_CERT,
                },
            ),
            (
                "篡改包（签名无效）",
                {
                    "package_id": "pkg.tampered",
                    "envelope_status": "ok",
                    "signature_status": "invalid",
                    "expiration_ts": "2027-08-01T00:00:00Z",
                    "now": ts(21, 0),
                    "replay_status": "new",
                    "envelope_recipient_cert_id": OWNER_CERT,
                    "expected_recipient_cert_id": OWNER_CERT,
                },
            ),
            (
                "过期包",
                {
                    "package_id": "pkg.expired",
                    "envelope_status": "ok",
                    "signature_status": "valid",
                    "expiration_ts": "2026-07-01T00:00:00Z",
                    "now": ts(21, 0),
                    "replay_status": "new",
                    "envelope_recipient_cert_id": OWNER_CERT,
                    "expected_recipient_cert_id": OWNER_CERT,
                },
            ),
            (
                "重放包",
                {
                    "package_id": "pkg.replay",
                    "envelope_status": "ok",
                    "signature_status": "valid",
                    "expiration_ts": "2027-08-01T00:00:00Z",
                    "now": ts(21, 0),
                    "replay_status": "duplicate",
                    "envelope_recipient_cert_id": OWNER_CERT,
                    "expected_recipient_cert_id": OWNER_CERT,
                },
            ),
            (
                "接收人不匹配",
                {
                    "package_id": "pkg.wrong-recipient",
                    "envelope_status": "ok",
                    "signature_status": "valid",
                    "expiration_ts": "2027-08-01T00:00:00Z",
                    "now": ts(21, 0),
                    "replay_status": "new",
                    "envelope_recipient_cert_id": "CERT-EVIL",
                    "expected_recipient_cert_id": OWNER_CERT,
                },
            ),
        ):
            decision = SecurityAuditFacade.evaluate_interception(**kwargs)  # type: ignore[arg-type]
            decisions_out.append(
                {
                    "label": label,
                    "intercepted": decision.intercepted,
                    "reasons": [r.value for r in decision.reasons],
                    "detail": decision.detail,
                }
            )
            out.write(
                f"  - {label}：intercepted={decision.intercepted} "
                f"reasons={[r.value for r in decision.reasons]}"
            )

        # 真实篡改字节演示：修改汇报包任意字节后解析/解密必须失败
        tampered = bytearray(dev_wire)
        tampered[len(tampered) // 2] ^= 0xFF
        try:
            parsed = parse_package_bytes(bytes(tampered))
            open_encrypted_package(
                parsed,
                provider=provider,
                recipient_handle=provider.recipient_handle(DEMO_PROFILE, OWNER_CERT),
                sender_handle=provider.sender_handle(DEMO_PROFILE, MEMBERS["u.dev"][0]),
            )
        except Exception as exc:
            out.write(f"  - 字节篡改演示：修改后的包被拒绝（{type(exc).__name__}）")
        else:
            raise RuntimeError("篡改包未被拒绝")

        # 真实错误接收人演示：发给 u.qa 的任务包，用 u.dev 的接收方句柄打开必须失败
        wrong_recipient_pkg, wrong_recipient_wire = build_and_verify_package(
            provider=provider,
            sender_cert=OWNER_CERT,
            recipient_cert=MEMBERS["u.qa"][0],
            package_type="TASK_ASSIGNMENT",
            project_id=PROJECT_ID,
            task_id=TASK_ID,
            base_revision="PRJ001-R0004",
            sequence_no=6,
            manifest={
                "event_id": "ev.tool.006",
                "project_id": PROJECT_ID,
                "task_id": TASK_ID,
                "base_revision": "PRJ001-R0004",
                "payload_digest": "0" * 64,
            },
            content=b"wrong recipient probe",
            signed_at=ts(22, 16),
            expires_at="2027-08-01T00:00:00Z",
        )
        try:
            open_encrypted_package(
                parse_package_bytes(wrong_recipient_wire),
                provider=provider,
                recipient_handle=provider.recipient_handle(
                    DEMO_PROFILE, MEMBERS["u.dev"][0]
                ),
                sender_handle=provider.sender_handle(DEMO_PROFILE, OWNER_CERT),
            )
        except Exception as exc:
            out.write(
                f"  - 错误接收人演示：发给 u.qa 的包用 u.dev 的接收方句柄打开"
                f" → 被拒绝（{type(exc).__name__}）"
            )
        else:
            raise RuntimeError("错误接收人包未被拒绝")

        json_dump(decisions_out, run_dir / "audit" / "interception-decisions.json")
        audit_events = [
            {
                "ts": event.ts,
                "actor": event.actor,
                "action": event.action,
                "result": event.result.value,
                "project_id": event.project_id,
                "task_id": event.task_id,
                "tool": event.tool,
            }
            for event in pushed
        ]
        # US-15 AC-6：安全管理员按主体/动作/结果查询审计流
        audit_by_actor = SecurityAuditFacade.query_events(
            tuple(pushed),
            AuditQuery(actor="u.auditor", project_id=PROJECT_ID, limit=50),
        )
        audit_replay = SecurityAuditFacade.query_events(
            tuple(pushed),
            AuditQuery(
                action="package.replay.rejected",
                result=AuditEventResult.REJECTED,
                project_id=PROJECT_ID,
                limit=50,
            ),
        )
        out.write(
            f"  - 审计查询（US-15 AC-6）：actor=u.auditor → {len(audit_by_actor.events)} 条；"
            f"action=package.replay.rejected → {len(audit_replay.events)} 条"
        )
        json_dump(
            {
                "by_actor_u_auditor": len(audit_by_actor.events),
                "replay_rejected": len(audit_replay.events),
            },
            run_dir / "audit" / "audit-query.json",
        )
        out.write(f"  - 编排审计摘要链校验：{real_chain_store.verify_audit_chain()}")
        out.write(f"  - 知识库审计摘要链校验：{knowledge_store.verify_audit_chain()}")
        out.write(
            f"  - 合并回执历史校验："
            f"{len(receipt_repository.verified_history(trusted_time=_dt.datetime(2026, 8, 23, tzinfo=_dt.timezone.utc)))} 条"
        )
        # 审计检查点包（AUDIT_CHECKPOINT）：安全管理员导出审计摘要与签名检查点
        receipt_count = len(
            receipt_repository.verified_history(
                trusted_time=_dt.datetime(2026, 8, 23, tzinfo=_dt.timezone.utc)
            )
        )
        checkpoint_content = json.dumps(
            {
                "audit_event_count": len(audit_events),
                "chain_verified": real_chain_store.verify_audit_chain(),
                "knowledge_chain_verified": knowledge_store.verify_audit_chain(),
                "receipt_count": receipt_count,
                "checkpoint_note": "PRJ001 全程审计检查点（示例导出）",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        checkpoint_pkg, checkpoint_wire = build_and_verify_package(
            provider=provider,
            sender_cert=AUDITOR_CERT,
            recipient_cert=OWNER_CERT,
            package_type="AUDIT_CHECKPOINT",
            project_id=PROJECT_ID,
            task_id=TASK_ID,
            base_revision="PRJ001-R0006",
            sequence_no=1,
            manifest={
                "event_id": "ev.tool.audit.001",
                "project_id": PROJECT_ID,
                "task_id": TASK_ID,
                "base_revision": "PRJ001-R0006",
                "payload_digest": "0" * 64,
            },
            content=checkpoint_content,
            signed_at=ts(22, 22),
            expires_at="2027-08-01T00:00:00Z",
        )
        (run_dir / "outbox" / f"AUDIT_CHECKPOINT_{PROJECT_ID}_{checkpoint_pkg.envelope.package_id}.agent").write_bytes(checkpoint_wire)
        out.write(
            f"  - 审计检查点包已导出（AUDIT_CHECKPOINT，安全管理员 → 负责人，"
            f"{len(audit_events)} 条审计、{receipt_count} 份回执）："
            f"{checkpoint_pkg.envelope.package_id[:12]}…"
        )
        audit(ts(22, 22), "u.auditor", "audit.checkpoint.exported")
        # 审计流完整落盘（含检查点导出事件）
        audit_events = [
            {
                "ts": event.ts,
                "actor": event.actor,
                "action": event.action,
                "result": event.result.value,
                "project_id": event.project_id,
                "task_id": event.task_id,
                "tool": event.tool,
            }
            for event in pushed
        ]
        (run_dir / "audit" / "audit-events.jsonl").write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in audit_events),
            encoding="utf-8",
        )
        out.write(f"  - 审计流共 {len(audit_events)} 条事件，已导出 JSONL")

        # ------------------------------------------------------------------
        # [17] 汇总
        # ------------------------------------------------------------------
        step_banner(out, interactive, 17, "汇总：演示报告与产物")
        summary.update(
            {
                "project": PROJECT_ID,
                "title": project_input["title"],
                "project_status": "closed",
                "acceptance_conclusion": "验收评审合并通过（R0006），项目具备交付条件",
                "flows": {"unit_a": confirmed_a.version, "unit_b": confirmed_b.version},
                "baseline_final": current_baseline.version,
                "master_revision_final": f"PRJ001-R{current_baseline.version:04d}",
                "task_packages": {m: p[0].envelope.package_id for m, p in task_packages.items()},
                "reports": {
                    "u.dev": dev_manifest.package_id,
                    "u.qa_final": qa_final_manifest.package_id,
                    "u.qa_cycle2": qa2_manifest.package_id,
                    "u.doc": doc_manifest.package_id,
                    "u.review": review_manifest.package_id,
                },
                "merge_receipts": [
                    outcome_dev.commit.receipt.receipt_id,
                    outcome_qa.commit.receipt.receipt_id,
                    outcome_c2.commit.receipt.receipt_id,
                    outcome_doc.commit.receipt.receipt_id,
                    outcome_review.commit.receipt.receipt_id,
                ],
                "risk_report": final_risk.merge_reporter_package_id,
                "coordination_meeting_recommended": final_risk.coordination_meeting_recommended,
                "supervision_items": [i.item_id for i in supervision.items],
                "decision_brief": brief.brief_id,
                "risk_topic_brief": topic_brief.brief_id,
                "periodic_brief": periodic_brief.brief_id,
                "knowledge_bundle": committed_bundle.bundle_id,
                "audit_event_count": audit_hub.event_count,
                "cockpit_api_probes": len(cockpit_api_results),
                "replay_rejected": replay_again.outcome.value,
                "interception_decisions": len(decisions_out),
                "identity_registrations": len(registrations),
                "wps_launch_decisions": len(wps_decisions),
                "cockpit_frontend_offline": True,
                "cockpit_restart_persisted": True,
                "wrong_recipient_rejected": True,
                "audit_query_actor_events": len(audit_by_actor.events),
                "reuse_project": {
                    "project_id": "PRJ002",
                    "baseline_version": baseline_p2.version,
                    "template_count": len(committed_bundle.reusable_templates),
                    "chain_outcome": completed_p2.orch_report.outcome.value,
                    "task_package": prj002_pkg.envelope.package_id,
                },
                "cycle2": {
                    "new_task": "n.test_exec（回归复核整改）",
                    "master_after_merge": f"PRJ001-R{current_baseline.version:04d}",
                    "merge_receipt": outcome_c2.commit.receipt.receipt_id,
                },
            }
        )
        # 终态驾驶舱视图：第二轮合并后项目进入完成态（--serve 模式展示终态）
        final_ws_view = WorkspaceView(
            PROJECT_ID,
            project_input["title"],
            tuple(MEMBERS.keys()),
            8,
            5,
            4,
        )
        final_role_views = []
        for member_id, (_cert_id, role_name, _org) in MEMBERS.items():
            evidence_dir = (
                run_dir / "workspaces" / PROJECT_ID / member_id / "evidence"
            )
            artifacts = []
            for evidence in sorted(evidence_dir.glob("*.md")):
                artifacts.append(ArtifactSummary(
                    f"evidence/{evidence.name}",
                    "document",
                    "text/markdown",
                    evidence.stat().st_size,
                    "0" * 64,
                ))
            completed = member_id in ("u.dev", "u.qa")
            final_role_views.append(RoleView(
                member_id,
                PROJECT_ID,
                role_name,
                (TaskSummary(
                    "t.1",
                    project_input["title"],
                    "completed" if completed else "in_progress",
                    project_input["plan_end"],
                    member_id,
                ),),
                (MilestoneSummary(
                    "m.1", "工具可用版本", project_input["plan_end"], completed
                ),),
                tuple(artifacts),
            ))
        # 多项目视图：PRJ002（复用模板项目）一并纳入终态驾驶舱
        prj002_ws_view = WorkspaceView(
            "PRJ002",
            prj002_input["title"],
            ("u.dev",),
            7,
            5,
            0,
        )
        final_workspace_views = (final_ws_view, prj002_ws_view)
        final_role_views.append(RoleView(
            "u.dev",
            "PRJ002",
            "研发工程师（复用项目）",
            (TaskSummary(
                "t.1",
                prj002_input["title"],
                "in_progress",
                prj002_input["plan_end"],
                "u.dev",
            ),),
            (MilestoneSummary(
                "m.1", "PRJ002 工具可用版本", prj002_input["plan_end"], False
            ),),
            (),
        ))
        json_dump(
            {
                "workspaces": [
                    dataclasses.asdict(view) for view in final_workspace_views
                ],
                "roles": [
                    dataclasses.asdict(view) for view in final_role_views
                ],
            },
            run_dir / "cockpit" / "final-views.json",
        )
        out.write(
            f"  - 终态驾驶舱视图：{len(final_workspace_views)} 个项目"
            "（PRJ001 结项态 + PRJ002 复用态）、"
            f"{len(final_role_views)} 个角色视图"
        )
        json_dump(
            {
                "merges": [
                    {
                        "reporter": "u.dev",
                        "task": "n.impl_core",
                        "accepted": True,
                        "merged_version": outcome_dev.commit.proposal.record.merged_version,
                        "receipt_id": outcome_dev.commit.receipt.receipt_id,
                    },
                    {
                        "reporter": "u.qa",
                        "task": "n.test_exec（旧基线）",
                        "accepted": False,
                        "has_conflict": True,
                        "reason": outcome_conflict.commit.proposal.rejection_reason,
                    },
                    {
                        "reporter": "u.qa",
                        "task": "n.test_exec",
                        "accepted": True,
                        "merged_version": outcome_qa.commit.proposal.record.merged_version,
                        "receipt_id": outcome_qa.commit.receipt.receipt_id,
                    },
                    {
                        "reporter": "u.qa",
                        "task": "n.test_exec（整改）",
                        "accepted": True,
                        "merged_version": outcome_c2.commit.proposal.record.merged_version,
                        "receipt_id": outcome_c2.commit.receipt.receipt_id,
                    },
                    {
                        "reporter": "u.doc",
                        "task": "n.docs_guide",
                        "accepted": True,
                        "merged_version": outcome_doc.commit.proposal.record.merged_version,
                        "receipt_id": outcome_doc.commit.receipt.receipt_id,
                    },
                    {
                        "reporter": "u.review",
                        "task": "n.acceptance",
                        "accepted": True,
                        "merged_version": outcome_review.commit.proposal.record.merged_version,
                        "receipt_id": outcome_review.commit.receipt.receipt_id,
                    },
                ]
            },
            run_dir / "merge" / "merge-records-final.json",
        )
        report_path = _render_html_report(run_dir, summary)
        summary["demo_report"] = str(report_path)
        summary["decision_brief_docx"] = "brief/决策简报-阶段.docx"
        json_dump(summary, run_dir / "summary.json")
        if args.open:
            try:
                os.startfile(report_path)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - 非 Windows 或无默认浏览器
                out.write(f"  - 自动打开演示报告失败：{exc}")
            else:
                out.write("  - 已在默认浏览器打开演示报告")
        out.write(f"  - 运行目录：{run_dir}")
        out.write(f"  - 演示报告：demo-report.html（浏览器直接打开，离线自包含）")
        out.write(
            f"  - 第二轮循环：会议结论转任务 → 下发 → 回传合并 → 主版本 "
            f"PRJ001-R{current_baseline.version:04d}"
        )
        out.write(
            f"  - 知识复用：PRJ002 复用 PRJ001 模板并完整跑通任务下发链（任务包 "
            f"{prj002_pkg.envelope.package_id[:12]}…）"
        )
        out.write("  - 关键产物：summary.json、outbox/*.agent、merge/merge-records.json、")
        out.write("    risk/risk-report.json、supervision/supervision-outcome.json、")
        out.write("    brief/decision-brief.json、knowledge/knowledge-bundle.json、")
        out.write("    audit/audit-events.jsonl")
        out.write("\n示例运行成功：US-0 ~ US-15 全流程闭环，所有不变量校验通过。")
        if args.serve:
            out.write("\n保持本地驾驶舱服务运行（浏览器访问下方地址，Ctrl+C 退出）…")
            serve_server = CockpitHttpServer(
                CockpitHttpConfig(
                    bind_port=args.port,
                    request_timeout_sec=5,
                    state_path=run_dir / "cockpit" / "cockpit-state.json",
                    lock_path=run_dir / "cockpit" / "cockpit-serve.lock",
                ),
                workspace_views=final_workspace_views,
                role_views=tuple(final_role_views),
            )
            serve_server.start()
            try:
                while True:
                    time.sleep(3600)
            except KeyboardInterrupt:
                pass
            finally:
                serve_server.stop()
            out.write("  驾驶舱服务已停止。")
        return 0
    finally:
        if knowledge_store is not None:
            knowledge_store.close()
        if receipt_repository is not None:
            receipt_repository.close()
        if real_chain_store is not None:
            real_chain_store.close()
        out.close()


if __name__ == "__main__":
    raise SystemExit(main())
