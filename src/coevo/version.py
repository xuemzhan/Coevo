"""Application version metadata for the Coevo MVP.

Versions are explicit semantic versions, never timestamps
(AGENTS.md 不得用时间戳代替项目版本). Bump ``VERSION`` on any release
and mirror it in the traceability matrix / release records.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 应用版本元数据：版本号/显示名集中定义。
from __future__ import annotations

APP_NAME: str = "coevo"
APP_DISPLAY_NAME: str = "Coevo"
VERSION: str = "0.2.0"
__version__: str = VERSION


def version_string() -> str:
    """Return ``"coevo 0.2.0"`` for CLI ``--version`` output."""
    return f"{APP_NAME} {VERSION}"
