"""benchmarks.models - SLA target definitions and scalability probes (merged from the former package __init__)."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class SlaTarget:
    """One reference-architecture SLA target."""

    name: str
    metric: str
    limit_value: float
    unit: str
    comparison: str

SLA_TARGETS: tuple[SlaTarget, ...] = (
    SlaTarget("page_open", "project view dispatch", 3.0, "seconds", "le"),
    SlaTarget("task_query", "task view dispatch", 2.0, "seconds", "le"),
    SlaTarget("package_check", "small package wire parse", 10.0, "seconds", "le"),
    SlaTarget("dir_discovery", "watcher scan", 5.0, "seconds", "le"),
    SlaTarget("package_generation", "encrypted package build success rate", 95.0, "percent", "ge"),
)

SCALABILITY_PROBES: tuple[SlaTarget, ...] = (
    SlaTarget("dag_toposort", "large DAG build + topological sort", 5.0, "seconds", "le"),
    SlaTarget("graph_lookup", "adjacency lookups on a 3k-task DAG", 1.0, "seconds", "le"),
    SlaTarget("watcher_rescan", "rescan of 200 unchanged files", 1.0, "seconds", "le"),
    SlaTarget("talent_recommend", "200 talents x 50 task slots", 5.0, "seconds", "le"),
    SlaTarget("registry_lookup", "20k processed-package get/by_digest", 1.0, "seconds", "le"),
    SlaTarget("flow_json_group", "flow JSON grouping (1k nodes / 40 stages)", 1.0, "seconds", "le"),
    SlaTarget("audit_stream_append", "500 audit stream appends", 1.0, "seconds", "le"),
)
