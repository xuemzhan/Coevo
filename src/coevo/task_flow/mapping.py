"""US-1 stage mapping (AC-7).

Per-unit flow nodes carry an arbitrary ``stage_hint`` string. The
system has a closed set of standardized stages (:class:`StandardStage`)
that all UI and orchestration code speaks. This module turns a
per-unit hint into a :class:`StandardStage` using a deterministic
rule table.

The rule table is itself versioned (the default table is version 1)
so we can later add new standard stages without invalidating
already-confirmed flows.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-1 阶段映射：规则表把 unit 节点映射到 StandardStage，O(1) 查询。
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import (
    MappingRule,
    Node,
    ProcessFlow,
    ProcessFlowError,
    StandardStage,
)


@dataclass(frozen=True)
class MappedNode:
    """A per-unit node with its standardized stage attached."""

    node: Node
    standard_stage: StandardStage
    rule_id: str


@dataclass(frozen=True)
class MappedFlow:
    """The mapped view of a :class:`ProcessFlow` (used by downstream)."""

    unit_id: str
    version: int
    nodes: tuple[MappedNode, ...]


def apply_mapping(
    flow: ProcessFlow,
    rules: Iterable[MappingRule] | None = None,
) -> MappedFlow:
    """Map every node in ``flow`` to a :class:`StandardStage`.

    Algorithm
    ---------
    * Sort rules by ``(priority ASC, rule_id ASC)`` and build a
      ``hint -> best rule`` dictionary once (the first rule in the
      sorted order per hint is the winner by definition).
    * For each node, resolve its ``unit_stage_hint`` with a single
      O(1) dictionary lookup instead of scanning the whole table.
    * If no rule matches, raise :class:`ProcessFlowError`.

    The rule table MUST contain :data:`DEFAULT_MAPPING_RULES` plus
    any rules the unit has supplied for itself.
    """
    rule_list = list(rules) if rules is not None else list(DEFAULT_MAPPING_RULES)
    if not rule_list:
        raise ProcessFlowError("mapping rule table must be non-empty")
    sorted_rules = sorted(rule_list, key=lambda r: (r.priority, r.rule_id))
    best_rule_by_hint: dict[str, MappingRule] = {}
    for rule in sorted_rules:
        # The first rule encountered for a hint is the winner because
        # the list is ordered by (priority ASC, rule_id ASC).
        best_rule_by_hint.setdefault(rule.unit_stage_hint, rule)

    mapped: list[MappedNode] = []
    seen: set[str] = set()
    for stage in flow.stages:
        for node in stage.nodes:
            hint = node.stage_hint.value
            match_rule = best_rule_by_hint.get(hint)
            if match_rule is None:
                raise ProcessFlowError(
                    f"no mapping rule matches stage_hint {hint!r} for "
                    f"node {node.node_id!r} in unit {flow.unit_id!r}"
                )
            key = f"{flow.unit_id}:{node.node_id}"
            if key in seen:
                raise ProcessFlowError(f"duplicate node key {key!r} during mapping")
            seen.add(key)
            mapped.append(
                MappedNode(node=node, standard_stage=match_rule.standard_stage,
                           rule_id=match_rule.rule_id)
            )

    if flow.mapping_rules_version != 1:
        raise ProcessFlowError(
            f"unsupported mapping_rules_version {flow.mapping_rules_version!r}; "
            f"only 1 is supported"
        )

    return MappedFlow(
        unit_id=flow.unit_id,
        version=flow.version,
        nodes=tuple(mapped),
    )


#: The default rule table. Versioned to 1.
#:
#: Lower ``priority`` wins ties; ``rule_id`` is the secondary key.
DEFAULT_MAPPING_RULES: tuple[MappingRule, ...] = (
    MappingRule(rule_id="m1",  unit_stage_hint="intake",   standard_stage=StandardStage.INTAKE,   priority=10),
    MappingRule(rule_id="m2",  unit_stage_hint="Intake",   standard_stage=StandardStage.INTAKE,   priority=11),
    MappingRule(rule_id="m3",  unit_stage_hint="接收",      standard_stage=StandardStage.INTAKE,   priority=12),
    MappingRule(rule_id="m4",  unit_stage_hint="接收阶段",  standard_stage=StandardStage.INTAKE,   priority=13),
    MappingRule(rule_id="m10", unit_stage_hint="planning",  standard_stage=StandardStage.PLANNING, priority=10),
    MappingRule(rule_id="m11", unit_stage_hint="Planning",  standard_stage=StandardStage.PLANNING, priority=11),
    MappingRule(rule_id="m12", unit_stage_hint="策划",      standard_stage=StandardStage.PLANNING, priority=12),
    MappingRule(rule_id="m13", unit_stage_hint="方案策划",  standard_stage=StandardStage.PLANNING, priority=13),
    MappingRule(rule_id="m20", unit_stage_hint="execution", standard_stage=StandardStage.EXECUTION, priority=10),
    MappingRule(rule_id="m21", unit_stage_hint="Execution", standard_stage=StandardStage.EXECUTION, priority=11),
    MappingRule(rule_id="m22", unit_stage_hint="执行",      standard_stage=StandardStage.EXECUTION, priority=12),
    MappingRule(rule_id="m23", unit_stage_hint="实施",      standard_stage=StandardStage.EXECUTION, priority=13),
    MappingRule(rule_id="m24", unit_stage_hint="开发阶段",  standard_stage=StandardStage.EXECUTION, priority=14),
    MappingRule(rule_id="m30", unit_stage_hint="review",    standard_stage=StandardStage.REVIEW,   priority=10),
    MappingRule(rule_id="m31", unit_stage_hint="Review",    standard_stage=StandardStage.REVIEW,   priority=11),
    MappingRule(rule_id="m32", unit_stage_hint="审核",      standard_stage=StandardStage.REVIEW,   priority=12),
    MappingRule(rule_id="m33", unit_stage_hint="评审",      standard_stage=StandardStage.REVIEW,   priority=13),
    MappingRule(rule_id="m40", unit_stage_hint="delivery",  standard_stage=StandardStage.DELIVERY, priority=10),
    MappingRule(rule_id="m41", unit_stage_hint="Delivery",  standard_stage=StandardStage.DELIVERY, priority=11),
    MappingRule(rule_id="m42", unit_stage_hint="交付",      standard_stage=StandardStage.DELIVERY, priority=12),
    MappingRule(rule_id="m43", unit_stage_hint="验收",      standard_stage=StandardStage.DELIVERY, priority=13),
    MappingRule(rule_id="m44", unit_stage_hint="提交",      standard_stage=StandardStage.DELIVERY, priority=14),
    MappingRule(rule_id="m50", unit_stage_hint="closure",   standard_stage=StandardStage.CLOSURE,  priority=10),
    MappingRule(rule_id="m51", unit_stage_hint="Closure",   standard_stage=StandardStage.CLOSURE,  priority=11),
    MappingRule(rule_id="m52", unit_stage_hint="收尾",      standard_stage=StandardStage.CLOSURE,  priority=12),
    MappingRule(rule_id="m53", unit_stage_hint="结束",      standard_stage=StandardStage.CLOSURE,  priority=13),
    MappingRule(rule_id="m54", unit_stage_hint="复盘",      standard_stage=StandardStage.CLOSURE,  priority=14),
)
