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

from src.coevo.benchmarks import BenchmarkResult, measure, report  # noqa: E402


# LOAD-1: /healthz p95 latency SLA. The cockpit deliberately serves one
# request per connection (see CockpitRequestHandler._handle), so every
# probe request pays a fresh loopback TCP handshake; 1s keeps an order of
# magnitude of headroom below the reference-architecture page SLA (3s)
# while still being meaningful under 32-way concurrent load on Windows.
COCKPIT_HTTP_P95_LIMIT_SEC = 1.0


def _cockpit_http_probe() -> BenchmarkResult:
    """Healthz latency under bounded concurrency (LOAD-1).

    Starts a real loopback cockpit at the production concurrency cap
    (max_concurrent_requests=16), fires 128 GET /healthz requests from
    16 worker threads (8 requests each, one fresh connection per request,
    matching the server's one-request-per-connection production behavior),
    and reports the p95 per-request latency plus the error count.
    SLA: p95 <= COCKPIT_HTTP_P95_LIMIT_SEC with zero errors.
    """
    import socket
    import threading
    import time
    import urllib.request

    from src.coevo.cockpit import CockpitHttpConfig, CockpitHttpServer

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = CockpitHttpServer(
        CockpitHttpConfig(
            bind_port=port,
            request_timeout_sec=5,
            lock_path=None,
            # Probe exactly at the production concurrency bound (the
            # CockpitHttpConfig default), so the load is representative of
            # the server's designed capacity rather than a stress beyond it.
            max_concurrent_requests=16,
        ),
        workspace_views=(),
        role_views=(),
    )
    server.start()
    latencies: list[float] = []
    errors = 0
    lock = threading.Lock()
    workers = 16
    per_worker = 8

    def fire() -> None:
        nonlocal errors
        for _ in range(per_worker):
            start = time.perf_counter()
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/healthz", timeout=5
                ) as response:
                    if response.status != 200:
                        with lock:
                            errors += 1
            except Exception:  # noqa: BLE001 - any failed probe request counts as an error
                with lock:
                    errors += 1
            finally:
                with lock:
                    latencies.append(time.perf_counter() - start)

    try:
        threads = [threading.Thread(target=fire) for _ in range(workers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=60)
    finally:
        server.stop()

    latencies.sort()
    total = len(latencies)
    p95 = latencies[int(total * 0.95) - 1] if total else float("inf")
    p50 = latencies[int(total * 0.5) - 1] if total else float("inf")
    detail = (
        f"p50={p50:.4f}s max={latencies[-1]:.4f}s errors={errors}"
        if total
        else "no samples"
    )
    return BenchmarkResult(
        name="cockpit_http",
        metric="healthz p95 latency (128 req / 16 workers, at concurrency cap)",
        value=round(p95, 4),
        unit="seconds",
        limit=COCKPIT_HTTP_P95_LIMIT_SEC,
        comparison="le",
        ok=p95 <= COCKPIT_HTTP_P95_LIMIT_SEC and errors == 0,
        samples=total,
        detail=detail,
    )


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


def _dag_probe():
    """Build a large stage-ordered DAG (3k tasks / 30 packages)."""
    from src.coevo.task_decomposition.baseline import BaselineInput, build_baseline
    from src.coevo.task_decomposition.models import Deliverable, Task, WorkPackage

    packages = 30
    tasks_per_package = 100
    work_packages = tuple(
        WorkPackage(
            work_package_id=f"wp.{pkg}",
            standard_stage="execution",
            title=f"package {pkg}",
            tasks=tuple(
                Task(
                    task_id=f"t.{pkg}.{idx}",
                    title=f"task {pkg}.{idx}",
                    responsible_role="role.eng",
                    plan_start="2026-08-01T00:00:00Z",
                    plan_end="2026-08-31T00:00:00Z",
                    deliverables=(
                        Deliverable(
                            deliverable_id=f"d.{pkg}.{idx}",
                            title=f"output {pkg}.{idx}",
                            kind="document",
                            acceptance_criteria=("accepted_by_reviewer",),
                        ),
                    ),
                )
                for idx in range(tasks_per_package)
            ),
        )
        for pkg in range(packages)
    )
    project_input = BaselineInput(
        project_id="PRJ-BIG",
        title="large DAG probe",
        objective="measure dependency-graph scalability",
        plan_start="2026-08-01T00:00:00Z",
        plan_end="2026-08-31T00:00:00Z",
        responsible_units=("unit_a",),
        process_flow_ref=("unit_a", 1),
        work_packages=work_packages,
    )
    baseline = build_baseline(project_input)
    return baseline


def _registry_probe(records: int = 20_000):
    """Construct a large processed-package registry directly."""
    from src.coevo.protocol.processed_package_store import (
        ProcessedPackageRecord,
        ProcessedPackageStore,
    )
    from src.coevo.protocol.replay_detector import ProcessedPackage

    entries = tuple(
        ProcessedPackageRecord(
            package=ProcessedPackage(
                package_id=f"pkg.{index:06d}",
                package_digest=f"{index:064x}",
                sender_cert_id="CERT-SENDER",
                recipient_cert_id="CERT-RECIPIENT",
                project_id="PRJ001",
                sequence_no=index + 1,
            ),
            package_type="RESULT_SUBMISSION",
            processed_at="2026-08-02T00:00:00Z",
            result="committed",
            revision=f"PRJ001-R{index + 1:04d}",
        )
        for index in range(records)
    )
    return ProcessedPackageStore(
        _records=entries,
        _by_id=tuple((e.package.package_id, i) for i, e in enumerate(entries)),
        _by_digest=tuple((e.package.package_digest, i) for i, e in enumerate(entries)),
    )


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
    results.append(_cockpit_http_probe())

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

    # ---- scalability probes (2026-08-02 optimization slice) ----
    baseline = _dag_probe()
    graph = build_dependency_graph_from_baseline(baseline)

    def dag_build() -> None:
        build_dependency_graph_from_baseline(baseline)

    results.append(
        measure(
            "dag_toposort",
            "large DAG build + topological sort (3k tasks / 30 packages)",
            dag_build,
            limit=5.0,
            unit="seconds",
            samples=1,
        )
    )

    def adjacency_lookups() -> None:
        for task_id in graph.task_ids:
            graph.predecessors(task_id)
            graph.successors(task_id)

    results.append(
        measure(
            "graph_lookup",
            "3k x (predecessors+successors) adjacency lookups",
            adjacency_lookups,
            limit=1.0,
            unit="seconds",
            samples=1,
        )
    )

    def talent_probe() -> None:
        from src.coevo.talent.models import AvailabilityWindow, SkillTag, Talent, TalentPool, RedactedIdentity
        from src.coevo.talent.recommender import TaskRequirement, recommend

        pool = TalentPool(
            pool_code="pool.big",
            schema_version="1.0",
            talents=tuple(
                Talent(
                    talent_code=f"t.{index:03d}",
                    skill_tags=(
                        SkillTag(f"tech:skill_{index % 20}"),
                        SkillTag(f"domain:domain_{index % 5}"),
                    ),
                    credentials=("cert.pmp",),
                    current_task_count=index % 5,
                    max_parallel_tasks=8,
                    availability=AvailabilityWindow("2026-08-01T00:00:00Z", "2026-09-30T00:00:00Z"),
                    redacted_identity=RedactedIdentity("pool.big", f"h{index:03d}", "0" * 64),
                )
                for index in range(200)
            ),
        )
        requirements = tuple(
            TaskRequirement(
                task_type=f"slot.{slot}",
                required_skill_tags=(f"tech:skill_{slot % 20}",),
                required_credentials=(),
                window=AvailabilityWindow("2026-08-10T00:00:00Z", "2026-08-20T00:00:00Z"),
            )
            for slot in range(50)
        )
        recommend(pool, requirements, limit=5)

    results.append(
        measure(
            "talent_recommend",
            "200 talents x 50 task slots (hoisted scoring)",
            talent_probe,
            limit=5.0,
            unit="seconds",
            samples=1,
        )
    )

    def registry_probe() -> None:
        store = _registry_probe()
        for index in range(20_000):
            store.get(f"pkg.{index:06d}")
            store.by_digest(f"{index:064x}")

    results.append(
        measure(
            "registry_lookup",
            "20k processed-package get/by_digest lookups",
            registry_probe,
            limit=1.0,
            unit="seconds",
            samples=1,
        )
    )

    def flow_json_probe() -> None:
        from src.coevo.task_decomposition.agent import _flow_json
        from src.coevo.task_flow.service import FlowUnderstandingService

        raw = {
            "format": "canonical",
            "flow": {
                "unit_id": "unit.bench",
                "title": "bench flow",
                "stages": [
                    {
                        "stage_id": f"s{stage}",
                        "name": f"stage {stage}",
                        "nodes": [
                            {
                                "node_id": f"n{stage}.{node}",
                                "title": f"task {stage}.{node}",
                                "stage_hint": "intake",
                                "inputs": ["doc"],
                                "outputs": ["out"],
                                "review_criteria": ["complete"],
                                "responsible_roles": ["a.role"],
                            }
                            for node in range(25)
                        ],
                    }
                    for stage in range(40)
                ],
                "roles": [
                    {"role_id": "a.role", "name": "PM", "responsibility": "Owns intake"}
                ],
            },
        }
        understanding = FlowUnderstandingService().understand(raw)
        _flow_json(understanding)

    results.append(
        measure(
            "flow_json_group",
            "flow JSON grouping (1k nodes / 40 stages, pre-indexed)",
            flow_json_probe,
            limit=1.0,
            unit="seconds",
            samples=1,
        )
    )

    def audit_stream_probe() -> None:
        from src.coevo.audit_governance import (
            AuditEvent,
            AuditEventResult,
            AuditEventSource,
            AuditStreamStore,
        )

        with tempfile.TemporaryDirectory() as tmp:
            store = AuditStreamStore.create(Path(tmp) / "stream.jsonl")
            try:
                for index in range(500):
                    store.append(
                        AuditEvent(
                            ts="2026-08-06T00:00:00Z",
                            actor="u.bench",
                            source=AuditEventSource.IMPORT,
                            action=f"a{index}",
                            project_id="PRJ001",
                            task_id="t.1",
                            result=AuditEventResult.OK,
                            tool="benchmark",
                        )
                    )
            finally:
                store.close()

    results.append(
        measure(
            "audit_stream_append",
            "500 audit stream appends (size tracked incrementally)",
            audit_stream_probe,
            limit=1.0,
            unit="seconds",
            samples=1,
        )
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for index in range(200):
            (root / f"doc-{index}.md").write_text(f"content {index}", encoding="utf-8")
        watcher = _watcher_scan(root)
        watcher()  # warm the snapshot + digests
        results.append(
            measure(
                "watcher_rescan",
                "rescan of 200 unchanged files (incremental digest reuse)",
                watcher,
                limit=1.0,
                unit="seconds",
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


def build_dependency_graph_from_baseline(baseline):
    """Rebuild the DependencyGraph object from a baseline's packages."""
    from src.coevo.task_decomposition.dependency_graph import build_dependency_graph

    return build_dependency_graph(baseline.work_packages, explicit_edges=baseline.dependencies)


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
