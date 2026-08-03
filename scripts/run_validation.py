"""run_validation.py — 把现有 opencode 验证转成机器可读报告。

输出位置：
  default → 文本表格到 stdout
  --report json → JSON 到 stdout
  --report file → 追加到 loop/VERIFICATION.md

依赖：调用 scripts/validate_opencode.py（其返回的诊断文本透传）。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(os.environ.get("COEVO_REPO_ROOT",Path(__file__).resolve().parents[1]))
VERIFY = "scripts/validate_opencode.py"

EXPECTED_FILES = [
    "AGENTS.md", "opencode.jsonc", "Makefile",
    "docs/README.md",
    "docs/requirements/system-requirements.md",
    "docs/requirements/mvp-user-stories.md",
    "docs/constraints/mandatory-technical-constraints.md",
    "docs/architecture/mvp-reference-architecture.md",
    "docs/protocol/agent-package-protocol.md",
    "docs/traceability/requirements-test-matrix.md",
    "loop/README.md", "loop/STATE.json", "loop/BACKLOG.yaml",
    "loop/GOAL.md", "loop/VERIFICATION.md",
    "loop/DECISIONS.md", "loop/tool-audit.jsonl",
    ".opencode/agents/loop-engineer.md",
    ".opencode/agents/mvp-planner.md",
    ".opencode/agents/mvp-builder.md",
    ".opencode/agents/mvp-verifier.md",
    ".opencode/agents/protocol-reviewer.md",
    ".opencode/agents/security-reviewer.md",
    ".opencode/commands/loop.md",
    ".opencode/commands/verify-story.md",
    ".opencode/commands/loop-status.md",
    ".opencode/skills/mvp-requirements/SKILL.md",
    ".opencode/skills/agent-package/SKILL.md",
    ".opencode/skills/acceptance-testing/SKILL.md",
    ".opencode/plugins/loop-guard.ts",
    ".opencode/plugins/README.md",
    ".opencode/tools/loop_state.ts",
    ".opencode/tools/quality_gate.ts",
    ".opencode/tools/traceability_check.ts",
    ".opencode/tools/README.md",
    "scripts/loop_state.py",
    "scripts/quality_gate.py",
    "scripts/traceability_check.py",
    "scripts/check_loop_stop.py",
    "scripts/run-loop.ps1",
]


def strip_jsonc(text: str) -> str:
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] not in ("\n", "\r"):
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def run_validator() -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, VERIFY],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout + proc.stderr


def collect_extra_metrics() -> dict:
    started = _dt.datetime.now(_dt.UTC)

    files_missing = sorted([f for f in EXPECTED_FILES if not (ROOT / f).exists()])
    project_jsonc = json.loads(strip_jsonc((ROOT / "opencode.jsonc").read_text(encoding="utf-8")))
    perms = project_jsonc.get("permission", {})
    bash_keys = sorted((perms.get("bash") or {}).keys())
    skill_allow = sorted(k for k, v in (perms.get("skill") or {}).items() if v == "allow")
    task_allow = sorted(k for k, v in (perms.get("task") or {}).items() if v == "allow")

    projdata = os.environ.get("ProgramData", "C:/ProgramData")
    org_dir = Path(projdata) / "opencode"
    org_policy_exists = (org_dir / "opencode.jsonc").exists()

    backlog = yaml.safe_load((ROOT / "loop/BACKLOG.yaml").read_text(encoding="utf-8"))
    by_status: dict[str, int] = {}
    for it in backlog.get("items", []):
        by_status[it.get("status", "?")] = by_status.get(it.get("status", "?"), 0) + 1

    audit_lines = 0
    with open(ROOT / "loop/tool-audit.jsonl", encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                audit_lines += 1

    finished = _dt.datetime.now(_dt.UTC)
    return {
        "timestamp": started.isoformat().replace("+00:00", "Z"),
        "duration_ms": int((finished - started).total_seconds() * 1000),
        "files": {
            "expected": len(EXPECTED_FILES),
            "missing": files_missing,
            "missing_count": len(files_missing),
        },
        "opencode_jsonc": {
            "permission_top_keys": sorted(perms.keys()),
            "bash_subkeys": bash_keys,
            "skill_allow": skill_allow,
            "task_allow": task_allow,
        },
        "org_policy": {"path": str(org_dir), "exists": org_policy_exists},
        "backlog": {"items": len(backlog.get("items", [])), "status_counts": by_status},
        "audit": {"lines": audit_lines},
    }


def render_text(metrics: dict, validator_stdout: str, validator_exit: int) -> str:
    out = ["# Coevo / OpenCode 配置验证报告", ""]
    out.append(f"- 时间戳：`{metrics['timestamp']}`")
    out.append(f"- 仓库根：`{metrics['root']}`")
    out.append(f"- validate_opencode.py 退出码：`{validator_exit}`")
    out.append(f"- 本报告构建耗时：`{metrics['duration_ms']} ms`")
    out.append("")
    out.append("## 1. 文件完整性")
    f = metrics["files"]
    out.append(f"- 预期：`{f['expected']}`  缺失：`{f['missing_count']}`")
    if f["missing"]:
        for m in f["missing"]:
            out.append(f"  - `{m}`")
    out.append("")
    out.append("## 2. 项目级 opencode.jsonc")
    j = metrics["opencode_jsonc"]
    out.append(f"- permission 顶层键：`{j['permission_top_keys']}`")
    out.append(f"- bash 子键数：`{len(j['bash_subkeys'])}`")
    out.append(f"- 显式 allow 的 skill：`{j['skill_allow']}`")
    out.append(f"- 显式 allow 的 task Agent：`{j['task_allow']}`")
    out.append("")
    out.append("## 3. 组织级策略")
    o = metrics["org_policy"]
    out.append(f"- 路径：`{o['path']}`")
    out.append(f"- 存在：`{o['exists']}`")
    out.append("")
    out.append("## 4. 状态机")
    b = metrics["backlog"]
    out.append(f"- BACKLOG 工作项：`{b['items']}`")
    out.append(f"- 状态分布：`{b['status_counts']}`")
    out.append(f"- tool-audit 行数：`{metrics['audit']['lines']}`")
    out.append("")
    out.append("## 5. validate_opencode.py 原始输出")
    out.append("```")
    out.append(validator_stdout.strip())
    out.append("```")
    return "\n".join(out)


def render_to_verification(metrics: dict, validator_exit: int) -> None:
    target = ROOT / "loop" / "VERIFICATION.md"
    ts = metrics["timestamp"]
    block = (
        f"\n## {ts} — `python scripts/run_validation.py`\n"
        f"- validator_exit: `{validator_exit}`\n"
        f"- files_missing_count: `{metrics['files']['missing_count']}`\n"
        f"- skill_allow: `{metrics['opencode_jsonc']['skill_allow']}`\n"
        f"- task_allow: `{metrics['opencode_jsonc']['task_allow']}`\n"
        f"- org_policy_exists: `{metrics['org_policy']['exists']}`\n"
        f"- backlog_items: `{metrics['backlog']['items']}`\n"
        f"- audit_lines: `{metrics['audit']['lines']}`\n\n"
    )
    with target.open("a", encoding="utf-8") as fh:
        fh.write(block)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", choices=["text", "json", "file"], default="text")
    args = parser.parse_args()

    validator_exit, validator_stdout = run_validator()
    metrics = collect_extra_metrics()
    metrics["root"] = str(ROOT)
    metrics["validator_exit"] = validator_exit

    if args.report == "json":
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    elif args.report == "file":
        render_to_verification(metrics, validator_exit)
        print(f"appended to loop/VERIFICATION.md (validator exit={validator_exit})")
    else:
        print(render_text(metrics, validator_stdout, validator_exit))
    return 0 if validator_exit == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
