"""Production logging bootstrap (stdlib ``logging``, no third-party deps).

This configures *application* operational logging (startup, shutdown,
errors, request counts). It is deliberately separate from the security
audit trail (``loop/tool-audit.jsonl`` + signed checkpoints), which must
never be routed through Python's standard logging.

* file handler: rotating, ``max_bytes`` per file, ``backup_count``
  rotated files, UTF-8;
* console handler: optional, defaults on;
* both share one deterministic formatter
  (``timestamp level logger message``).
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import AppConfig, ConfigError, VALID_LOG_LEVELS


_FORMAT: str = "%(asctime)s %(levelname)s %(name)s %(message)s"
_DATE_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"
_MAX_BYTES: int = 5 * 1024 * 1024
_BACKUP_COUNT: int = 5


def _level(level_name: str) -> int:
    if level_name not in VALID_LOG_LEVELS:
        raise ConfigError(f"invalid log level {level_name!r}")
    return getattr(logging, level_name)


def setup_logging(
    config: AppConfig | None = None,
    *,
    log_file: Path | None = None,
    console: bool = True,
    level: str = "INFO",
    reset: bool = False,
) -> logging.Logger:
    """Configure the root logger and return it.

    ``log_file`` may be supplied explicitly; otherwise it is derived
    from ``config.log_dir`` (or the local-app-data default) as
    ``coevo-app.log``. When ``reset`` is true the root logger's existing
    handlers are removed first (idempotent re-entry).
    """
    resolved_level = _level((config.log_level if config is not None else level))
    if config is not None:
        level_name = config.log_level
    else:
        level_name = level
    target: Path | None = log_file
    if target is None:
        base = config.log_dir if config is not None and config.log_dir else None
        target = (base or Path.home()) / "coevo-app.log"
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    if reset:
        for handler in list(root.handlers):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:  # noqa: BLE001 - never break startup on close
                pass

    root.setLevel(resolved_level)
    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)
    file_handler = RotatingFileHandler(
        target,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(resolved_level)
    root.addHandler(file_handler)
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(resolved_level)
        root.addHandler(console_handler)

    logger = logging.getLogger("coevo")
    logger.info(
        "logging initialised level=%s file=%s",
        level_name,
        str(target),
    )
    return logger


__all__ = ["setup_logging"]
