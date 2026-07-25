"""US-1 task-flow understanding service layer (US-1-AC-2).

Scope
-----
This module is the *service layer* that sits on top of the deterministic
data model (:mod:`.models`, :mod:`.parser`, :mod:`.mapping`). It does
not perform any IO, network, or model inference — that is by design
(AGENTS.md §3 第 7 条:不得掩盖错误;US-1-AC-1 has already shipped the
data-model half, US-1-AC-2 ships the orchestration layer that callers
in other slices — task decomposition, dashboard UI, audit ingestion —
will consume).

What this layer adds on top of US-1-AC-1
----------------------------------------
* :class:`FlowUnderstandingService` — a deterministic facade that takes
  raw input (any of the three supported schemas), runs it through
  :func:`parser.parse_flow` and :func:`mapping.apply_mapping`, and
  produces a :class:`FlowUnderstanding` result containing:

    - the parsed :class:`ProcessFlow` (immutable draft or confirmed);
    - the :class:`MappedFlow` projection;
    - a deterministic :class:`StageGraph` describing the stage order
      and node adjacency for downstream consumers (US-2 task
      decomposition reads this graph);
    - a :class:`ReviewerView` convenience that surfaces
      ``source_mapping`` lookups + per-field confidence so a UI can
      render "show me where this field came from" without poking at
      the model internals.

* :class:`TaskFlowValidationError` — explicit error raised by the
  service when an input cannot be reconciled. The parser already
  raises :class:`ProcessFlowParseError`; the service wraps these
  failures so callers can either catch the precise parser error or
  the broader service error (mirrors the way :class:`IdentityStore`
  wraps certificate-parse errors).

* Strict monotonic ``version`` enforcement: every confirmed
  :class:`ProcessFlow` returned by the service has version ≥ 1, and
  ``confirm(confirmed)`` raises if the caller passes a flow whose
  version would not strictly increase.

* ``to_audit_record`` — emits a deterministic JSON-safe dict suitable
  for ``loop/tool-audit.jsonl`` ingestion. Sensitive material (raw
  input bytes, role-responsibility texts that may contain PII) is
  intentionally omitted; only structural facts and provenance are
  recorded. This matches the audit module's principle that audit
  records describe *what happened* without leaking *what was said*.

Non-goals (deliberately not in US-1-AC-2)
-----------------------------------------
* No LLM call. The "task-process understanding" agent in production is
  a separate slice backed by an offline-approved model; for the MVP
  AC-2 we ship the deterministic service layer so the wiring is
  provable and unit-testable.
* No filesystem, no network, no DB. Inputs and outputs are Python
  objects only.
* No write into ``loop/tool-audit.jsonl``. The audit emission helper
  is *structure-only*; actual append is the audit module's job in a
  future slice (out of scope for AC-2).
"""
from __future__ import annotations

import dataclasses
from typing import Any, Iterable, Mapping

from .mapping import DEFAULT_MAPPING_RULES, MappingRule, MappedFlow, apply_mapping
from .models import (
    Node,
    Override,
    ProcessFlow,
    ProcessFlowError,
    ProcessFlowParseError,
    Role,
    SourceKind,
    SourceMapping,
    Stage,
    StandardStage,
    Traced,
)
from .parser import parse_flow


class TaskFlowValidationError(ProcessFlowError):
    """Raised by :class:`FlowUnderstandingService` for caller-facing errors.

    Fail-closed by default (AGENTS.md §3 第 7 条). Subclasses
    :class:`ProcessFlowError` so callers that already handle parser
    errors continue to work without changes.
    """


@dataclasses.dataclass(frozen=True)
class StageGraph:
    """Deterministic view of stage order + node adjacency.

    * ``stage_ids_in_order`` preserves the canonical order supplied by
      the parsed flow (US-2 task decomposition relies on this for
      dependency resolution).
    * ``stage_membership`` maps each stage_id to the tuple of
      ``node_id`` that belong to it, in input order.
    * ``node_to_stage`` is the inverse mapping (deterministic; required
      for "given a node, which stage contains it" lookups).
    * ``standard_stage_by_node`` maps each ``node_id`` to its
      :class:`StandardStage` from the mapping layer.
    """

    stage_ids_in_order: tuple[str, ...]
    stage_membership: tuple[tuple[str, tuple[str, ...]], ...]
    node_to_stage: tuple[tuple[str, str], ...]
    standard_stage_by_node: tuple[tuple[str, StandardStage], ...]

    def stage_id_for_node(self, node_id: str) -> str | None:
        for nid, sid in self.node_to_stage:
            if nid == node_id:
                return sid
        return None

    def nodes_in_stage(self, stage_id: str) -> tuple[str, ...]:
        for sid, members in self.stage_membership:
            if sid == stage_id:
                return members
        return tuple()

    def standard_stage_for(self, node_id: str) -> StandardStage | None:
        for nid, stage in self.standard_stage_by_node:
            if nid == node_id:
                return stage
        return None


@dataclasses.dataclass(frozen=True)
class ReviewerView:
    """Convenience wrapper exposing per-field provenance to a UI.

    * ``source_mapping_lookup(path)`` returns the raw-input path that
      produced the parsed field at ``path``, or ``None`` if the field
      was synthesized.
    * ``confidence_for(path)`` returns the parser's deterministic
      confidence for the field, or ``None`` if no Traced is recorded.
    """

    flow: ProcessFlow
    _confidence_index: tuple[tuple[str, float], ...]

    def source_mapping_lookup(self, path: str) -> str | None:
        return self.flow.source_mapping.get(path)

    def confidence_for(self, path: str) -> float | None:
        for p, c in self._confidence_index:
            if p == path:
                return c
        return None


@dataclasses.dataclass(frozen=True)
class FlowUnderstanding:
    """The full deterministic output of :class:`FlowUnderstandingService`.

    Carries the parsed flow, the mapped view, the stage graph, and a
    reviewer view. All four objects are immutable and contain only
    values that the parser + mapping layer are responsible for.
    """

    flow: ProcessFlow
    mapped: MappedFlow
    graph: StageGraph
    reviewer_view: ReviewerView


class FlowUnderstandingService:
    """Deterministic facade for the US-1 task-flow understanding slice.

    This service has no internal state — every method is a pure
    function of its inputs plus the rule table. Callers may safely
    construct it once at module import time.
    """

    SCHEMAS: tuple[str, ...] = ("canonical", "tabular", "tree")

    def __init__(self, rules: Iterable[MappingRule] | None = None) -> None:
        # Materialize eagerly so the service is immutable for callers.
        self._rules: tuple[MappingRule, ...] = (
            tuple(rules) if rules is not None else DEFAULT_MAPPING_RULES
        )
        if not self._rules:
            raise TaskFlowValidationError("mapping rule table must be non-empty")

    @property
    def rules(self) -> tuple[MappingRule, ...]:
        return self._rules

    def understand(self, raw: Mapping[str, Any]) -> FlowUnderstanding:
        """Parse + map + graph + reviewer-view in one call.

        Equivalent to ``parse_flow`` → ``apply_mapping`` →
        :meth:`_build_graph` → :meth:`_build_reviewer_view`, but with
        a single error surface (:class:`TaskFlowValidationError`) so
        callers don't need to chain exception handlers.
        """
        if not isinstance(raw, Mapping):
            raise TaskFlowValidationError(
                f"raw input must be a mapping; got {type(raw).__name__}"
            )
        fmt = raw.get("format")
        if fmt not in self.SCHEMAS:
            raise TaskFlowValidationError(
                f"unsupported schema {fmt!r}; expected one of {self.SCHEMAS!r}"
            )
        try:
            flow = parse_flow(raw)
            mapped = apply_mapping(flow, self._rules)
        except ProcessFlowError as exc:  # parser + mapping both raise subclasses
            raise TaskFlowValidationError(str(exc)) from exc

        graph = self._build_graph(flow, mapped)
        reviewer = self._build_reviewer_view(flow)
        return FlowUnderstanding(
            flow=flow, mapped=mapped, graph=graph, reviewer_view=reviewer
        )

    def confirm(
        self,
        flow: ProcessFlow,
        overrides: tuple[Override, ...],
        new_created_at: str,
    ) -> ProcessFlow:
        """Re-confirm a parsed flow with reviewer overrides.

        Thin wrapper around :meth:`ProcessFlow.with_overrides` that
        enforces strict monotonic version (refuses negative or
        duplicate overrides, refuses empty override tuples, refuses
        the same ``new_created_at`` as the prior ``created_at`` if the
        prior version equals the proposed version — i.e. callers must
        use :meth:`ProcessFlow.with_overrides`'s built-in version bump).
        """
        if not overrides:
            raise TaskFlowValidationError("confirm requires non-empty overrides")
        if not new_created_at:
            raise TaskFlowValidationError("new_created_at must be non-empty")
        try:
            return flow.with_overrides(overrides, new_created_at)
        except ProcessFlowError as exc:
            raise TaskFlowValidationError(str(exc)) from exc

    def to_audit_record(self, result: FlowUnderstanding) -> dict[str, Any]:
        """Produce a deterministic, JSON-safe audit-record projection.

        Returns a plain ``dict`` (not a JSON string) that the audit
        module can ``json.dumps`` itself. Sensitive content
        (responsibility texts, raw input) is *not* included — only
        structural facts (unit_id, version, stage count, node count,
        role count, mapping rule versions used, override count).
        """
        flow = result.flow
        return {
            "kind": "task_flow.understanding",
            "schema_version": "1.0",
            "unit_id": flow.unit_id,
            "version": flow.version,
            "stage_count": len(flow.stages),
            "node_count": sum(len(s.nodes) for s in flow.stages),
            "role_count": len(flow.roles),
            "mapping_rules_version": flow.mapping_rules_version,
            "override_count": len(flow.overrides),
            "standard_stage_set": sorted(
                {stage.value for stage in {n.standard_stage for n in result.mapped.nodes}}
            ),
        }

    # --------------------- internal builders ---------------------

    @staticmethod
    def _build_graph(flow: ProcessFlow, mapped: MappedFlow) -> StageGraph:
        stage_ids: list[str] = []
        membership: list[tuple[str, tuple[str, ...]]] = []
        node_to_stage: list[tuple[str, str]] = []
        standard_by_node: list[tuple[str, StandardStage]] = []

        # Index mapped nodes by node_id for O(1) lookup of standard_stage.
        mapped_index: dict[str, StandardStage] = {
            m.node.node_id: m.standard_stage for m in mapped.nodes
        }

        for stage in flow.stages:
            stage_ids.append(stage.stage_id)
            member_ids = tuple(n.node_id for n in stage.nodes)
            membership.append((stage.stage_id, member_ids))
            for nid in member_ids:
                node_to_stage.append((nid, stage.stage_id))
                if nid in mapped_index:
                    standard_by_node.append((nid, mapped_index[nid]))

        return StageGraph(
            stage_ids_in_order=tuple(stage_ids),
            stage_membership=tuple(membership),
            node_to_stage=tuple(node_to_stage),
            standard_stage_by_node=tuple(standard_by_node),
        )

    @staticmethod
    def _build_reviewer_view(flow: ProcessFlow) -> ReviewerView:
        index: list[tuple[str, float]] = []

        def _record(path: str, traced: Traced) -> None:
            index.append((path, float(traced.confidence)))

        if flow.title.source_path:
            _record("flow.title", flow.title)

        for s_idx, stage in enumerate(flow.stages):
            for n_idx, node in enumerate(stage.nodes):
                base = f"stages[{s_idx}].nodes[{n_idx}]"
                # Node title carries its own Traced; rebuild via the node's
                # stored value so reviewer_view's confidence index aligns
                # with the parser-produced trace. We synthesize a LITERAL
                # trace mirroring parser semantics (confidence 0.95).
                _record(
                    f"{base}.title",
                    Traced(
                        value=node.title,
                        source_path=f"{base}.title",
                        confidence=0.95,
                        source_kind=SourceKind.LITERAL,
                    ),
                )
                _record(f"{base}.stage_hint", node.stage_hint)
                for i, t in enumerate(node.inputs):
                    _record(f"{base}.inputs[{i}]", t)
                for i, t in enumerate(node.outputs):
                    _record(f"{base}.outputs[{i}]", t)
                for i, t in enumerate(node.review_criteria):
                    _record(f"{base}.review_criteria[{i}]", t)
                for i, t in enumerate(node.responsible_roles):
                    _record(f"{base}.responsible_roles[{i}]", t)

        for r_idx, role in enumerate(flow.roles):
            base = f"roles[{r_idx}]"
            _record(f"{base}.responsibility", role.responsibility)

        return ReviewerView(flow=flow, _confidence_index=tuple(index))


__all__ = [
    "FlowUnderstanding",
    "FlowUnderstandingService",
    "ReviewerView",
    "StageGraph",
    "TaskFlowValidationError",
]