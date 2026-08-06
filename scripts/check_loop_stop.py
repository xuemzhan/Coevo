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

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        # OPTIMIZE-11: a malformed state file must block the loop with exit
        # code 20 instead of crashing the runner (fail-closed).
        print(f"STATE.json is unreadable or malformed: {exc}")
        return 20
    if not isinstance(state, dict):
        print("STATE.json is not a JSON object.")
        return 20
    status = state.get("status")

    if status == "mvp-complete":
        return 0

    if status in {"blocked", "security-blocked", "decision-required"}:
        return 20

    return 10


if __name__ == "__main__":
    raise SystemExit(main())
