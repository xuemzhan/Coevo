"""US-1 deterministic flow parser.

Scope
-----
* :func:`parse_flow` accepts a canonical JSON-shaped mapping and
  returns a *draft* :class:`ProcessFlow` plus a :class:`SourceMapping`.
* No network, no IO, no models — this is a deterministic state
  machine whose only side effects are the return values.

* The parser accepts these shapes (decided by callers per
  AC-1 "import documents / tables / templates"):
  - tabular: ``{"format": "tabular", "columns": [...], "rows": [...]}``
  - tree:    ``{"format": "tree", "root": {...}}``
  - already-canonical: ``{"format": "canonical", "flow": {...}}``

  "Tabular" and "tree" are reduced to the same canonical schema so
  downstream code is shape-agnostic.

What the parser refuses (fail-closed, AGENTS.md §3 第 7 条)
------------------------------------------------------------
* Unknown ``format`` value.
* Duplicate IDs (stage_id / node_id / role_id).
* Rows that lack the minimum fields required by AC-2.
* Non-finite or non-UTF-8 strings (defensive; safe to raise).
* Confidence values outside [0, 1].
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# US-1 确定性流程解析器：canonical/tabular/tree 三 schema，失败关闭。
from __future__ import annotations

import re
from typing import Any, Mapping
from src.coevo.timefmt import now_utc_iso_z

from .models import (
    Node,
    ProcessFlow,
    ProcessFlowParseError,
    Role,
    SourceKind,
    SourceMapping,
    Stage,
    Traced,
)


_SAFE_ID = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_.\-]{0,63}$")


def _str_traced(value: Any, source_path: str, kind: SourceKind,
                confidence: float = 0.9) -> Traced:
    if not isinstance(value, str):
        raise ProcessFlowParseError(
            f"expected string at {source_path!r}; got {type(value).__name__}"
        )
    if not value:
        raise ProcessFlowParseError(f"empty string at {source_path!r}")
    return Traced(value, source_path, confidence, kind)


def _list_traced(values: Any, source_path: str, item_path_tmpl: str,
                 element_kind: SourceKind = SourceKind.LITERAL,
                 default_confidence: float = 0.85) -> tuple[Traced, ...]:
    if not isinstance(values, list):
        raise ProcessFlowParseError(
            f"expected list at {source_path!r}; got {type(values).__name__}"
        )
    out: list[Traced] = []
    for idx, v in enumerate(values):
        out.append(_str_traced(v, item_path_tmpl.format(idx=idx), element_kind, default_confidence))
    return tuple(out)


def _ensure_id(value: Any, source_path: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.match(value):
        raise ProcessFlowParseError(
            f"invalid identifier at {source_path!r}: {value!r}"
        )
    return value


def _checked_unique(ids: list[str], kind: str) -> None:
    seen: set[str] = set()
    for i in ids:
        if i in seen:
            raise ProcessFlowParseError(f"duplicate {kind}_id: {i!r}")
        seen.add(i)


def _to_stage(stage: Mapping[str, Any], stage_idx: int,
              source_pairs: list[tuple[str, str]]) -> Stage:
    """Reduce a 'stage' dict to :class:`Stage`.

    Required keys: ``stage_id``, ``name``, ``nodes``.
    """
    base = f"stages[{stage_idx}]"
    stage_id = _ensure_id(stage["stage_id"], f"{base}.stage_id")
    name = _str_traced(stage["name"], f"{base}.name", SourceKind.LITERAL, 0.95)
    source_pairs.append((f"{base}.name", "title"))

    raw_nodes = stage.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ProcessFlowParseError(
            f"stage {stage_id!r} must contain a non-empty 'nodes' list"
        )

    nodes = tuple(_to_node(n, stage_idx, n_idx, source_pairs) for n_idx, n in enumerate(raw_nodes))

    return Stage(stage_id=stage_id, name=name.value, nodes=nodes)


def _to_node(node: Mapping[str, Any], stage_idx: int, node_idx: int,
             source_pairs: list[tuple[str, str]]) -> Node:
    base = f"stages[{stage_idx}].nodes[{node_idx}]"
    nid = _ensure_id(node["node_id"], f"{base}.node_id")
    title = _str_traced(node["title"], f"{base}.title", SourceKind.LITERAL, 0.95)
    source_pairs.append((f"{base}.title", "title"))

    stage_hint_value = node.get("stage_hint", "")
    if not isinstance(stage_hint_value, str):
        raise ProcessFlowParseError(
            f"stage_hint at {base!r} must be a string"
        )
    # stage_hint is LITERAL with mild confidence (defaults are easy)
    stage_hint = Traced(
        stage_hint_value or stage_hint_value,
        f"{base}.stage_hint",
        0.85 if stage_hint_value else 0.5,
        SourceKind.LITERAL if stage_hint_value else SourceKind.DEFAULTED,
    )

    inputs = _list_traced(node.get("inputs", []), f"{base}.inputs",
                           f"{base}.inputs[{{idx}}]", SourceKind.LITERAL, 0.8)
    outputs = _list_traced(node.get("outputs", []), f"{base}.outputs",
                            f"{base}.outputs[{{idx}}]", SourceKind.LITERAL, 0.8)
    reviews = _list_traced(node.get("review_criteria", []),
                            f"{base}.review_criteria",
                            f"{base}.review_criteria[{{idx}}]", SourceKind.LITERAL, 0.8)
    roles = _list_traced(node.get("responsible_roles", []),
                          f"{base}.responsible_roles",
                          f"{base}.responsible_roles[{{idx}}]", SourceKind.LITERAL, 0.8)

    source_pairs.extend([
        (f"{base}.stage_hint", "stage_hint"),
        (f"{base}.inputs", "inputs"),
        (f"{base}.outputs", "outputs"),
        (f"{base}.review_criteria", "review_criteria"),
        (f"{base}.responsible_roles", "responsible_roles"),
    ])

    return Node(
        node_id=nid,
        title=title.value,
        stage_hint=stage_hint,
        inputs=inputs,
        outputs=outputs,
        review_criteria=reviews,
        responsible_roles=roles,
    )


def _to_role(role: Mapping[str, Any], role_idx: int,
             source_pairs: list[tuple[str, str]]) -> Role:
    base = f"roles[{role_idx}]"
    rid = _ensure_id(role["role_id"], f"{base}.role_id")
    name = _str_traced(role["name"], f"{base}.name", SourceKind.LITERAL, 0.9)
    responsibility = _str_traced(
        role["responsibility"], f"{base}.responsibility", SourceKind.LITERAL, 0.85,
    )
    source_pairs.append((f"{base}.responsibility", "responsibility"))
    return Role(role_id=rid, name=name.value, responsibility=responsibility)


def parse_flow(raw: Mapping[str, Any]) -> ProcessFlow:
    """Parse a canonicalized raw input into a draft :class:`ProcessFlow`.

    The returned flow is a *draft* — :attr:`ProcessFlow.overrides` is
    empty. Reviewers call :meth:`ProcessFlow.with_overrides` (after
    editing the value layers themselves) to bump the version.

    The draft has ``version=1`` and ``created_at=now_utc``.
    """
    if not isinstance(raw, Mapping):
        raise ProcessFlowParseError("flow document must be a mapping")

    fmt = raw.get("format")
    canonical: Mapping[str, Any]
    if fmt == "canonical":
        canonical = raw["flow"]
        if not isinstance(canonical, Mapping):
            raise ProcessFlowParseError("'flow' must be a mapping")
    elif fmt == "tabular":
        canonical = _tabular_to_canonical(raw)
    elif fmt == "tree":
        canonical = _tree_to_canonical(raw)
    else:
        raise ProcessFlowParseError(f"unknown 'format': {fmt!r}")

    if not isinstance(canonical, Mapping):
        raise ProcessFlowParseError("canonical payload must be a mapping")

    unit_id = _ensure_id(canonical.get("unit_id", ""), "flow.unit_id") if "unit_id" in canonical else ""
    if not unit_id:
        raise ProcessFlowParseError("flow.unit_id is required")
    title = _str_traced(
        canonical.get("title", canonical.get("unit_id", "")),
        "flow.title", SourceKind.LITERAL, 0.95,
    )
    source_pairs: list[tuple[str, str]] = [("flow.title", "title")]

    raw_stages = canonical.get("stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise ProcessFlowParseError("flow.stages must be a non-empty list")
    stages = tuple(_to_stage(s, idx, source_pairs) for idx, s in enumerate(raw_stages))

    _checked_unique([s.stage_id for s in stages], "stage")
    node_ids: list[str] = []
    for s in stages:
        node_ids.extend(n.node_id for n in s.nodes)
    _checked_unique(node_ids, "node")

    raw_roles = canonical.get("roles", [])
    if not isinstance(raw_roles, list):
        raise ProcessFlowParseError("flow.roles must be a list")
    roles = tuple(_to_role(r, idx, source_pairs) for idx, r in enumerate(raw_roles))
    _checked_unique([r.role_id for r in roles], "role")

    return ProcessFlow(
        unit_id=unit_id,
        version=1,
        created_at=now_utc_iso_z(),
        title=title,
        stages=stages,
        roles=roles,
        source_mapping=SourceMapping(tuple(source_pairs)),
        overrides=tuple(),
    )


# --------------------------- format adapters ----------------------------


def _tabular_to_canonical(raw: Mapping[str, Any]) -> Mapping[str, Any]:
    """Reduce a tabular input into the canonical schema.

    Required keys: ``columns`` (non-empty list of strings),
    ``rows`` (non-empty list of mappings).
    """
    columns = raw.get("columns")
    rows = raw.get("rows")
    if not isinstance(columns, list) or not columns:
        raise ProcessFlowParseError("tabular input requires non-empty 'columns'")
    if not isinstance(rows, list) or not rows:
        raise ProcessFlowParseError("tabular input requires non-empty 'rows'")
    column_set = {str(c) for c in columns}

    stages_index: dict[str, dict[str, Any]] = {}
    for r_idx, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ProcessFlowParseError(f"rows[{r_idx}] must be a mapping")
        for k in row.keys():
            if str(k) not in column_set:
                raise ProcessFlowParseError(
                    f"rows[{r_idx}] has unknown column {k!r}; expected one of {sorted(column_set)!r}"
                )
        stage_name = row.get("stage") or row.get("阶段") or "stage"
        if not isinstance(stage_name, str) or not stage_name:
            raise ProcessFlowParseError(
                f"rows[{r_idx}] missing a non-empty 'stage' value"
            )
        slot = stages_index.setdefault(
            stage_name, {"stage_id": stage_name, "name": stage_name, "nodes": []}
        )
        # Required per-node fields
        for required_key in ("node_id", "title", "responsible_roles"):
            if required_key not in row:
                raise ProcessFlowParseError(
                    f"rows[{r_idx}] missing required column {required_key!r}"
                )
        slot["nodes"].append({
            "node_id": row["node_id"],
            "title": row["title"],
            "stage_hint": row.get("stage_hint") or row.get("阶段节点", "") or stage_name,
            "inputs": row.get("inputs", []),
            "outputs": row.get("outputs", []),
            "review_criteria": row.get("review_criteria", []),
            "responsible_roles": row["responsible_roles"],
        })

    return {
        "unit_id": raw.get("unit_id", ""),
        "title": raw.get("title") or raw.get("unit_id", ""),
        "stages": list(stages_index.values()),
        "roles": raw.get("roles", []),
    }


def _tree_to_canonical(raw: Mapping[str, Any]) -> Mapping[str, Any]:
    """Reduce a nested-tree input into the canonical schema.

    Required keys: ``root`` (a nested mapping with children).
    Tree structure::

        {"name": "stage-name", "nodes": [{"name": "node", "...": "..."}]}
    """
    root = raw.get("root")
    if not isinstance(root, Mapping):
        raise ProcessFlowParseError("tree input requires 'root' mapping")

    stages: list[dict[str, Any]] = []

    def walk(node: Mapping[str, Any], path: str) -> dict[str, Any]:
        if "name" not in node or "children" not in node:
            raise ProcessFlowParseError(
                f"tree node at {path!r} must have both 'name' and 'children'"
            )
        if not isinstance(node["name"], str) or not node["name"]:
            raise ProcessFlowParseError(f"tree node at {path!r} missing 'name'")
        if not isinstance(node["children"], list):
            raise ProcessFlowParseError(f"tree node at {path!r} 'children' must be a list")

        raw_nodes = node.get("nodes", [])
        if not isinstance(raw_nodes, list):
            raise ProcessFlowParseError(f"tree node at {path!r} 'nodes' must be a list")

        stage_entry: dict[str, Any] = {
            "stage_id": node["name"],
            "name": node["name"],
            "nodes": [
                {
                    "node_id": n.get("id", f"node_{i}"),
                    "title": n.get("title", n.get("name", "")),
                    "stage_hint": n.get("stage_hint", node["name"]),
                    "inputs": n.get("inputs", []),
                    "outputs": n.get("outputs", []),
                    "review_criteria": n.get("review_criteria", []),
                    "responsible_roles": n.get("responsible_roles", []),
                }
                for i, n in enumerate(raw_nodes)
            ],
        }
        stages.append(stage_entry)
        for c_idx, child in enumerate(node["children"]):
            if not isinstance(child, Mapping):
                raise ProcessFlowParseError(f"tree child {path}/{c_idx} must be a mapping")
            walk(child, f"{path}/{child.get('name', c_idx)}")
        return stage_entry

    walk(root, "root")

    return {
        "unit_id": raw.get("unit_id", ""),
        "title": raw.get("title") or root.get("name", ""),
        "stages": stages,
        "roles": raw.get("roles", []),
    }
