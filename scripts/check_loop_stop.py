"""check_loop_stop.py — 受限自动循环脚本的退出码决策器。

退出码：
 0  — mvp-complete
 10 — 继续下一轮
 20 — 阻断，需要人工决策
"""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    state_path = Path("loop/STATE.json")
    if not state_path.exists():
        print("STATE.json does not exist.")
        return 20

    state = json.loads(state_path.read_text(encoding="utf-8"))
    status = state.get("status")

    if status == "mvp-complete":
        return 0

    if status in {"blocked", "security-blocked", "decision-required"}:
        return 20

    return 10


if __name__ == "__main__":
    raise SystemExit(main())
