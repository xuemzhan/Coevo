"""一致性 API 演示（最小闭环）：通过统一服务框架驱动 MVP 全流程。

以统一信封逐个调用 16 个服务，走通：身份 → 流程理解 → 任务分解 →
人才推荐 → 运行中枢编排（下发链，含人工确认）→ 加密任务包 → 工作区初始化 →
进展采集 → 成果回传 → 状态合并（含风险预检）→ 督办会议 → 阶段简报 →
知识沉淀 → 安全审计查询；并演示一致性错误路径与 OpenAPI 契约。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import urllib.error
import urllib.request
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

from service_api.demo_common import run_demo_server  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo 一致性 API 演示")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent / "output"),
        help="运行产物父目录（默认 examples/service-api/output）",
    )
    parser.add_argument("--port", type=int, default=0, help="HTTP 端口（默认自动）")
    args = parser.parse_args(argv)

    run_dir = Path(args.output_dir) / f"run-{_dt.datetime.now():%Y%m%d-%H%M%S}"
    run_dir.mkdir(parents=True, exist_ok=True)

    def sequence(server, ctx) -> int:
        token = server.token

        def call(
            service: str,
            method: str,
            params: dict,
            *,
            actor: str = "u.pm",
            index: int = 0,
        ) -> tuple[int, dict]:
            payload = {
                "params": params,
                "actor": actor,
                "request_id": f"svc.{index}.{service}.{method}",
                "ts": "2026-08-01T00:00:00Z",
            }
            request = urllib.request.Request(
                server.url + f"api/v1/{service}/{method}",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "X-Service-Token": token,
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as resp:
                    return resp.status, json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                return exc.code, json.loads(exc.read().decode("utf-8"))

        def show(index: int, label: str, status: int, envelope: dict) -> None:
            ok = envelope.get("ok")
            code = envelope.get("code")
            message = envelope.get("message", "")
            data = envelope.get("data", {})
            print(f"[{index:02d}] {label}: HTTP {status} ok={ok} code={code}")
            if data:
                print(f"      data={json.dumps(data, ensure_ascii=False)[:180]}")
            if message:
                print(f"      message={message[:120]}")
        unit_a_raw = json.loads(
            (SCENARIO / "flows" / "unit-a-flow.json").read_text(encoding="utf-8")
        )
        project_input = json.loads(
            (SCENARIO / "project-input.json").read_text(encoding="utf-8")
        )
        window = {
            "start": project_input["plan_start"],
            "end": project_input["plan_end"],
        }

        sequence: list[tuple[str, str, dict, str]] = [
            ("identity", "describe", {}, "身份与信任：角色/证书/授权"),
            ("flow", "understand", {"raw": unit_a_raw}, "流程理解：unit_a 解析与映射"),
            (
                "decomposition",
                "propose",
                {"project_input": project_input, "flow": unit_a_raw},
                "任务分解：结构化基线",
            ),
            (
                "talent",
                "recommend",
                {
                    "requirements": [
                        {
                            "task_type": "task.n.impl_core",
                            "required_skill_tags": ["tech:python"],
                            "window": window,
                        },
                        {
                            "task_type": "task.n.test_exec",
                            "required_skill_tags": ["tech:testing"],
                            "window": window,
                        },
                    ]
                },
                "团队组建：脱敏人才推荐",
            ),
            (
                "orchestration",
                "dispatch",
                {
                    "event_id": "ev.svc.001",
                    "project_input": {
                        **project_input,
                        "flow": unit_a_raw["flow"],
                    },
                },
                "运行中枢：编排链第 1-3 步（待人工确认）",
            ),
            (
                "orchestration",
                "confirm",
                {"event_id": "ev.svc.001", "actor": "u.pm"},
                "运行中枢：负责人授权确认",
            ),
            (
                "orchestration",
                "resume",
                {"event_id": "ev.svc.001", "recipient_cert_id": "CERT-DEV"},
                "运行中枢：生成加密任务包",
            ),
        ]
        package_data: dict = {}
        for index, (service, method, params, label) in enumerate(sequence, start=1):
            status, envelope = call(service, method, params, index=index)
            show(index, label, status, envelope)
            if not envelope.get("ok"):
                    return 1
        steps = [
            (
                "package",
                "build",
                {
                    "sender_cert_id": "CERT-OWNER",
                    "recipient_cert_id": "CERT-DEV",
                    "project_id": "PRJ001",
                    "package_type": "TASK_ASSIGNMENT",
                    "sequence_no": 1,
                    "manifest": {
                        "event_id": "ev.svc.002",
                        "project_id": "PRJ001",
                        "task_id": "t.1",
                        "base_revision": "PRJ001-R0001",
                        "payload_digest": "0" * 64,
                    },
                    "content": {
                        "title": "内部工时统计小工具开发",
                        "role": "研发工程师",
                    },
                },
                "加密任务包生成并回读校验",
            ),
            (
                "workspace",
                "init",
                {
                    "package_base64": "",
                    "role_id": "u.dev",
                    "base_revision": "PRJ001-R0001",
                },
                "工作区初始化（验签导入）",
            ),
            (
                "progress",
                "extract",
                {
                    "project_id": "PRJ001",
                    "role_id": "u.dev",
                    "revision": "PRJ001-R0001",
                    "evidence": [
                        {
                            "task_id": "n.impl_core",
                            "kind": "document_content",
                            "source_ref": "evidence/开发进展说明.md",
                            "text": "核心统计功能已完成并通过样例数据自测",
                            "confidence": 0.9,
                            "evidence_refs": [
                                {
                                    "path": "evidence/开发进展说明.md",
                                    "role": "document",
                                    "media_type": "text/markdown",
                                    "digest_hex": "0" * 64,
                                    "size_bytes": 1,
                                }
                            ],
                        }
                    ],
                },
                "进展采集：成果证据识别（PROPOSED）",
            ),
        ]
        for index, (service, method, params, label) in enumerate(steps, start=9):
            if service == "workspace":
                params["package_base64"] = package_data.get("wire_base64", "")
            status, envelope = call(service, method, params, index=index)
            show(index, label, status, envelope)
            if not envelope.get("ok"):
                    return 1
            if service == "package":
                package_data = envelope["data"]

        tail_steps = [
            (
                "report",
                "build",
                {
                    "manifest": {
                        "project_id": "PRJ001",
                        "task_id": "n.impl_core",
                        "base_revision": "PRJ001-R0001",
                        "sequence_no": 1,
                        "status": "completed",
                        "sender_cert_id": "CERT-DEV",
                        "recipient_cert_id": "CERT-OWNER",
                        "sender_user_id": "U-DEV",
                        "progress_summary": "开发任务完成并通过自测",
                        "completed_work": ["核心统计功能实现", "报表导出功能实现"],
                    }
                },
                "成果回传包生成",
            ),
            ("merge", "analyze", {}, "状态合并与风险预检（签名回执）"),
            ("risk", "analyze", {}, "风险预警明细"),
            ("supervision", "coordinate", {}, "督办事项与会议提案"),
            ("brief", "generate", {"brief_type": "stage"}, "阶段决策简报"),
            (
                "knowledge",
                "aggregate",
                {
                    "project_id": "PRJ001",
                    "merge_records": [
                        {
                            "id": "m.svc.1",
                            "title": "开发完成合并",
                            "summary": "主版本 R0002",
                        }
                    ],
                    "model_summaries": [
                        {
                            "id": "ms.svc.1",
                            "title": "服务框架总结",
                            "summary": "一致性 API 统筹全部 MVP 模块",
                        }
                    ],
                },
                "知识沉淀（审批入库）",
            ),
            ("audit", "query", {"actor": "u.pm"}, "安全审计查询"),
        ]
        for index, (service, method, params, label) in enumerate(
            tail_steps, start=13
        ):
            status, envelope = call(service, method, params, index=index)
            show(index, label, status, envelope)
            if not envelope.get("ok"):
                    return 1
        # 一致性错误路径演示
        status, envelope = call("unknown", "ping", {}, index=99)
        show(20, "未知服务 → 统一 not_found 信封", status, envelope)
        if envelope.get("ok") or envelope.get("code") != "not_found":
                    return 1
        status, envelope = call(
            "identity",
            "register",
            {
                "actor_id": "u.pm",
                "display_name": "王负责人",
                "organization": "任务牵头单位",
                "role_code": "project_owner",
                "cert_id": "CERT-OWNER",
            },
            actor="u.auditor",
            index=21,
        )
        show(21, "身份注册（u.pm，同证书基线）", status, envelope)
        if not envelope.get("ok"):
                    return 1
        status, envelope = call(
            "identity",
            "register",
            {
                "actor_id": "u.dev",
                "display_name": "李研发",
                "organization": "研发组",
                "role_code": "project_member",
                "cert_id": "CERT-DEV",
            },
            actor="u.auditor",
            index=22,
        )
        show(22, "证书指纹复用 → 统一 conflict 信封", status, envelope)
        if envelope.get("ok") or envelope.get("code") != "conflict":
                    return 1
        status, envelope = call(
            "orchestration",
            "dispatch",
            {"event_id": "ev.svc.unauthorized"},
            actor="u.auditor",
            index=23,
        )
        show(23, "越权调用 → 统一 unauthorized 信封", status, envelope)
        if envelope.get("ok") or envelope.get("code") != "unauthorized":
                    return 1
        status, envelope = call(
            "orchestration",
            "fail_demo",
            {"project_input": {**project_input, "flow": unit_a_raw["flow"]}},
            index=24,
        )
        show(24, "编排失败升级（智能体 BUSY）→ escalated 信封", status, envelope)
        if (
            not envelope.get("ok")
            or envelope["data"].get("outcome") != "escalated"
        ):
                    return 1
        request = urllib.request.Request(
            server.url + "api/v1/services",
            headers={"X-Service-Token": token},
        )
        with urllib.request.urlopen(request, timeout=10) as resp:
            catalog = json.loads(resp.read().decode("utf-8"))
        openapi_request = urllib.request.Request(
            server.url + "api/v1/openapi.json",
            headers={"X-Service-Token": token},
        )
        with urllib.request.urlopen(openapi_request, timeout=10) as resp:
            openapi = json.loads(resp.read().decode("utf-8"))
        print(f"[25] 能力目录：{len(catalog['services'])} 个服务")
        print(
            f"[26] OpenAPI 契约：{len(openapi['paths'])} 个路径，"
            f"openapi={openapi['openapi']}"
        )
        print(f"[27] 审计事件总数：{len(ctx['audit_events'])} 条")
        print(f"\n一致性 API 演示完成：{server.url}  token={token[:8]}…")
        print("示例产物目录：" + str(run_dir))
        return 0

    return run_demo_server(
        run_dir,
        sequence=sequence,
        permissions={
            "u.pm": frozenset({"*"}),
            "u.auditor": frozenset({
                "identity.register",
                "audit.query",
                "audit.intercept",
            }),
        },
        tool="coevo.service-api",
        port=args.port,
    )


if __name__ == "__main__":
    raise SystemExit(main())
