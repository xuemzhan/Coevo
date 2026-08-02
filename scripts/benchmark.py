"""Offline Coevo performance benchmark runner (reference architecture 14).

Usage:
    python scripts/benchmark.py                 # run all, print table + JSON
    python scripts/benchmark.py --check         # exit non-zero if any SLA misses
    python scripts/benchmark.py --samples 2     # run 2x samples for timing stability
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coevo.benchmarks import measure, report  # noqa: E402


def _sample_views():
    from src.coevo.cockpit import (
        ArtifactSummary,
        CockpitFacade,
        CockpitRequest,
        CockpitRoute,
        MilestoneSummary,
        RoleView,
        TaskSummary,
        WorkspaceView,
    )

    workspace_views = tuple(
        WorkspaceView(
            f"PRJ{index:03d}",
            f"Project {index}",
            ("a.pm", "a.eng"),
            100,
            10,
            20,
        )
        for index in range(50)
    )
    role_views = tuple(
        RoleView(
            "a.eng",
            f"PRJ{index:03d}",
            "Engineering",
            tuple(
                TaskSummary(
                    f"t.{task}",
                    f"task {task}",
                    "in_progress",
                    "2026-09-01",
                    "a.eng",
                )
                for task in range(100)
            ),
            (MilestoneSummary("m.1", "review", "2026-09-15", False),),
            (
                ArtifactSummary(
                    "docs/r.docx",
                    "document",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    128,
                    "0" * 64,
                ),
            ),
        )
        for index in range(50)
    )
    state = CockpitFacade.start_server(
        workspace_views=workspace_views,
        role_views=role_views,
        now="2026-08-02T00:00:00Z",
    )
    return CockpitFacade, CockpitRequest, CockpitRoute, state


def _watcher_scan(root: Path):
    from src.coevo.progress_capture import WorkspaceWatcher

    watcher = WorkspaceWatcher(root, stability_checks=1, poll_interval_sec=0.05)
    return lambda: watcher.scan(now="2026-08-02T00:00:00Z")


def _package_fixture():
    from src.coevo.app import ensure_demo_profile
    from src.coevo.crypto import GmsslPrototypeProvider
    from src.coevo.protocol import (
        build_encrypted_package,
        build_envelope_template,
        parse_package_bytes,
    )

    ensure_demo_profile()
    provider = GmsslPrototypeProvider(ROOT)
    sender = provider.sender_handle("demo", "CERT-SENDER")
    recipient = provider.recipient_handle("demo", "CERT-RECIPIENT")
    package = build_encrypted_package(
        envelope=build_envelope_template(
            sender_cert_id="CERT-SENDER",
            recipient_cert_id="CERT-RECIPIENT",
            project_id="PRJ001",
            package_type="TASK_ASSIGNMENT",
            sequence_no=1,
            payload_length=0,
            created_at="2026-08-02T00:00:00Z",
            expires_at="2027-08-02T00:00:00Z",
        ),
        manifest={"project_id": "PRJ001", "task_id": "t.1"},
        content=b"small package payload",
        provider=provider,
        sender_handle=sender,
        recipient_handle=recipient,
        signed_at="2026-08-02T00:00:00Z",
    )
    return provider, sender, recipient, package


def run(samples: int = 1) -> tuple:
    results = []

    facade, request_cls, route_cls, state = _sample_views()
    now = "2026-08-02T00:00:00Z"
    project_request = request_cls(route_cls.PROJECT_VIEW, "PRJ000", "", "", "", now)
    task_request = request_cls(route_cls.TASK_VIEW, "PRJ000", "a.eng", "t.50", "", now)

    results.append(
        measure(
            "page_open",
            "project view dispatch",
            lambda: facade.dispatch(project_request, server_state=state, now=now),
            limit=3.0,
            unit="seconds",
            samples=max(50, 50 * samples),
        )
    )
    results.append(
        measure(
            "task_query",
            "task view dispatch",
            lambda: facade.dispatch(task_request, server_state=state, now=now),
            limit=2.0,
            unit="seconds",
            samples=max(100, 100 * samples),
        )
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for index in range(200):
            (root / f"doc-{index}.md").write_text(f"content {index}", encoding="utf-8")
        results.append(
            measure(
                "dir_discovery",
                "watcher scan (200 files)",
                _watcher_scan(root),
                limit=5.0,
                unit="seconds",
                samples=max(3, 3 * samples),
            )
        )

    provider, sender, recipient, package = _package_fixture()
    wire = package.to_bytes()
    from src.coevo.protocol import parse_package_bytes

    results.append(
        measure(
            "package_check",
            "small encrypted package wire parse",
            lambda: parse_package_bytes(wire),
            limit=10.0,
            unit="seconds",
            samples=max(50, 50 * samples),
        )
    )

    def generate() -> float:
        from src.coevo.protocol import build_encrypted_package, build_envelope_template

        success = 0
        total = max(3, 3 * samples)
        first_error = ""
        for _ in range(total):
            try:
                build_encrypted_package(
                    envelope=build_envelope_template(
                        sender_cert_id="CERT-SENDER",
                        recipient_cert_id="CERT-RECIPIENT",
                        project_id="PRJ001",
                        package_type="TASK_ASSIGNMENT",
                        sequence_no=1,
                        payload_length=0,
                        created_at="2026-08-02T00:00:00Z",
                        expires_at="2027-08-02T00:00:00Z",
                    ),
                    manifest={"project_id": "PRJ001", "task_id": "t.1"},
                    content=b"payload",
                    provider=provider,
                    sender_handle=sender,
                    recipient_handle=recipient,
                    signed_at="2026-08-02T00:00:00Z",
                )
                success += 1
            except Exception as exc:
                if not first_error:
                    first_error = f"{type(exc).__name__}: {str(exc)[:120]}"
                continue
        global _LAST_GENERATION_ERROR
        _LAST_GENERATION_ERROR = first_error
        return success / total * 100.0

    results.append(
        measure(
            "package_generation",
            "encrypted package build success rate",
            generate,
            limit=95.0,
            unit="percent",
            comparison="ge",
            samples=1,
        )
    )
    if _LAST_GENERATION_ERROR:
        last = results[-1]
        results = results[:-1] + [
            type(last)(
                last.name, last.metric, last.value, last.unit, last.limit,
                last.comparison, last.ok, last.samples,
                detail=_LAST_GENERATION_ERROR,
            ),
        ]
    return tuple(results)


_LAST_GENERATION_ERROR: str = ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline Coevo benchmark suite")
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    results = run(args.samples)
    data = report(results)
    for item in data["results"]:
        marker = "OK " if item["ok"] else "MISS"
        print(
            f"[{marker}] {item['name']:<20} {item['value']:>10.3f} {item['unit']:<8} "
            f"(limit {item['comparison']} {item['limit']}) samples={item['samples']}"
        )
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    if args.check and not data["all_ok"]:
        print("BENCHMARK CHECK FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
