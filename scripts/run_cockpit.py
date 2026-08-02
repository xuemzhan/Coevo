"""Production cockpit launcher (loopback-only, graceful shutdown).

Usage:
    python scripts/run_cockpit.py                  # start with env/defaults
    python scripts/run_cockpit.py --check          # validate config and exit
    python scripts/run_cockpit.py --version        # print version and exit
    python scripts/run_cockpit.py --port 12710     # override bind port

Configuration comes from :class:`src.coevo.config.AppConfig`
(environment-driven, fail-closed). On SIGINT/SIGTERM the server stops
gracefully: pending state is flushed, the single-instance lock and log
writer are released, and the process exits 0.
"""
from __future__ import annotations

import argparse
import signal
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.cockpit.server import (  # noqa: E402
    CockpitHttpConfig,
    CockpitHttpServer,
)
from src.coevo.config import AppConfig, ConfigError  # noqa: E402
from src.coevo.logging_setup import setup_logging  # noqa: E402
from src.coevo.version import version_string  # noqa: E402


def build_config(args: argparse.Namespace) -> AppConfig:
    """Merge CLI overrides on top of the environment-driven config."""
    config = AppConfig.from_env()
    if args.port is not None:
        config = AppConfig(
            app_name=config.app_name,
            version=config.version,
            repo_root=config.repo_root,
            data_dir=config.data_dir,
            log_dir=config.log_dir,
            cockpit_host=config.cockpit_host,
            cockpit_port=args.port,
            session_timeout_sec=config.session_timeout_sec,
            log_level=config.log_level,
            cockpit_state_path=config.cockpit_state_path,
            cockpit_log_path=config.cockpit_log_path,
        )
    return config


def run(args: argparse.Namespace) -> int:
    config = build_config(args)
    if args.check:
        print(
            f"config ok: host={config.cockpit_host} port={config.cockpit_port} "
            f"log_level={config.log_level}"
        )
        return 0
    logger = setup_logging(config)
    http_config_kwargs = dict(
        bind_host=config.cockpit_host,
        bind_port=config.cockpit_port,
        session_timeout_sec=config.session_timeout_sec,
        state_path=config.cockpit_state_path or config.default_state_path(),
        log_path=config.cockpit_log_path or config.default_log_path(),
    )
    if config.cockpit_lock_path is not None:
        # Only override the single-instance lock when explicitly
        # configured; otherwise the server keeps its default lock.
        http_config_kwargs["lock_path"] = config.cockpit_lock_path
    http_config = CockpitHttpConfig(**http_config_kwargs)
    server = CockpitHttpServer(http_config)
    logger.info(
        "cockpit listening on %s (state=%s log=%s)",
        server.url,
        http_config.state_path,
        http_config.log_path,
    )
    print(f"coevo cockpit ready: {server.url}")
    stop_event = threading.Event()

    def _shutdown(_signum: int, _frame: object) -> None:
        logger.info("shutdown signal received; stopping cockpit")
        stop_event.set()

    signal.signal(signal.SIGINT, _shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _shutdown)
    if hasattr(signal, "SIGBREAK"):
        # Windows console break (CTRL+BREAK) must also stop gracefully
        # instead of terminating the process without flushing state.
        signal.signal(signal.SIGBREAK, _shutdown)
    try:
        # serve_forever runs on a background thread so the signal
        # handler (main thread) never deadlocks waiting for it.
        server.start()
        while not stop_event.wait(0.5):
            pass
    finally:
        server.stop()
        logger.info("cockpit stopped")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coevo local cockpit server")
    parser.add_argument("--port", type=int, default=None, help="bind port (loopback only)")
    parser.add_argument("--check", action="store_true", help="validate configuration and exit")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    args = parser.parse_args(argv)
    if args.version:
        print(version_string())
        return 0
    try:
        return run(args)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - launcher surfaces startup failures
        print(f"startup failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
