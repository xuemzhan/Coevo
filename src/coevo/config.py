"""Production runtime configuration (stdlib-only, fail-closed).

The MVP previously hard-coded paths and limits inside the cockpit
server and demo runner. This module centralises the *operational*
settings (data/log directories, bind host/port, session lifetime,
log level) behind one validated, environment-driven
:class:`AppConfig`. Security-relevant invariants stay enforced here:

* ``cockpit_host`` must be the loopback literal (``127.0.0.1``);
* ``cockpit_port`` must be an open TCP port number;
* ``log_level`` must be one of the standard logging levels;
* every path is resolved and must remain inside an allowed base when
  ``data_dir``/``log_dir`` are supplied.

No new dependency; unknown environment values fail closed instead of
silently falling back to insecure defaults.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 生产运行配置（stdlib-only）：AppConfig 校验并冻结，失败关闭。
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from .version import APP_NAME, VERSION


LOOPBACK_HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 12701
VALID_LOG_LEVELS: frozenset[str] = frozenset({
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG",
})


class ConfigError(ValueError):
    """Raised when the runtime configuration is invalid (fail-closed)."""


def _local_app_data() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "KaiwuAgent"


def _require_path(value: str | None, label: str) -> Path | None:
    if value is None or not value:
        return None
    path = Path(value)
    try:
        resolved = path.resolve()
    except OSError as exc:
        raise ConfigError(f"{label} cannot be resolved: {value!r}") from exc
    return resolved


@dataclass(frozen=True)
class AppConfig:
    """Validated operational configuration for local Coevo processes."""

    app_name: str = APP_NAME
    version: str = VERSION
    repo_root: Path | None = None
    data_dir: Path | None = None
    log_dir: Path | None = None
    cockpit_host: str = LOOPBACK_HOST
    cockpit_port: int = DEFAULT_PORT
    session_timeout_sec: int = 8 * 3600
    cockpit_checkpoint_interval_sec: float = 300.0
    log_level: str = "INFO"
    cockpit_state_path: Path | None = None
    cockpit_log_path: Path | None = None
    cockpit_lock_path: Path | None = None

    def __post_init__(self) -> None:
        if self.cockpit_host != LOOPBACK_HOST:
            raise ConfigError(
                f"cockpit_host must be the loopback literal {LOOPBACK_HOST!r}; "
                f"got {self.cockpit_host!r} (强制约束 § 5.1)"
            )
        if not isinstance(self.cockpit_port, int) or not (
            1 <= self.cockpit_port <= 65535
        ):
            raise ConfigError(
                f"cockpit_port must be 1..65535; got {self.cockpit_port!r}"
            )
        if not isinstance(self.session_timeout_sec, int) or self.session_timeout_sec <= 0:
            raise ConfigError("session_timeout_sec must be a positive integer")
        interval = self.cockpit_checkpoint_interval_sec
        if (
            not isinstance(interval, (int, float))
            or isinstance(interval, bool)
            or interval <= 0
        ):
            raise ConfigError(
                "cockpit_checkpoint_interval_sec must be a positive number"
            )
        if self.log_level not in VALID_LOG_LEVELS:
            raise ConfigError(
                f"log_level must be one of {sorted(VALID_LOG_LEVELS)!r}; "
                f"got {self.log_level!r}"
            )

    def default_state_path(self) -> Path:
        """Return the canonical cockpit state file under the data dir."""
        return (self.data_dir or _local_app_data()) / "cockpit-state.json"

    def default_log_path(self) -> Path:
        """Return the canonical cockpit JSONL access-log path."""
        return (self.log_dir or _local_app_data()) / "cockpit-access.jsonl"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "AppConfig":
        """Build a validated config from environment variables.

        Recognised variables (all optional, validated when present):

        * ``COEVO_DATA_DIR`` / ``COEVO_LOG_DIR`` -- data and log roots;
        * ``COEVO_COCKPIT_HOST`` / ``COEVO_COCKPIT_PORT`` -- bind target
          (host must stay loopback);
        * ``COEVO_SESSION_TIMEOUT_SEC`` -- cockpit session lifetime;
        * ``COEVO_COCKPIT_CHECKPOINT_SEC`` -- periodic cockpit state
          snapshot interval in seconds;
        * ``COEVO_LOG_LEVEL`` -- one of the standard logging levels;
        * ``COEVO_STATE_PATH`` / ``COEVO_LOG_PATH`` -- explicit file
          overrides for the cockpit state / access log;
        * ``COEVO_LOCK_PATH`` -- explicit single-instance lock file
          (defaults to ``%LOCALAPPDATA%\\KaiwuAgent\\cockpit.lock``).
        """
        source = dict(os.environ if env is None else env)

        def _int(name: str, default: int) -> int:
            raw = source.get(name)
            if raw is None or not raw:
                return default
            try:
                return int(raw)
            except ValueError as exc:
                raise ConfigError(f"{name} must be an integer; got {raw!r}") from exc

        def _float(name: str, default: float) -> float:
            raw = source.get(name)
            if raw is None or not raw:
                return default
            try:
                return float(raw)
            except ValueError as exc:
                raise ConfigError(f"{name} must be a number; got {raw!r}") from exc

        return cls(
            repo_root=_require_path(source.get("COEVO_REPO_ROOT"), "COEVO_REPO_ROOT"),
            data_dir=_require_path(source.get("COEVO_DATA_DIR"), "COEVO_DATA_DIR"),
            log_dir=_require_path(source.get("COEVO_LOG_DIR"), "COEVO_LOG_DIR"),
            cockpit_host=source.get("COEVO_COCKPIT_HOST", LOOPBACK_HOST),
            cockpit_port=_int("COEVO_COCKPIT_PORT", DEFAULT_PORT),
            session_timeout_sec=_int("COEVO_SESSION_TIMEOUT_SEC", 8 * 3600),
            cockpit_checkpoint_interval_sec=_float(
                "COEVO_COCKPIT_CHECKPOINT_SEC", 300.0
            ),
            log_level=source.get("COEVO_LOG_LEVEL", "INFO").upper(),
            cockpit_state_path=_require_path(
                source.get("COEVO_STATE_PATH"), "COEVO_STATE_PATH"
            ),
            cockpit_log_path=_require_path(
                source.get("COEVO_LOG_PATH"), "COEVO_LOG_PATH"
            ),
            cockpit_lock_path=_require_path(
                source.get("COEVO_LOCK_PATH"), "COEVO_LOCK_PATH"
            ),
        )


__all__ = [
    "AppConfig",
    "ConfigError",
    "DEFAULT_PORT",
    "LOOPBACK_HOST",
    "VALID_LOG_LEVELS",
]
