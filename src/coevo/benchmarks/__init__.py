"""Offline performance benchmark suite (MVP reference architecture 14).

Establishes reproducible, offline measurements for the reference SLA
targets so the project stops guessing and starts tracking:

* page open / project view       <= 3s
* local task query               <= 2s
* small package baseline check   <= 10s
* directory file discovery       <= 5s
* package generation success     >= 95%

The harness is pure and small; the actual measurements live in
``scripts/benchmark.py`` so they are not part of the quality gate
(timing runs are environment-dependent and must not gate CI).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class SlaTarget:
    """One reference-architecture SLA target."""

    name: str
    metric: str
    limit_value: float
    unit: str
    comparison: str  # "le" (<=) or "ge" (>=)


SLA_TARGETS: tuple[SlaTarget, ...] = (
    SlaTarget("page_open", "project view dispatch", 3.0, "seconds", "le"),
    SlaTarget("task_query", "task view dispatch", 2.0, "seconds", "le"),
    SlaTarget("package_check", "small package wire parse", 10.0, "seconds", "le"),
    SlaTarget("dir_discovery", "watcher scan", 5.0, "seconds", "le"),
    SlaTarget("package_generation", "encrypted package build success rate", 95.0, "percent", "ge"),
)


# Scalability probes (2026-08-02 optimization slice)
# ---------------------------------------------------
# These are NOT reference-architecture SLA targets; they are
# reproducible probes for the algorithmic hot paths added during the
# performance review (large DAG construction + topological sort,
# O(1) adjacency lookups, incremental watcher rescan, hoisted talent
# scoring, and cached registry lookups). They live in the same harness
# so regressions in asymptotic behaviour are visible in the report.
SCALABILITY_PROBES: tuple[SlaTarget, ...] = (
    SlaTarget("dag_toposort", "large DAG build + topological sort", 5.0, "seconds", "le"),
    SlaTarget("graph_lookup", "adjacency lookups on a 3k-task DAG", 1.0, "seconds", "le"),
    SlaTarget("watcher_rescan", "rescan of 200 unchanged files", 1.0, "seconds", "le"),
    SlaTarget("talent_recommend", "200 talents x 50 task slots", 5.0, "seconds", "le"),
    SlaTarget("registry_lookup", "20k processed-package get/by_digest", 1.0, "seconds", "le"),
)


@dataclass(frozen=True)
class BenchmarkResult:
    """A single measured result against its SLA target."""

    name: str
    metric: str
    value: float
    unit: str
    limit: float
    comparison: str
    ok: bool
    samples: int
    detail: str = ""

    def to_mapping(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "limit": self.limit,
            "comparison": self.comparison,
            "ok": self.ok,
            "samples": self.samples,
            "detail": self.detail,
        }


def measure(
    name: str,
    metric: str,
    fn: Callable[[], Any],
    *,
    limit: float,
    unit: str,
    comparison: str = "le",
    samples: int = 1,
) -> BenchmarkResult:
    """Time ``fn`` (optionally repeated) and compare against the limit."""
    if not callable(fn):
        raise TypeError("fn must be callable")
    if not isinstance(samples, int) or samples < 1:
        raise ValueError("samples must be a positive integer")
    if not isinstance(limit, (int, float)) or limit <= 0:
        raise ValueError("limit must be positive")
    if comparison not in {"le", "ge"}:
        raise ValueError("comparison must be 'le' or 'ge'")
    start = time.perf_counter()
    outcome: Any = None
    for _ in range(samples):
        outcome = fn()
    elapsed = time.perf_counter() - start
    value = elapsed / samples if comparison == "le" else float(outcome)
    ok = value <= limit if comparison == "le" else value >= limit
    return BenchmarkResult(
        name=name,
        metric=metric,
        value=round(value, 4),
        unit=unit,
        limit=limit,
        comparison=comparison,
        ok=ok,
        samples=samples,
    )


def report(results: tuple[BenchmarkResult, ...]) -> dict[str, Any]:
    """JSON-safe report for the record."""
    if not results:
        raise ValueError("report requires at least one result")
    return {
        "schema_version": "1.0",
        "all_ok": all(result.ok for result in results),
        "results": [result.to_mapping() for result in results],
    }
