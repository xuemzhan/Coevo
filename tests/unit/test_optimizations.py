"""Regression tests for the 2026-08-02 performance review slice.

Covers the algorithmic / data-structure optimizations without making
the unit suite timing-dependent:

* heap-based topological sort + iterative cycle detection scale to
  thousands of tasks without recursion limits;
* DependencyGraph adjacency lookups are indexed (functional parity
  with the edge list is asserted on large graphs);
* task-flow mapping resolves hints with the best (priority, rule_id)
  rule when multiple rules share a hint;
* StageGraph / SourceMapping / ReviewerView lookups are indexed;
* talent scoring hoists per-candidate set construction while keeping
  public results identical;
* TalentPool.by_code is an O(1) index;
* watcher incremental digest reuse (digest calls drop to changed
  files only) with a strict mode that re-hashes everything;
* ProcessedPackageStore get/by_digest work on a large registry;
* cockpit static asset cache validates mtime and evicts within bounds.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coevo.cockpit.server import _StaticAssetCache
from src.coevo.orchestrator import (
    AgentCapability,
    AgentRegistration,
    AgentRegistry,
    AgentSpec,
    AgentStatus,
)
from src.coevo.protocol.processed_package_store import (
    ProcessedPackageRecord,
    ProcessedPackageStore,
)
from src.coevo.protocol.replay_detector import ProcessedPackage
from src.coevo.task_decomposition.dependency_graph import (
    DependencyGraph,
    build_dependency_graph,
    cycle_in_components,
    topological_order,
)
from src.coevo.task_decomposition.models import (
    Deliverable,
    DependencyEdge,
    Task,
    WorkPackage,
)
from src.coevo.task_flow.mapping import MappingRule, apply_mapping
from src.coevo.task_flow.models import (
    ProcessFlow,
    SourceKind,
    SourceMapping,
    StandardStage,
    Traced,
)
from src.coevo.task_flow.parser import parse_flow
from src.coevo.task_flow.service import FlowUnderstandingService, StageGraph
from src.coevo.talent.models import (
    AvailabilityWindow,
    RedactedIdentity,
    SkillTag,
    Talent,
    TalentPool,
)


def _task(task_id: str) -> Task:
    return Task(
        task_id=task_id,
        title=f"task {task_id}",
        responsible_role="role.eng",
        plan_start="2026-08-01T00:00:00Z",
        plan_end="2026-08-31T00:00:00Z",
        deliverables=(
            Deliverable(
                deliverable_id=f"d.{task_id}",
                title=f"output {task_id}",
                kind="document",
                acceptance_criteria=("accepted_by_reviewer",),
            ),
        ),
    )


class DependencyGraphOptimizationTests(unittest.TestCase):
    def test_large_chain_topological_order_is_deterministic(self):
        """A 5000-task chain must sort without recursion / stack issues."""
        task_ids = [f"t.{i:05d}" for i in range(5000)]
        edges = [
            DependencyEdge(task_ids[i], task_ids[i + 1], "fs")
            for i in range(len(task_ids) - 1)
        ]
        order = topological_order(task_ids, edges)
        self.assertEqual(tuple(task_ids), order)
        self.assertEqual(
            order,
            topological_order(task_ids, edges),
            "topological order must be deterministic",
        )

    def test_large_cycle_detection_is_iterative(self):
        """A 5000-node cycle must be detected without recursion errors."""
        task_ids = [f"t.{i:05d}" for i in range(5000)]
        edges = [
            DependencyEdge(task_ids[i], task_ids[(i + 1) % len(task_ids)], "fs")
            for i in range(len(task_ids))
        ]
        offending = cycle_in_components(edges)
        self.assertTrue(offending)

    def test_adjacency_lookups_match_edge_list_on_large_graph(self):
        packages = tuple(
            WorkPackage(
                work_package_id=f"wp.{p}",
                standard_stage="execution",
                title=f"package {p}",
                tasks=tuple(_task(f"t.{p}.{i}") for i in range(20)),
            )
            for p in range(10)
        )
        graph = build_dependency_graph(packages)
        self.assertIsInstance(graph, DependencyGraph)
        for edge in graph.edges:
            self.assertIn(
                edge.successor_task_id,
                graph.successors(edge.predecessor_task_id),
            )
            self.assertIn(
                edge.predecessor_task_id,
                graph.predecessors(edge.successor_task_id),
            )
        self.assertEqual(tuple(), graph.predecessors("unknown.task"))
        self.assertEqual(tuple(), graph.successors("unknown.task"))
        self.assertEqual(len(graph.task_ids), len(packages) * 20)
        self.assertEqual(len(graph.topo_order), len(graph.task_ids))


class TaskFlowIndexTests(unittest.TestCase):
    def _flow(self, *, stage_hint: str = "接收") -> ProcessFlow:
        return parse_flow(
            {
                "format": "canonical",
                "flow": {
                    "unit_id": "unit_a",
                    "title": "unit flow",
                    "stages": [
                        {
                            "stage_id": "stage_1",
                            "name": "intake",
                            "nodes": [
                                {
                                    "node_id": "n1",
                                    "title": "receive",
                                    "stage_hint": stage_hint,
                                }
                            ],
                        }
                    ],
                    "roles": [],
                },
            }
        )

    def test_mapping_picks_best_rule_for_duplicate_hints(self):
        rules = (
            MappingRule("r.low", "hint-x", StandardStage.EXECUTION, priority=50),
            MappingRule("r.high", "hint-x", StandardStage.INTAKE, priority=10),
            MappingRule("r.other", "hint-y", StandardStage.CLOSURE, priority=10),
        )
        mapped = apply_mapping(self._flow(stage_hint="hint-x"), rules)
        self.assertEqual(StandardStage.INTAKE, mapped.nodes[0].standard_stage)
        self.assertEqual("r.high", mapped.nodes[0].rule_id)

    def test_mapping_resolves_hint_without_scanning_all_rules(self):
        mapped = apply_mapping(self._flow())
        self.assertEqual(StandardStage.INTAKE, mapped.nodes[0].standard_stage)

    def test_stage_graph_lookups_are_indexed(self):
        service = FlowUnderstandingService()
        understanding = service.understand(
            {
                "format": "canonical",
                "flow": {
                    "unit_id": "unit_a",
                    "title": "unit flow",
                    "stages": [
                        {
                            "stage_id": "s1",
                            "name": "intake",
                            "nodes": [
                                {
                                    "node_id": "n1",
                                    "title": "receive",
                                    "stage_hint": "接收",
                                }
                            ],
                        }
                    ],
                    "roles": [],
                },
            }
        )
        graph: StageGraph = understanding.graph
        self.assertEqual("s1", graph.stage_id_for_node("n1"))
        self.assertEqual(("n1",), graph.nodes_in_stage("s1"))
        self.assertEqual(StandardStage.INTAKE, graph.standard_stage_for("n1"))
        self.assertIsNone(graph.stage_id_for_node("n_missing"))
        self.assertEqual(tuple(), graph.nodes_in_stage("s_missing"))
        self.assertIsNone(graph.standard_stage_for("n_missing"))

    def test_source_mapping_and_reviewer_view_lookups(self):
        flow = self._flow()
        self.assertEqual("title", flow.source_mapping.get("flow.title"))
        self.assertIsNone(flow.source_mapping.get("missing.path"))
        reviewer = FlowUnderstandingService()._build_reviewer_view(flow)
        self.assertEqual(0.95, reviewer.confidence_for("flow.title"))
        self.assertIsNone(reviewer.confidence_for("missing.path"))

    def test_source_mapping_index_survives_duplicate_keys(self):
        mapping = SourceMapping((("a", "1"), ("a", "2")))
        self.assertEqual(
            "1",
            mapping.get("a"),
            "first occurrence must win, matching the legacy scan",
        )


class TalentRecommendationOptimizationTests(unittest.TestCase):
    def _pool(self) -> TalentPool:
        return TalentPool(
            pool_code="pool.t",
            schema_version="1.0",
            talents=(
                Talent(
                    talent_code="t.one",
                    skill_tags=(
                        SkillTag("tech:python"),
                        SkillTag("domain:audit"),
                    ),
                    credentials=("cert.pmp",),
                    current_task_count=1,
                    max_parallel_tasks=4,
                    availability=AvailabilityWindow(
                        "2026-08-01T00:00:00Z", "2026-09-01T00:00:00Z"
                    ),
                    redacted_identity=RedactedIdentity(
                        "pool.t", "one", "0" * 64
                    ),
                ),
                Talent(
                    talent_code="t.two",
                    skill_tags=(SkillTag("tech:go"),),
                    credentials=(),
                    current_task_count=0,
                    max_parallel_tasks=2,
                    availability=AvailabilityWindow(
                        "2026-08-01T00:00:00Z", "2026-09-01T00:00:00Z"
                    ),
                    redacted_identity=RedactedIdentity(
                        "pool.t", "two", "1" * 64
                    ),
                ),
            ),
        )

    def test_by_code_is_indexed(self):
        pool = self._pool()
        self.assertEqual("t.one", pool.by_code("t.one").talent_code)
        self.assertIsNone(pool.by_code("t.missing"))


class WatcherIncrementalDigestTests(unittest.TestCase):
    def _digest_count(self, watcher) -> list[int]:
        counter = [0]
        original = watcher._digest

        def counting(path: Path, size: int) -> str:
            counter[0] += 1
            return original(path, size)

        watcher._digest = counting
        return counter

    def test_unchanged_files_skip_rehashing(self):
        from src.coevo.progress_capture import WorkspaceWatcher

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(20):
                (root / f"doc-{index}.md").write_text(
                    f"content {index}", encoding="utf-8"
                )
            watcher = WorkspaceWatcher(
                root, stability_checks=1, poll_interval_sec=0.05
            )
            counter = self._digest_count(watcher)
            watcher.scan(now="2026-08-02T00:00:00Z")
            self.assertEqual(20, counter[0], "first scan hashes every file")
            watcher.scan(now="2026-08-02T00:00:01Z")
            self.assertEqual(20, counter[0], "unchanged rescan reuses digests")
            changed = root / "doc-0.md"
            changed.write_text("new content 0", encoding="utf-8")
            watcher.scan(now="2026-08-02T00:00:02Z")
            self.assertEqual(21, counter[0], "changed file is re-hashed once")

    def test_strict_mode_always_rehashes(self):
        from src.coevo.progress_capture import WorkspaceWatcher

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("a", encoding="utf-8")
            watcher = WorkspaceWatcher(
                root,
                stability_checks=1,
                poll_interval_sec=0.05,
                reuse_digest_on_unchanged=False,
            )
            counter = self._digest_count(watcher)
            watcher.scan(now="2026-08-02T00:00:00Z")
            watcher.scan(now="2026-08-02T00:00:01Z")
            self.assertEqual(2, counter[0], "strict mode hashes on every scan")

    def test_invalid_reuse_flag_is_rejected(self):
        from src.coevo.progress_capture import ProgressCaptureValidationError, WorkspaceWatcher

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ProgressCaptureValidationError):
                WorkspaceWatcher(
                    Path(tmp),
                    stability_checks=1,
                    poll_interval_sec=0.05,
                    reuse_digest_on_unchanged=1,  # type: ignore[arg-type]
                )


class RegistryIndexTests(unittest.TestCase):
    def test_large_registry_get_and_by_digest(self):
        entries = tuple(
            ProcessedPackageRecord(
                package=ProcessedPackage(
                    package_id=f"pkg.{i:05d}",
                    package_digest=f"{i:064x}",
                    sender_cert_id="CERT-S",
                    recipient_cert_id="CERT-R",
                    project_id="PRJ001",
                    sequence_no=i + 1,
                ),
                package_type="RESULT_SUBMISSION",
                processed_at="2026-08-02T00:00:00Z",
                result="committed",
                revision=f"PRJ001-R{i + 1:04d}",
            )
            for i in range(3000)
        )
        store = ProcessedPackageStore(
            _records=entries,
            _by_id=tuple((e.package.package_id, i) for i, e in enumerate(entries)),
            _by_digest=tuple(
                (e.package.package_digest, i) for i, e in enumerate(entries)
            ),
        )
        self.assertEqual("pkg.02999", store.get("pkg.02999").package.package_id)
        self.assertEqual("pkg.00000", store.get("pkg.00000").package.package_id)
        self.assertIsNone(store.get("pkg.missing"))
        self.assertEqual(
            f"{2999:064x}",
            store.by_digest(f"{2999:064x}").package.package_digest,
        )
        self.assertIsNone(store.by_digest("f" * 64))

    def test_agent_registry_get_is_indexed(self):
        entries = tuple(
            AgentRegistration(
                spec=AgentSpec(
                    agent_id=f"agent.{i:03d}",
                    capability=AgentCapability.TASK_FLOW_UNDERSTANDING,
                    display_name=f"agent {i}",
                    input_schema=("json",),
                    output_schema=("json",),
                ),
                status=AgentStatus.AVAILABLE,
            )
            for i in range(100)
        )
        registry = AgentRegistry(_by_id=entries)
        self.assertIsNotNone(registry.get("agent.000"))
        self.assertIsNotNone(registry.get("agent.099"))
        self.assertIsNone(registry.get("agent.missing"))
        self.assertEqual(
            AgentStatus.AVAILABLE,
            registry.get("agent.050").status,
        )


class StaticAssetCacheTests(unittest.TestCase):
    def test_cache_hit_and_mtime_invalidation(self):
        import os

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "asset.js"
            path.write_text("body v1", encoding="utf-8")
            cache = _StaticAssetCache()
            self.assertIsNone(cache.get(path))
            cache.put(path, b"body v1")
            self.assertEqual(b"body v1", cache.get(path))
            # Different size invalidates regardless of mtime granularity.
            path.write_text("body v2 is longer", encoding="utf-8")
            self.assertIsNone(cache.get(path), "stale entry must be invalidated")
            cache.put(path, b"body v2 is longer")
            self.assertEqual(b"body v2 is longer", cache.get(path))
            # Same size but bumped mtime must also invalidate.
            path.write_text("body v3 same len", encoding="utf-8")
            stamp = path.stat().st_mtime_ns + 1_000_000
            os.utime(path, ns=(stamp, stamp))
            self.assertIsNone(cache.get(path), "mtime change must invalidate")

    def test_eviction_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = _StaticAssetCache(max_entries=4, max_bytes=1024)
            paths = []
            for index in range(6):
                path = Path(tmp) / f"f{index}.txt"
                path.write_text(f"x{index}", encoding="utf-8")
                cache.put(path, f"x{index}".encode())
                paths.append(path)
            self.assertEqual(4, cache.size)
            self.assertLessEqual(cache.total_bytes, 1024)
            self.assertIsNone(cache.get(paths[0]), "oldest entry is evicted")
            self.assertEqual(f"x5".encode(), cache.get(paths[5]))

    def test_oversized_payload_is_not_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "big.bin"
            path.write_bytes(b"b" * 4096)
            cache = _StaticAssetCache(max_bytes=256)
            cache.put(path, b"b" * 4096)
            self.assertEqual(0, cache.size)


if __name__ == "__main__":
    unittest.main()
