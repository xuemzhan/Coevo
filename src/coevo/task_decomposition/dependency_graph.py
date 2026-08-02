"""US-2 deterministic dependency-graph builder (US-2-AC-1 / AC-5).

The dependency graph is a directed acyclic graph over task IDs. US-2
AC-5 requires "automatic identification of predecessor/successor and
input/output relationships"; this module ships the deterministic half
of that AC. The LLM half (which would propose candidate edges from
the process flow's natural-language descriptions) is a separate
slice.

Algorithm
---------
* Build a node set from all task IDs in the baseline.
* Add every :class:`DependencyEdge` as a directed edge.
* Also seed edges from the underlying :class:`StageGraph`: every
  task in stage ``S_i`` is preceded by every task in stage
  ``S_{i-1}``. This is the deterministic fallback when the caller
  has not provided explicit edges yet.
* Detect cycles using iterative DFS with a permanent / temporary mark
  (CLRS, ch. 20). Raise :class:`TaskDecompositionValidationError`
  with the offending component if a cycle is found. The traversal is
  iterative (explicit stack) so very large graphs never hit Python's
  recursion limit.
* Compute a stable topological order via Kahn's algorithm using a
  binary heap for the ready set (lexical tie-breaking on task IDs),
  which is deterministic across calls and runs in
  ``O((V + E) log V)`` instead of the previous quadratic
  ``list.pop(0)`` + re-sort per insertion.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Iterable

from .models import (
    DependencyEdge,
    TaskDecompositionValidationError,
    WorkPackage,
)


@dataclass(frozen=True)
class DependencyGraph:
    """A directed acyclic graph over task IDs."""

    task_ids: tuple[str, ...]
    edges: tuple[DependencyEdge, ...]
    topo_order: tuple[str, ...]

    def __post_init__(self) -> None:
        # Build O(1) adjacency indexes once. The index fields are
        # private and deliberately excluded from equality / hashing
        # (dataclass only considers declared fields).
        successors: dict[str, list[str]] = {}
        predecessors: dict[str, list[str]] = {}
        for edge in self.edges:
            successors.setdefault(edge.predecessor_task_id, []).append(
                edge.successor_task_id
            )
            predecessors.setdefault(edge.successor_task_id, []).append(
                edge.predecessor_task_id
            )
        object.__setattr__(
            self,
            "_successor_index",
            {key: tuple(value) for key, value in successors.items()},
        )
        object.__setattr__(
            self,
            "_predecessor_index",
            {key: tuple(value) for key, value in predecessors.items()},
        )

    def predecessors(self, task_id: str) -> tuple[str, ...]:
        """Return predecessor task IDs of ``task_id`` (O(1) lookup)."""
        return self._predecessor_index.get(task_id, ())

    def successors(self, task_id: str) -> tuple[str, ...]:
        """Return successor task IDs of ``task_id`` (O(1) lookup)."""
        return self._successor_index.get(task_id, ())


def cycle_in_components(edges: Iterable[DependencyEdge]) -> list[DependencyEdge]:
    """Return the edges that participate in at least one cycle.

    The search uses DFS with white / gray / black marks; edges that
    reach a gray node are the back edges. The returned list is
    deterministic (sorted by ``(predecessor, successor)``). The
    traversal is iterative (explicit stack) so graph size is not
    bounded by the interpreter recursion limit.
    """
    adj: dict[str, list[str]] = {}
    edge_by_pair: dict[tuple[str, str], DependencyEdge] = {}
    for e in edges:
        adj.setdefault(e.predecessor_task_id, []).append(e.successor_task_id)
        edge_by_pair[(e.predecessor_task_id, e.successor_task_id)] = e
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in adj}
    cycle_pairs: set[tuple[str, str]] = set()

    for node in sorted(adj):
        if color[node] == WHITE:
            color[node] = GRAY
            # Explicit stack of (node, iterator over its adjacency).
            # The iterator retains its position across the child's
            # sub-traversal, giving the exact DFS semantics of the
            # recursive formulation without recursion.
            stack: list[tuple[str, object]] = [(node, iter(adj.get(node, ())))]
            while stack:
                current, adjacency = stack[-1]
                descended = False
                for nxt in adjacency:  # type: ignore[union-attr]
                    mark = color.get(nxt, WHITE)
                    if mark == GRAY:
                        cycle_pairs.add((current, nxt))
                    elif mark == WHITE:
                        color[nxt] = GRAY
                        stack.append((nxt, iter(adj.get(nxt, ()))))
                        descended = True
                        break
                if not descended:
                    color[current] = BLACK
                    stack.pop()

    return [edge_by_pair[p] for p in sorted(cycle_pairs)]


def topological_order(
    task_ids: Iterable[str],
    edges: Iterable[DependencyEdge],
) -> tuple[str, ...]:
    """Return a deterministic topological order over ``task_ids``.

    Uses Kahn's algorithm with lexical tie-breaking on task IDs so
    the order is stable across calls. The ready set is maintained in
    a binary heap, giving ``O((V + E) log V)`` overall. Raises
    :class:`TaskDecompositionValidationError` if a cycle is detected.
    """
    nodes = sorted(set(task_ids))
    node_set = set(nodes)
    succ: dict[str, list[str]] = {n: [] for n in nodes}
    pred_count: dict[str, int] = {n: 0 for n in nodes}
    edge_pairs: set[tuple[str, str]] = set()
    for e in edges:
        # ``node_set`` (not the sorted list) is used here: an ``in``
        # test against the list would be O(V) per edge and make the
        # whole pass O(V * E) on large DAGs.
        if (
            e.predecessor_task_id not in node_set
            or e.successor_task_id not in node_set
        ):
            raise TaskDecompositionValidationError(
                f"edge references unknown task: ({e.predecessor_task_id!r}, "
                f"{e.successor_task_id!r})"
            )
        key = (e.predecessor_task_id, e.successor_task_id)
        if key in edge_pairs:
            raise TaskDecompositionValidationError(
                f"duplicate edge {key!r}"
            )
        edge_pairs.add(key)
        succ[e.predecessor_task_id].append(e.successor_task_id)
        pred_count[e.successor_task_id] += 1

    # Deterministic adjacency lists
    for k in succ:
        succ[k] = sorted(set(succ[k]))

    ready: list[str] = sorted(n for n, c in pred_count.items() if c == 0)
    heapq.heapify(ready)
    out: list[str] = []
    while ready:
        node = heapq.heappop(ready)
        out.append(node)
        for nxt in succ[node]:
            pred_count[nxt] -= 1
            if pred_count[nxt] == 0:
                heapq.heappush(ready, nxt)
    if len(out) != len(nodes):
        cyclic = cycle_in_components(
            DependencyEdge(p, s, "fs") for p, s in edge_pairs
        )
        raise TaskDecompositionValidationError(
            f"dependency graph has a cycle; offending edges: "
            f"{[ (e.predecessor_task_id, e.successor_task_id) for e in cyclic ]!r}"
        )
    return tuple(out)


def build_dependency_graph(
    work_packages: Iterable[WorkPackage],
    explicit_edges: Iterable[DependencyEdge] | None = None,
) -> DependencyGraph:
    """Build a :class:`DependencyGraph` from work packages.

    Stage-order edges are seeded from the order in which work packages
    appear in ``work_packages`` (the caller is responsible for
    preserving that order — US-1's :class:`StageGraph.stage_ids_in_order`
    is the canonical source).

    If ``explicit_edges`` is supplied, those edges are added on top
    of the stage-order seeds. Duplicate edges are de-duplicated; the
    graph builder refuses to add an edge whose endpoints are not
    known task IDs.
    """
    packages = list(work_packages)
    if not packages:
        raise TaskDecompositionValidationError("work_packages must be non-empty")

    task_to_pkg: dict[str, str] = {}
    pkg_to_tasks: dict[str, list[str]] = {}
    for wp in packages:
        ids = [t.task_id for t in wp.tasks]
        for tid in ids:
            if tid in task_to_pkg:
                raise TaskDecompositionValidationError(
                    f"task_id {tid!r} appears in multiple work packages"
                )
            task_to_pkg[tid] = wp.work_package_id
        pkg_to_tasks[wp.work_package_id] = ids

    edges: list[DependencyEdge] = []

    # Stage-order seeds: every task in package i precedes every task in
    # package i+1.
    pkg_order = [wp.work_package_id for wp in packages]
    for i in range(len(pkg_order) - 1):
        a_tasks = pkg_to_tasks[pkg_order[i]]
        b_tasks = pkg_to_tasks[pkg_order[i + 1]]
        for a in a_tasks:
            for b in b_tasks:
                edges.append(DependencyEdge(a, b, "fs"))

    # Explicit edges (caller-supplied)
    if explicit_edges is not None:
        for e in explicit_edges:
            if e.predecessor_task_id not in task_to_pkg:
                raise TaskDecompositionValidationError(
                    f"edge predecessor {e.predecessor_task_id!r} not in any work package"
                )
            if e.successor_task_id not in task_to_pkg:
                raise TaskDecompositionValidationError(
                    f"edge successor {e.successor_task_id!r} not in any work package"
                )
            edges.append(e)

    # De-duplicate while preserving insertion order
    seen: set[tuple[str, str]] = set()
    deduped: list[DependencyEdge] = []
    for e in edges:
        key = (e.predecessor_task_id, e.successor_task_id)
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    topo = topological_order(set(task_to_pkg), deduped)
    return DependencyGraph(
        task_ids=tuple(sorted(task_to_pkg)),
        edges=tuple(deduped),
        topo_order=topo,
    )
