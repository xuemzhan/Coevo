"""一致性 API 完整业务闭环演示：只通过统一服务框架跑通多角色项目。

与 run_demo.py 的区别
--------------------
* run_demo.py 走“单角色最小闭环”（24 步）；
* 本脚本用 Python 客户端（ServiceClient）走“完整业务闭环”：
  双单位合并流程 → 编排下发 → 四类角色（研发/测试/文档/评审）连续
  成果回传与签名合并（R0001 → R0005）→ 风险预警 → 督办会议 →
  三类决策简报（阶段/风险专题/周期）→ 知识沉淀 → 安全审计查询。
全程只通过一致性 API 调用，证明“服务框架统筹所有模块”可承载
与 tool-dev-project 等价的业务闭环。

用法：python examples\\service-api\\run_demo_full.py
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SCENARIO = ROOT / "examples" / "tool-dev-project" / "scenario"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
except Exception:  # pragma: no cover
    pass

from service_api.client import ServiceApiError, ServiceClient  # noqa: E402
from service_api.demo_common import run_demo_server  # noqa: E402


def build_merged_flow() -> dict:
    """双单位合并流程（与 tool-dev-project 同构：7 个任务）。"""
    unit_a = json.loads(
        (SCENARIO / "flows" / "unit-a-flow.json").read_text(encoding="utf-8")
    )
    unit_b = json.loads(
        (SCENARIO / "flows" / "unit-b-flow.json").read_text(encoding="utf-8")
    )

    def b_nodes():
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
            for row in unit_b["rows"]
        ]

    return {
        "format": "canonical",
        "flow": {
            "unit_id": "prj001_combined",
            "title": "PRJ001 跨单位任务流程（unit_a 研发 + unit_b 测试交付）",
            "stages": [
                {
                    "stage_id": "planning_stage",
                    "name": "需求与方案",
                    "nodes": [unit_a["flow"]["stages"][0]["nodes"][0]],
                },
                {
                    "stage_id": "design_review_stage",
                    "name": "测试设计与评审",
                    "nodes": [b_nodes()[0]],
                },
                {
                    "stage_id": "execution_stage",
                    "name": "开发与测试执行",
                    "nodes": [
                        unit_a["flow"]["stages"][1]["nodes"][0],
                        unit_a["flow"]["stages"][1]["nodes"][1],
                        b_nodes()[1],
                    ],
                },
                {
                    "stage_id": "closure_stage",
                    "name": "文档收尾",
                    "nodes": [unit_a["flow"]["stages"][2]["nodes"][0]],
                },
                {
                    "stage_id": "delivery_stage",
                    "name": "验收交付",
                    "nodes": [b_nodes()[2]],
                },
            ],
            "roles": list(unit_a["flow"]["roles"]) + list(unit_b["roles"]),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="一致性 API 完整业务闭环演示")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "output"),
    )
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args(argv)

    run_dir = Path(args.output_dir) / f"run-full-{_dt.datetime.now():%Y%m%d-%H%M%S}"
    run_dir.mkdir(parents=True, exist_ok=True)

    def sequence(server, ctx) -> int:
        client = ServiceClient(server.url, server.token)
        try:
            def call(service: str, method: str, params: dict | None = None) -> dict:
                """一致性 API 调用（默认负责人主体）。"""
                return client.call(service, method, params, actor="u.pm")

            project_input = json.loads(
                (SCENARIO / "project-input.json").read_text(encoding="utf-8")
            )
            merged_flow = build_merged_flow()
            print(f"[01] 身份与信任：{len(call('identity', 'describe')['actors'])} 个角色")

            baseline = call(
                "decomposition",
                "propose",
                {"project_input": project_input, "flow": merged_flow},
            )
            print(
                f"[02] 任务分解：基线 v{baseline['version']}，"
                f"{len(baseline['work_packages'])} 个工作包"
            )

            print("[03] 运行中枢：编排链下发（含人工确认）…")
            call(
                "orchestration",
                "dispatch",
                {
                    "event_id": "ev.full.001",
                    "project_input": {
                        **project_input,
                        "flow": merged_flow["flow"],
                    },
                },
            )
            call(
                "orchestration",
                "confirm",
                {"event_id": "ev.full.001", "actor": "u.pm"},
            )
            resume = call(
                "orchestration",
                "resume",
                {"event_id": "ev.full.001", "recipient_cert_id": "CERT-DEV"},
            )
            print(f"       outcome={resume['outcome']}（加密任务包已生成）")

            roles = [
                ("研发", "u.dev", "CERT-DEV", "n.impl_core",
                 ["核心统计功能实现", "报表导出功能实现"]),
                ("测试", "u.qa", "CERT-QA", "n.test_exec",
                 ["功能测试执行", "回归测试执行"]),
                ("文档", "u.doc", "CERT-DOC", "n.docs_guide",
                 ["用户手册初稿", "交付说明"]),
                ("评审", "u.review", "CERT-REV", "n.acceptance",
                 ["验收评审完成", "验收结论签署"]),
            ]
            current_revision = "PRJ001-R0001"
            merge_records = []
            risk_summaries = []
            for index, (label, role, cert, task, completed) in enumerate(roles, start=4):
                report = call(
                    "report",
                    "build",
                    {
                        "manifest": {
                            "project_id": "PRJ001",
                            "task_id": task,
                            "base_revision": current_revision,
                            "sequence_no": index - 3,
                            "status": "completed",
                            "sender_cert_id": cert,
                            "recipient_cert_id": "CERT-OWNER",
                            "sender_user_id": role.upper().replace(".", "-"),
                            "progress_summary": f"{label}任务完成",
                            "completed_work": completed,
                        }
                    },
                )
                merged = call("merge", "analyze", {})
                current_revision = merged["merged_version"]
                merge_records.append({
                    "id": f"m.full.{index}",
                    "title": f"{label}成果合并",
                    "summary": f"合并至 {current_revision}",
                })
                risk_summaries.append(
                    {"kinds": merged["risk_kinds"], "version": current_revision}
                )
                print(
                    f"[{index:02d}] {label}成果回传合并：{current_revision}，"
                    f"回执 {merged['receipt_id'][:16]}…，"
                    f"风险 {merged['risk_kinds']}"
                )

            risk = call("risk", "analyze", {})
            print(
                f"[08] 风险预警：{len(risk['risks'])} 项，"
                f"会议建议={risk['coordination_meeting_recommended']}"
            )
            supervision = call("supervision", "coordinate", {})
            print(
                f"[09] 督办会议：{len(supervision['supervision_items'])} 项督办，"
                f"会议提案={supervision['meeting_proposal_id'] is not None}"
            )
            notice = call(
                "package",
                "build",
                {
                    "sender_cert_id": "CERT-OWNER",
                    "recipient_cert_id": "CERT-QA",
                    "project_id": "PRJ001",
                    "package_type": "SUPERVISION_NOTICE",
                    "sequence_no": 1,
                    "manifest": {
                        "event_id": "ev.full.notice",
                        "project_id": "PRJ001",
                        "task_id": "n.test_exec",
                        "base_revision": current_revision,
                        "payload_digest": "0" * 64,
                    },
                    "content": {
                        "title": "测试整改督办",
                        "responsible_subject": "u.qa",
                        "items": supervision["supervision_items"],
                    },
                },
            )
            print(
                f"[10] 督办包下发（SUPERVISION_NOTICE → u.qa）："
                f"{notice['package_id'][:12]}…"
            )

            stage = call("brief", "generate", {"brief_type": "stage"})
            print(f"[11] 阶段简报：{stage['brief_id']}")
            risk_topic = call(
                "brief",
                "generate",
                {
                    "brief_type": "risk_topic",
                    "topic_risk_ids": [risk["risks"][0]["risk_id"]],
                },
            )
            print(f"[12] 风险专题简报：{risk_topic['brief_id']}")
            periodic = call(
                "brief",
                "generate",
                {
                    "brief_type": "periodic",
                    "period_start": "2026-08-01T00:00:00Z",
                    "period_end": "2026-08-31T00:00:00Z",
                },
            )
            print(f"[13] 周期简报：{periodic['brief_id']}")

            knowledge = call(
                "knowledge",
                "aggregate",
                {
                    "project_id": "PRJ001",
                    "merge_records": merge_records,
                    "risk_reports": [
                        {
                            "id": f"risk.full.{i}",
                            "title": f"合并风险 {item['version']}",
                            "summary": f"风险类型 {item['kinds']}",
                        }
                        for i, item in enumerate(risk_summaries)
                    ],
                    "decision_briefs": [
                        {"id": stage["brief_id"], "title": "阶段简报", "summary": ""},
                        {"id": risk_topic["brief_id"], "title": "风险专题", "summary": ""},
                        {"id": periodic["brief_id"], "title": "周期简报", "summary": ""},
                    ],
                    "model_summaries": [
                        {
                            "id": "ms.full.1",
                            "title": "一致性 API 闭环总结",
                            "summary": "完整业务闭环仅通过统一服务框架 API 完成",
                        }
                    ],
                },
            )
            print(
                f"[14] 知识沉淀：{knowledge['bundle_id']}，"
                f"{knowledge['entry_count']} 条知识，"
                f"正式入库={knowledge['formally_committed']}"
            )
            audit = call("audit", "query", {"actor": "u.pm"})
            print(
                f"[15] 审计查询：{len(audit['events'])} 条（scan={audit['total_scanned']}）"
            )
            checkpoint = call("audit", "checkpoint", {})
            print(
                f"[16] 审计检查点包（AUDIT_CHECKPOINT → 负责人）："
                f"{checkpoint['package_id'][:12]}…"
            )
            exported = call("audit", "export", {"format": "jsonl"})
            print(
                f"[17] 审计导出：{exported['event_count']} 条，"
                f"digest={exported['digest_hex'][:12]}…"
            )

            print(
                f"\n一致性 API 完整闭环演示完成：主版本连续至 {current_revision}，"
                f"审计事件 {len(ctx['audit_events'])} 条"
            )
            print("示例产物目录：" + str(run_dir))
            return 0
        except ServiceApiError as exc:
            print(f"服务调用失败：code={exc.code} status={exc.status} message={exc}")
            return 1

    return run_demo_server(
        run_dir,
        sequence=sequence,
        permissions={
            "u.pm": frozenset({"*"}),
            "u.auditor": frozenset({"audit.query", "audit.intercept"}),
        },
        tool="coevo.service-api.full",
        port=args.port,
    )


if __name__ == "__main__":
    raise SystemExit(main())
