"""examples 体系一键联合验证。

依次执行：
1. tool-dev-project 产物独立核验（verify_output.py，最新完整运行）
2. service-api 测试套件（run_tests.py，框架层 30 项 + 两个 E2E 冒烟）

任一环节失败返回非零退出码；全程离线。

用法：python examples\\run_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
except Exception:  # pragma: no cover - 非控制台环境
    pass


def run_step(label: str, script: str, *extra: str) -> int:
    command = [PYTHON, str(ROOT / script), *extra]
    print(f"===== [{label}] =====")
    print("$ " + " ".join(command))
    process = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1200,
    )
    output = (process.stdout + process.stderr).strip()
    print(output[-2500:] if output else "(no output)")
    return process.returncode


def main() -> int:
    steps = [
        (
            "tool-dev-project 产物独立核验",
            "examples/tool-dev-project/scripts/verify_output.py",
            (),
        ),
        (
            "service-api 测试套件",
            "examples/service-api/run_tests.py",
            (),
        ),
    ]
    failed = []
    for label, script, extra in steps:
        code = run_step(label, script, *extra)
        print(f"[{label}] 退出码={code}\n")
        if code != 0:
            failed.append(label)
    if failed:
        print("联合验证失败：" + "；".join(failed))
        return 1
    print("examples 体系联合验证全部通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
