"""Coevo 示例产物独立核验脚本（只读，不修改任何文件）。

对一次完整运行的 output/run-<时间戳>-demo/ 目录做独立断言：
产物存在性、`.agent` 包可解析、包类型覆盖、合并记录、简报、知识包、
审计事件数一致性、驾驶舱巡检与演示报告等。

用法：
    python examples\\tool-dev-project\\scripts\\verify_output.py
    python examples\\tool-dev-project\\scripts\\verify_output.py --run-dir <运行目录>

默认核验最新一次含 summary.json 的完整运行目录；任一检查失败返回非零退出码。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXAMPLES = ROOT / "examples" / "tool-dev-project"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
except Exception:  # pragma: no cover - 非控制台环境
    pass

EXPECTED_PACKAGE_TYPES = frozenset({
    "TASK_ASSIGNMENT",
    "TASK_CHANGE",
    "MEETING_DECISION",
    "SUPERVISION_NOTICE",
    "AUDIT_CHECKPOINT",
    "RESULT_SUBMISSION",
})


def _latest_run(output_dir: Path) -> Path:
    candidates = [
        path for path in output_dir.glob("run-*")
        if (path / "summary.json").is_file()
    ]
    if not candidates:
        raise SystemExit(f"未找到含 summary.json 的完整运行目录：{output_dir}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo 示例产物独立核验")
    parser.add_argument("--run-dir", default=None, help="运行产物目录（默认最新完整运行）")
    args = parser.parse_args(argv)

    output_dir = EXAMPLES / "output"
    run_dir = Path(args.run_dir) if args.run_dir else _latest_run(output_dir)
    if not run_dir.is_dir():
        raise SystemExit(f"运行目录不存在：{run_dir}")

    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    summary_path = run_dir / "summary.json"
    if not summary_path.is_file():
        raise SystemExit(f"缺少 summary.json：{summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    check(
        "summary.json 关键字段",
        all(
            key in summary
            for key in (
                "project",
                "title",
                "master_revision_final",
                "merge_receipts",
                "audit_event_count",
                "knowledge_bundle",
            )
        ),
    )
    check(
        "主版本终态",
        summary.get("master_revision_final") in {"PRJ001-R0004", "PRJ001-R0006"},
        str(summary.get("master_revision_final")),
    )
    check(
        "合并回执数量",
        len(summary.get("merge_receipts", [])) >= 3,
        str(len(summary.get("merge_receipts", []))),
    )
    reports = summary.get("reports", {})
    check(
        "全员回传（文档/评审）",
        "u.doc" in reports and "u.review" in reports,
        str(sorted(reports)),
    )
    check(
        "三类简报 ID",
        all(
            key in summary
            for key in ("decision_brief", "risk_topic_brief", "periodic_brief")
        ),
    )
    check(
        "知识复用 PRJ002 链",
        summary.get("reuse_project", {}).get("chain_outcome") == "completed",
    )

    # .agent 任务包可解析 + 类型覆盖
    from src.coevo.protocol import parse_package_bytes

    agent_files = sorted((run_dir / "outbox").glob("*.agent"))
    check("outbox 任务包存在", len(agent_files) >= 12, str(len(agent_files)))
    report_files = sorted((run_dir / "reports").glob("RESULT_SUBMISSION_*.agent"))
    check("成果包数量", len(report_files) >= 4, str(len(report_files)))
    parsed_types: set[str] = set()
    for wire_file in agent_files + report_files:
        try:
            parsed = parse_package_bytes(wire_file.read_bytes())
            parsed_types.add(parsed.envelope.package_type)
        except Exception as exc:
            check(f"包可解析：{wire_file.name}", False, str(exc)[:120])
    check(
        "包类型覆盖",
        EXPECTED_PACKAGE_TYPES.issubset(parsed_types),
        str(sorted(parsed_types)),
    )

    check("merge-records-final.json", (run_dir / "merge" / "merge-records-final.json").is_file())
    check("risk/risk-report.json", (run_dir / "risk" / "risk-report.json").is_file())
    check(
        "supervision/supervision-outcome.json",
        (run_dir / "supervision" / "supervision-outcome.json").is_file(),
    )
    for name in ("decision-brief.json", "risk-topic-brief.json", "periodic-brief.json"):
        check(f"简报 {name}", (run_dir / "brief" / name).is_file())
    check(
        "简报 DOCX",
        (run_dir / "brief" / "决策简报-阶段.docx").is_file(),
    )
    check("知识包 JSON", (run_dir / "knowledge" / "knowledge-bundle.json").is_file())
    check("知识复用 JSON", (run_dir / "knowledge" / "reuse-prj002.json").is_file())
    check(
        "身份注册 JSON",
        (run_dir / "identity" / "registrations.json").is_file(),
    )
    check(
        "驾驶舱 API 响应",
        (run_dir / "cockpit" / "api-responses.json").is_file(),
    )
    check(
        "驾驶舱终态视图",
        (run_dir / "cockpit" / "final-views.json").is_file(),
    )
    final_views = run_dir / "cockpit" / "final-views.json"
    if final_views.is_file():
        try:
            views = json.loads(final_views.read_text(encoding="utf-8"))
            check(
                "终态视图含双项目",
                len(views.get("workspaces", [])) >= 2,
                str(len(views.get("workspaces", []))),
            )
        except Exception as exc:  # pragma: no cover
            check("终态视图 JSON 可解析", False, str(exc)[:120])

    audit_path = run_dir / "audit" / "audit-events.jsonl"
    audit_lines = (
        len(audit_path.read_text(encoding="utf-8").splitlines())
        if audit_path.is_file()
        else 0
    )
    check(
        "审计事件数与 summary 一致",
        audit_lines == int(summary.get("audit_event_count", -1)),
        f"{audit_lines}/{summary.get('audit_event_count')}",
    )
    check("驾驶舱 API 巡检项数", summary.get("cockpit_api_probes", 0) >= 9)
    check("错误接收人拒绝", summary.get("wrong_recipient_rejected") is True)
    check("重放被拦截", bool(summary.get("replay_rejected")))
    check("演示报告存在", (run_dir / "demo-report.html").is_file())
    narrative = run_dir / "NARRATIVE.md"
    check(
        "NARRATIVE.md 非空",
        narrative.is_file() and narrative.stat().st_size > 1000,
        str(narrative.stat().st_size if narrative.is_file() else 0),
    )

    print(f"核验运行目录：{run_dir}")
    failed = 0
    for name, ok, detail in checks:
        mark = "通过" if ok else "失败"
        print(f"  [{mark}] {name}" + (f"（{detail}）" if detail else ""))
        if not ok:
            failed += 1
    total = len(checks)
    print(
        f"\n核验结果：{total - failed}/{total} 项通过"
        + ("，全部通过。" if failed == 0 else f"，{failed} 项失败。")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
