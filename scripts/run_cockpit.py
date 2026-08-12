"""Production cockpit launcher (loopback-only, graceful shutdown).

Usage:
    python scripts/run_cockpit.py                  # start with env/defaults
    python scripts/run_cockpit.py --check          # validate config and exit
    python scripts/run_cockpit.py --preflight      # fail-fast startup checks and exit
    python scripts/run_cockpit.py --print-token    # print a one-time UI session token
    python scripts/run_cockpit.py --open           # open the cockpit in the browser
    python scripts/run_cockpit.py --version        # print version and exit
    python scripts/run_cockpit.py --port 12710     # override bind port

Configuration comes from :class:`src.coevo.config.AppConfig`
(environment-driven, fail-closed). On SIGINT/SIGTERM the server stops
gracefully: pending state is flushed, the single-instance lock and log
writer are released, and the process exits 0.

``--preflight`` (AVAIL-1) runs the same fail-fast checks operators use
before starting: config validity, data/log directory writability, free
disk space, audit-seal state and model-config loadability. Exit codes:
0 = ok, 1 = degraded (warnings), 2 = critical (do not start). Model
external-egress posture is reported as a degraded warning (OPS-4) when
the active provider is non-loopback and has ``external_data_ok=true``,
or when the legacy ``COEVO_LLM_EXTERNAL_DATA_OK`` switch is set; the
same warning is written to the app log at every start.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import threading
import webbrowser
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


def model_egress_warnings() -> list[str]:
    """Posture warnings when model external egress may be approved (OPS-4).

    Approval itself is fail-closed and legitimate (``config/model-config.json``
    ``external_data_ok``); this helper only makes it visible. Loopback
    providers never warn because their traffic stays on the machine.
    """
    warnings: list[str] = []
    if os.environ.get("COEVO_LLM_EXTERNAL_DATA_OK", "") == "1":
        warnings.append(
            "legacy COEVO_LLM_EXTERNAL_DATA_OK=1 is set "
            "(compat switch only; approval via config/model-config.json governs)"
        )
    try:
        from src.coevo.model.config import load_model_config
        from src.coevo.model.openai_compatible import is_loopback

        cfg = load_model_config()
    except Exception as exc:  # noqa: BLE001 - model config is advisory for startup
        warnings.append(
            f"model config unreadable ({exc}); offline default will be used"
        )
        return warnings
    if cfg.external_data_ok and cfg.base_url and not is_loopback(cfg.base_url):
        warnings.append(
            f"model external egress is APPROVED (provider={cfg.provider}, "
            "external_data_ok=true): data may leave this machine"
        )
    return warnings


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
            cockpit_checkpoint_interval_sec=config.cockpit_checkpoint_interval_sec,
            log_level=config.log_level,
            cockpit_state_path=config.cockpit_state_path,
            cockpit_log_path=config.cockpit_log_path,
            cockpit_lock_path=config.cockpit_lock_path,
        )
    return config


def preflight(config: AppConfig, *, python: str | None = None) -> int:
    """Run fail-fast startup checks (AVAIL-1). Returns 0/1/2."""
    problems: list[str] = []
    warnings: list[str] = []
    data_dir = config.data_dir or (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "KaiwuAgent"
    )
    log_dir = config.log_dir or data_dir
    for label, directory in (("data", data_dir), ("log", log_dir)):
        try:
            directory.mkdir(parents=True, exist_ok=True)
            probe = directory / ".preflight-probe"
            probe.write_text("probe", encoding="utf-8")
            probe.unlink()
        except OSError as exc:
            problems.append(f"{label} dir not writable ({exc})")
    try:
        usage = shutil.disk_usage(data_dir)
        if usage.free < 256 * 1024 * 1024:
            problems.append(f"free disk space low: {usage.free} bytes")
    except OSError as exc:
        problems.append(f"cannot stat disk ({exc})")
    try:
        interpreter = python or sys.executable
        result = subprocess.run(
            [interpreter, str(ROOT / "scripts" / "audit_seal.py"), "verify"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        status = ""
        try:
            status = json.loads(result.stdout or "{}").get("status", "")
        except json.JSONDecodeError:
            pass
        if status == "fully-sealed":
            pass
        elif status == "valid-prefix-with-unsealed-tail":
            warnings.append("audit has an unsealed tail (run make quality to re-seal)")
        else:
            problems.append(
                "audit seal verify failed: "
                + (result.stderr or result.stdout or "unknown").strip()[:200]
            )
    except subprocess.TimeoutExpired:
        problems.append("audit seal verify timed out")
    warnings.extend(model_egress_warnings())
    print("preflight ok" if not problems else "preflight critical")
    for problem in problems:
        print(f"  critical: {problem}")
    for warning in warnings:
        print(f"  warning: {warning}")
    return 2 if problems else (1 if warnings else 0)


def run(args: argparse.Namespace) -> int:
    config = build_config(args)
    if args.check:
        print(
            f"config ok: host={config.cockpit_host} port={config.cockpit_port} "
            f"log_level={config.log_level}"
        )
        return 0
    if args.preflight:
        return preflight(config)
    logger = setup_logging(config)
    for warning in model_egress_warnings():
        logger.warning("model egress posture: %s", warning)
    http_config_kwargs = dict(
        bind_host=config.cockpit_host,
        bind_port=config.cockpit_port,
        session_timeout_sec=config.session_timeout_sec,
        state_snapshot_interval_sec=config.cockpit_checkpoint_interval_sec,
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
    if args.print_token or args.open:
        # REVIEW-FIX-2: interactive token handoff. The raw token is shown
        # once on stdout (never via the logging framework and never written
        # to disk); the server retains only its SHA-256 digest.
        token = server.session_manager.create()
        if args.print_token:
            print(f"session token: {token}", flush=True)
        # 直接打印可点击的完整地址，方便使用者复制粘贴。
        open_url = f"{server.url}?token={token}"
        print(f"open cockpit: {open_url}", flush=True)
        if args.open:
            webbrowser.open(open_url)
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
    parser.add_argument(
        "--print-token",
        action="store_true",
        help="issue and print a one-time UI session token at startup (stdout only)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="issue a session token and open the cockpit in the default browser",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="run fail-fast startup checks and exit (0 ok / 1 degraded / 2 critical)",
    )
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
