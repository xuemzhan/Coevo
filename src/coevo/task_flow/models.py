"""US-1 task-flow domain model.

Design notes
------------
* Every domain class is a frozen dataclass so a confirmed
  :class:`ProcessFlow` is immutable once stored; later edits go
  through the override layer (:class:`Override`) or produce a new
  :class:`ProcessFlow` with a higher monotonic ``version``.

* Versions are integers, never timestamps (AGENTS.md §3 第 2 条
  forbids timestamps as version surrogates).

* Every "extracted" attribute that the parser produces carries a
  :class:`Traced` wrapper that records the input field it came from
  (:attr:`source_path`), the confidence score the deterministic
  parser assigns, and the :class:`SourceKind` (literal vs derived
  vs defaulted). Override edits are recorded separately so the
  original trace is never lost.

* Stage names follow the system's standardized taxonomy
  (:class:`StandardStage`). Per-unit flow nodes may carry arbitrary
  stage names; the mapping layer (:mod:`.mapping`) translates them
  into the standardized enum.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field, replace
from typing import Mapping


class ProcessFlowError(Exception):
    """Base class for all US-1 errors. Fail-closed by default."""


class ProcessFlowParseError(ProcessFlowError):
    """Raised when the deterministic parser cannot reconcile inputs.

    The parser never raises a 'soft' error — every inconsistency is
    surfaced, since AGENTS.md §3 第 7 条禁止掩盖错误.
    """


class SourceKind(enum.Enum):
    """How an attribute value entered the model.

    * ``LITERAL`` — copied verbatim from the raw input.
    * ``DERIVED`` — deterministically computed from one or more
      inputs (e.g. role set deduplication, stage sort).
    * ``DEFAULTED`` — bound by a default because the input did not
      supply it (UI must surface these so the reviewer can confirm).
    * ``OVERRIDDEN`` — reviewer-edited value that replaced the
      model's original extraction; the original trace is preserved
      alongside via :class:`Override`.
    """

    LITERAL = "literal"
    DERIVED = "derived"
    DEFAULTED = "defaulted"
    OVERRIDDEN = "overridden"


@dataclass(frozen=True)
class Traced:
    """A single extracted value + provenance.

    ``source_path`` is a dotted JSON-pointer-like path inside the raw
    input mapping, e.g. ``"rows[3].columns[1].value"``. Empty string
    means "synthesized at parse time without an input counterpart".
    """

    value: object
    source_path: str
    confidence: float  # ∈ [0.0, 1.0]
    source_kind: SourceKind

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.confidence) <= 1.0:  # noqa: PLR2004 - validation
            raise ProcessFlowError(
                f"confidence must be in [0, 1]; got {self.confidence!r}"
            )


@dataclass(frozen=True)
class Override:
    """A reviewer edit that replaces a previously extracted value."""

    target_path: str
    original_value: object
    edited_value: object
    reason: str


@dataclass(frozen=True)
class Role:
    """A role in the unit's task process (e.g. "QAC reviewer")."""

    role_id: str
    name: str
    responsibility: Traced


@dataclass(frozen=True)
class Node:
    """A single process node (= a task step)."""

    node_id: str
    title: str
    stage_hint: Traced  # arbitrary per-unit name; mapped by mapping layer
    inputs: tuple[Traced, ...]
    outputs: tuple[Traced, ...]
    review_criteria: tuple[Traced, ...]
    responsible_roles: tuple[Traced, ...]


@dataclass(frozen=True)
class Stage:
    """A process stage (= an ordered group of nodes)."""

    stage_id: str
    name: str
    nodes: tuple[Node, ...]


class StandardStage(enum.Enum):
    """The system's standardized stage taxonomy.

    Per AC-7, per-unit flow nodes are mapped onto this enum. The
    default mapping table lives in :mod:`.mapping`.
    """

    INTAKE = "intake"
    PLANNING = "planning"
    EXECUTION = "execution"
    REVIEW = "review"
    DELIVERY = "delivery"
    CLOSURE = "closure"


@dataclass(frozen=True)
class SourceMapping:
    """AC-3: maps each parsed output attribute back to raw input.

    Keys are dotted paths inside the parsed model (e.g.
    ``"stages[0].nodes[2].title"``); values are the corresponding
    raw input paths. Missing entries mean "no input counterpart
    (synthesized)" — never silently dropped.
    """

    entries: tuple[tuple[str, str], ...]

    def get(self, key: str) -> str | None:
        for k, v in self.entries:
            if k == key:
                return v
        return None


@dataclass(frozen=True)
class MappingRule:
    """AC-7: a single rule mapping a per-unit stage hint to a standard stage.

    The rule set is itself versioned so we can evolve the taxonomy
    without invalidating confirmed flows.
    """

    rule_id: str
    unit_stage_hint: str
    standard_stage: StandardStage
    priority: int  # lower wins; ties broken by rule_id


@dataclass(frozen=True)
class ProcessFlow:
    """AC-6: a confirmed, versioned unit task-process model.

    ``unit_id`` is the unit name; ``version`` is a monotonic integer
    that increments on every confirm(); ``created_at`` is an
    ISO-8601 UTC string with a 'Z' suffix; it is NOT used for
    ordering — that is ``version``'s job.
    """

    unit_id: str
    version: int
    created_at: str  # ISO-8601 UTC with 'Z' suffix (informational only)
    title: Traced
    stages: tuple[Stage, ...]
    roles: tuple[Role, ...]
    source_mapping: SourceMapping
    overrides: tuple[Override, ...] = field(default_factory=tuple)
    mapping_rules_version: int = 1

    def with_overrides(
        self,
        overrides: tuple[Override, ...],
        new_created_at: str,
    ) -> "ProcessFlow":
        """Return a new :class:`ProcessFlow` at version+1 with overrides applied.

        The actual value substitutions are the caller's responsibility
        (the model layer is pure data). This helper only bumps the
        version + records the overrides.
        """
        if not overrides:
            raise ProcessFlowError("with_overrides requires non-empty overrides")
        return replace(
            self,
            version=self.version + 1,
            created_at=new_created_at,
            overrides=overrides,
        )
