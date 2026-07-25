"""Offline task-flow ingestion and per-unit modeling (US-1).

This package implements the deterministic data-model half of US-1
("task-process-understanding" agent). The agent itself is a thin
adapter that feeds already-canonicalized inputs into :mod:`.parser`
and produces a versioned :class:`ProcessFlow` model with:

* explicit ``version`` integer (never a timestamp — AGENTS.md §3 第 2 条);
* per-field source mapping (which input field produced each output
  field) with a deterministic confidence score;
* reviewer-edited overlay so a human's manual edits are recorded
  without losing the model's original extraction;
* a strict mapping layer that turns per-unit flow nodes into the
  system's standardized stages.

Scope (US-1-AC-1 acceptance criteria 1..7):
  AC-1  import flow documents / tables / templates (caller hands us
        a canonical JSON INPUT; the parser is deterministic).
  AC-2  extract stage, node, role, IO, review criteria fields.
  AC-3  expose ``source_mapping`` so the UI can pair raw input with
        parsed fields.
  AC-4  per-field ``confidence_score`` ∈ [0, 1] and ``source_kind``
        (literal, derived, defaulted) on each parsed attribute.
  AC-5  reviewer edits become ``Override`` entries that survive a
        re-parse without overwriting human input.
  AC-6  confirm(...) emits a new :class:`ProcessFlow` with monotonic
        integer ``version``.
  AC-7  stage mapping rules live in :mod:`.mapping` and are also
        version-tagged.

What this is NOT:
* No LLM call — the parser is a deterministic state machine, not a
  neural extractor. The "理解" agent in production is a separate
  slice backed by an offline-approved model; for the MVP AC-1 we
  ship the deterministic data model first so the wiring is provable.
* No I/O of any kind — no filesystem, no network. Input and output
  are Python objects only.
"""
from .models import (
    MappingRule,
    Node,
    ProcessFlow,
    ProcessFlowError,
    ProcessFlowParseError,
    Role,
    SourceKind,
    SourceMapping,
    StandardStage,
    Traced,
)
from .parser import parse_flow
from .mapping import (
    DEFAULT_MAPPING_RULES,
    apply_mapping,
)

__all__ = [
    "DEFAULT_MAPPING_RULES",
    "MappingRule",
    "Node",
    "ProcessFlow",
    "ProcessFlowError",
    "ProcessFlowParseError",
    "Role",
    "SourceKind",
    "SourceMapping",
    "StandardStage",
    "Traced",
    "apply_mapping",
    "parse_flow",
]
