"""Offline Coevo MVP demo runner (CLI).

Usage:
    python scripts/run_demo.py --smoke                # headless end-to-end check
    python scripts/run_demo.py --runtime-dir <dir>    # run + cockpit server
    python scripts/run_demo.py --no-server            # run pipeline only
    python scripts/run_demo.py --interactive          # pause at the confirmation gate
    python scripts/run_demo.py --serve-gate           # confirm via the cockpit
    python scripts/run_demo.py --quiet                # suppress progress output
    python scripts/run_demo.py --open                 # open cockpit in the browser
    python scripts/run_demo.py --resume <dir>         # reopen a finished run's cockpit
    python scripts/run_demo.py --json                 # machine-readable result
"""
from __future__ import annotations

import argparse
import sys
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.app import run_demo_pipeline  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Coevo MVP demo")
    parser.add_argument(
        "--runtime-dir",
        default=str(ROOT / "loop" / "runtime" / "demo"),
        help="parent directory for demo run artifacts",
    )
    parser.add_argument("--port", type=int, default=12751)
    parser.add_argument(
        "--session-hours",
        type=int,
        default=8,
        help="cockpit session lifetime in hours (default 8)",
    )
    parser.add_argument(
        "--lock-path",
        default="",
        help="override the cockpit single-instance lock file",
    )
    parser.add_argument("--no-server", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--serve-gate", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--open", action="store_true")
    parser.add_argument(
        "--resume",
        default="",
        help="reopen an existing demo run's cockpit state (dir or state file)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        from src.coevo.version import version_string

        print(version_string())
        return 0

    if args.smoke and args.interactive:
        print("--smoke and --interactive are mutually exclusive", file=sys.stderr)
        return 2
    if args.json and args.smoke:
        print("--smoke and --json are mutually exclusive", file=sys.stderr)
        return 2
    if args.interactive and args.json:
        print("--interactive and --json are mutually exclusive", file=sys.stderr)
        return 2
    if args.interactive and args.quiet:
        print("--interactive and --quiet are mutually exclusive", file=sys.stderr)
        return 2
    if args.serve_gate and (
        args.interactive or args.json or args.smoke or args.no_server
        or args.open or args.resume
    ):
        print(
            "--serve-gate is a standalone cockpit-confirmation mode "
            + "(cannot combine with other run modes)",
            file=sys.stderr,
        )
        return 2
    if args.open and (args.smoke or args.no_server or args.json):
        print(
            "--open requires the cockpit server "
            + "(cannot combine with --smoke/--no-server/--json)",
            file=sys.stderr,
        )
        return 2
    if args.resume and (
        args.smoke or args.no_server or args.json
        or args.interactive or args.open
    ):
        print(
            "--resume is a standalone mode "
            + "(cannot combine with other run modes)",
            file=sys.stderr,
        )
        return 2
    if args.session_hours <= 0 or args.session_hours > 24 * 30:
        print("--session-hours must be between 1 and 720", file=sys.stderr)
        return 2
    if args.resume:
        return _serve_resumed(args)

    progress = None
    if not args.quiet and not args.smoke and not args.json:
        print("=" * 64)
        print("Coevo 离线演示开始：全流程离线、可复现。")
        print("=" * 64, flush=True)
        progress_counter = {"value": 0}
        def progress(message):
            progress_counter["value"] += 1
            print(
                f"[{progress_counter['value']}/7] {message}",
                flush=True,
            )

    confirm_callback = None
    if args.interactive:
        def confirm_callback(preview):
            print()
            print("到达人工确认节点：")
            print(f"  事件：{preview.event_id}")
            print(f"  项目：{preview.project_id} · 任务：{preview.task_id}")
            print(f"  基线版本：{preview.base_revision}")
            print(f"  任务包类型：{preview.package_type}")
            print(f"  载荷摘要：{preview.payload_digest[:16]}…")
            while True:
                answer = input("按回车授权下发，输入 n 拒绝：").strip().lower()
                if answer in ("", "y", "yes"):
                    print("已授权，继续执行。", flush=True)
                    return True
                if answer in ("n", "no"):
                    print("已拒绝，演示中止。", flush=True)
                    return False

    gate_ready = None
    if args.serve_gate:
        def gate_ready(cockpit_url, cockpit_token):
            open_url = cockpit_url.rstrip("/") + "?token=" + cockpit_token
            print(f"open cockpit: {open_url}", flush=True)
            if args.open:
                webbrowser.open(open_url)

    try:
        result = run_demo_pipeline(
            Path(args.runtime_dir),
            with_cockpit=not args.no_server and not args.smoke,
            cockpit_port=args.port,
            progress=progress,
            confirm_callback=confirm_callback,
            session_timeout_sec=args.session_hours * 3600,
            confirm_via_web=args.serve_gate,
            gate_ready=gate_ready,
            cockpit_lock_path=(
                Path(args.lock_path) if args.lock_path else None
            ),
        )
    except RuntimeError as exc:
        if "rejected by operator" in str(exc):
            print("演示中止：负责人拒绝了任务下发。", file=sys.stderr)
            return 1
        raise

    if args.json:
        import json as _json

        payload = {
            "outcome": result.outcome,
            "package_path": str(result.package_path) if result.package_path else None,
            "package_sha256": result.package_wire_sha256,
            "knowledge_bundle_id": result.knowledge_bundle_id,
            "audit_event_count": result.audit_event_count,
            "audit_chain_entries": 0,
            "audit_chain_head": "",
            "audit_chain_valid": False,
            "cockpit_url": result.cockpit_url,
            "cockpit_token": result.cockpit_token or None,
        }
        try:
            entries = getattr(result.store, "audit_entries", ())
            payload["audit_chain_entries"] = len(entries)
            if entries:
                payload["audit_chain_head"] = entries[-1].entry_hash
            payload["audit_chain_valid"] = bool(
                getattr(result.store, "verify_audit_chain", lambda: False)()
            )
        except Exception:
            pass
        print(_json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.smoke:
        if result.outcome != "completed" or result.package_path is None:
            print("DEMO FAILED", file=sys.stderr)
            return 1
        if not result.package_path.is_file():
            print("DEMO FAILED: package missing", file=sys.stderr)
            return 1
        print("DEMO OK")
        return 0

    print()
    print("演示完成。")
    print("  结果：", "成功" if result.outcome == "completed" else result.outcome)
    print(
        "  人工确认：",
        "由操作者交互授权"
        if args.interactive
        else "已在驾驶舱中确认"
        if args.serve_gate
        else "自动授权（使用 --interactive 可体验人工确认节点）",
    )
    print("  加密任务包：", result.package_path)
    print("  包 SHA-256：", result.package_wire_sha256)
    print("  知识包：", result.knowledge_bundle_id)
    print("  审计事件：", result.audit_event_count)
    audit_info = _audit_chain_summary(result)
    if audit_info:
        print("  审计链：", audit_info)
    try:
        if getattr(result.store, "verify_audit_chain", lambda: False)():
            print("  审计链校验：通过")
    except Exception:
        pass
    if result.cockpit_url:
        print("  驾驶舱地址：", result.cockpit_url)
        if result.cockpit_token:
            print(
                "  直接打开： " + result.cockpit_url.rstrip("/")
                + "?token=" + result.cockpit_token,
                flush=True,
            )
            if args.open:
                webbrowser.open(
                    result.cockpit_url.rstrip("/")
                    + "?token=" + result.cockpit_token
                )
    if result.runtime_dir:
        print()
        print("  之后可随时重开本次运行：")
        print(
            "    python " + Path(sys.argv[0]).name
            + " --resume " + str(result.runtime_dir)
        )
    if result.cockpit_url:
        print()
        print("Ctrl+C 停止驾驶舱服务。", flush=True)
    if args.smoke:
        if result.outcome != "completed" or result.package_path is None:
            print("DEMO FAILED", file=sys.stderr)
            return 1
        if not result.package_path.is_file():
            print("DEMO FAILED: package missing", file=sys.stderr)
            return 1
        print("DEMO OK")
        return 0
    if result.cockpit_url:
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
        finally:
            if getattr(result, "cockpit_server", None) is not None:
                result.cockpit_server.stop()
    return 0


def _audit_chain_summary(result) -> str:
    """Read the real-chain audit head for a compact integrity fingerprint."""
    try:
        store = getattr(result, "store", None)
        if store is None:
            return ""
        entries = getattr(store, "audit_entries", ())
        if not entries:
            return ""
        head = entries[-1].entry_hash
        return f"{len(entries)} 条 · 头部指纹 {head[:16]}…"
    except Exception:
        return ""


def _find_cockpit_state(target: str) -> Path:
    """Locate cockpit-state.json from a run dir, a run-* subdir, or a file."""
    candidate = Path(target)
    if candidate.is_file():
        return candidate
    direct = candidate / "cockpit-state.json"
    if direct.is_file():
        return direct
    runs = sorted(
        candidate.glob("run-*/cockpit-state.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if runs:
        return runs[0]
    raise FileNotFoundError(
        f"no cockpit-state.json found under {target!s}"
    )


def _serve_resumed(args) -> int:
    """Serve an existing run's cockpit snapshot without re-running the demo."""
    from src.coevo.cockpit.server import CockpitHttpConfig, CockpitHttpServer

    try:
        state_path = _find_cockpit_state(args.resume)
    except FileNotFoundError as exc:
        print(f"resume failed: {exc}", file=sys.stderr)
        return 2
    server = CockpitHttpServer(
        CockpitHttpConfig(
            bind_port=args.port,
            request_timeout_sec=5,
            state_path=state_path,
            lock_path=(Path(args.lock_path) if args.lock_path else None),
            session_timeout_sec=args.session_hours * 3600,
        )
    )
    try:
        server.start()
    except Exception as exc:
        print(f"startup failed: {exc}", file=sys.stderr)
        return 1
    token = server.session_manager.create()
    open_url = f"{server.url}?token={token}"
    print(f"resumed cockpit: {state_path}")
    print(f"open cockpit: {open_url}", flush=True)
    if args.open:
        webbrowser.open(open_url)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
