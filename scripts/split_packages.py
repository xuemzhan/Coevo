"""Bulk mechanical split of oversized package __init__.py files.

Preserves comments and formatting via source-segment slicing, prunes
imports per module by used names, and regenerates the package
__init__.py as a re-export facade. Public namespace is unchanged.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys


ROOT = pathlib.Path("src/coevo")


def line_offsets(src: str) -> list[int]:
    offsets = [0]
    for i, ch in enumerate(src):
        if ch == "\n":
            offsets.append(i + 1)
    return offsets


def node_start(node: ast.AST, offsets: list[int]) -> int:
    start = offsets[node.lineno - 1] + node.col_offset
    # In CPython >= 3.8 the lineno of a decorated class/function points
    # to the ``class``/``def`` keyword, NOT the first decorator line.
    # Extend the slice backwards so decorators are preserved.
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        decorators = getattr(node, "decorator_list", ())
        if decorators:
            first_line = min(dec.lineno for dec in decorators)
            first_col = min(
                dec.col_offset
                for dec in decorators
                if dec.lineno == first_line
            )
            # ``col_offset`` points at the decorator NAME; the ``@``
            # marker is exactly one column to its left.
            start = min(start, offsets[first_line - 1] + first_col - 1)
    return start


def node_end(node: ast.AST, offsets: list[int]) -> int:
    return offsets[node.end_lineno - 1] + node.end_col_offset


def node_names(node: ast.AST) -> list[str]:
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        out: list[str] = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                out.append(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        out.append(elt.id)
        return out
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    return []


def used_names(nodes: list[ast.AST]) -> set[str]:
    used: set[str] = set()
    for node in nodes:
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                used.add(child.id)
            elif isinstance(child, ast.Attribute) and isinstance(child.ctx, ast.Load):
                root: ast.AST = child
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name):
                    used.add(root.id)
    return used


def import_bound_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.asname or alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        return [alias.asname or alias.name for alias in node.names]
    return []


def filter_import(node: ast.AST, used: set[str]) -> ast.AST | None:
    if isinstance(node, ast.Import):
        kept = [
            alias
            for alias in node.names
            if (alias.asname or alias.name.split(".")[0]) in used
        ]
        if not kept:
            return None
        return ast.Import(names=kept)
    if isinstance(node, ast.ImportFrom):
        if node.module == "__future__":
            return node
        kept = [
            alias
            for alias in node.names
            if (alias.asname or alias.name) in used
        ]
        if not kept:
            return None
        return ast.ImportFrom(
            module=node.module,
            names=kept,
            level=node.level,
        )
    return node


def render(statements: list[ast.AST]) -> str:
    return "\n".join(ast.unparse(stmt) for stmt in statements)


def split_package(pkg: str, plan: dict) -> None:
    path = ROOT / pkg / "__init__.py"
    src = path.read_text(encoding="utf-8")
    offsets = line_offsets(src)
    tree = ast.parse(src)
    body = tree.body
    doc = ast.get_docstring(tree) or ""
    modules = plan["modules"]
    target_of = plan["targets"]
    default = plan.get("default", "models")
    keep_in_init = set(plan.get("keep_in_init", ()))

    doc_node = None
    if body and isinstance(body[0], ast.Expr) and isinstance(
        body[0].value, ast.Constant
    ) and isinstance(body[0].value.value, str):
        doc_node = body[0]

    groups: dict[str, list[ast.AST]] = {m: [] for m in modules}
    imports: list[ast.AST] = []
    keep_nodes: list[ast.AST] = []
    all_node = None
    for node in body:
        if node is doc_node:
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
            continue
        if isinstance(node, ast.Assign):
            names = node_names(node)
            if "__all__" in names:
                all_node = node
                continue
            if any(name in keep_in_init for name in names):
                keep_nodes.append(node)
                continue
        name = (node_names(node) or [None])[0]
        target = target_of.get(name, default)
        groups[target].append(node)

    defined: dict[str, set[str]] = {m: set() for m in modules}
    for mod, nodes in groups.items():
        for node in nodes:
            defined[mod].update(node_names(node))

    # Build source segments that preserve inter-definition comments.
    cursor = 0
    for node in body:
        if node is doc_node or isinstance(node, (ast.Import, ast.ImportFrom)):
            cursor = max(cursor, node_end(node, offsets))
        else:
            break
    segments: dict[str, list[str]] = {m: [] for m in modules}
    keep_segments: list[str] = []
    for node in body:
        if node is doc_node or isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if node is all_node:
            cursor = node_end(node, offsets)
            continue
        if node in keep_nodes:
            start = max(cursor, node_start(node, offsets))
            keep_segments.append(src[start:node_end(node, offsets)])
            cursor = node_end(node, offsets)
            continue
        name = (node_names(node) or [None])[0]
        target = target_of.get(name, default)
        start = max(cursor, node_start(node, offsets))
        segments[target].append(src[start:node_end(node, offsets)])
        cursor = node_end(node, offsets)

    for mod in modules:
        nodes = groups[mod]
        used = used_names(nodes)
        has_future = any(
            isinstance(i, ast.ImportFrom) and i.module == "__future__"
            for i in imports
        )
        parts = [f'"""{pkg}.{mod} - {plan["descriptions"][mod]}"""', ""]
        if has_future:
            parts.append("from __future__ import annotations")
            parts.append("")
        kept_imports = [
            filtered
            for imp in imports
            if (filtered := filter_import(imp, used)) is not None
            and not (
                isinstance(filtered, ast.ImportFrom)
                and filtered.module == "__future__"
            )
        ]
        if kept_imports:
            parts.append(render(kept_imports))
        # Cross-module imports for names used here but defined elsewhere.
        missing = {
            name
            for name in used
            if any(
                mod != other and name in defined[other]
                for other in modules
            )
        }
        for other in modules:
            if other == mod:
                continue
            shared = sorted(name for name in missing if name in defined[other])
            if shared:
                parts.append(f"from .{other} import {', '.join(shared)}")
        if segments[mod]:
            parts.append("\n\n".join(segments[mod]))
        module_text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(parts))
        (ROOT / pkg / f"{mod}.py").write_text(
            module_text + "\n", encoding="utf-8"
        )

    # Regenerate __init__.py as a re-export facade.
    init_parts = [f'"""{doc}"""', ""]
    if has_future:
        init_parts.append("from __future__ import annotations")
        init_parts.append("")
    init_imports = [
        imp
        for imp in imports
        if not (
            isinstance(imp, ast.ImportFrom) and imp.module == "__future__"
        ) and not (isinstance(imp, ast.ImportFrom) and imp.level >= 1)
    ]
    if init_imports:
        init_parts.append(render(init_imports))
        init_parts.append("")
    for mod in modules:
        names = sorted(defined[mod])
        if names:
            init_parts.append(f"from .{mod} import ({', '.join(names)})")
    relative_imports = [
        imp
        for imp in imports
        if isinstance(imp, ast.ImportFrom)
        and imp.level >= 1
        and imp.module != "__future__"
    ]
    if relative_imports:
        init_parts.append("")
        init_parts.append(render(relative_imports))
    if keep_segments:
        init_parts.append("\n\n".join(keep_segments))
    if all_node is not None:
        init_parts.append(
            src[node_start(all_node, offsets):node_end(all_node, offsets)]
        )
    text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(init_parts))
    path.write_text(text + "\n", encoding="utf-8")
    print(f"[split] {pkg}: {', '.join(f'{m}={len(groups[m])}' for m in modules)}")


CONFIGS: dict[str, dict] = {
    "merge": {
        "modules": ["models", "engine"],
        "descriptions": {
            "models": (
                "domain models, enums, sentinels and errors for US-10 "
                "(merged from the former package __init__)."
            ),
            "engine": (
                "deterministic MergeEngine facade (US-10-AC-1 P1 + Round-2)."
            ),
        },
        "targets": {
            "_MissingSentinel": "models",
            "_is_missing": "models",
            "MISSING": "models",
            "MERGEABLE_PACKAGE_TYPES": "models",
            "MergeDecision": "models",
            "FieldMerge": "models",
            "MergeRecord": "models",
            "MergeProposal": "models",
            "MergeCommitOutcome": "models",
            "MergeError": "models",
            "MergeValidationError": "models",
            "_master_revision": "models",
            "MergeEngine": "engine",
        },
        "default": "models",
    },
    "decision_brief": {
        "modules": ["models", "repositories", "service"],
        "descriptions": {
            "models": (
                "domain models, enums, errors and shared validation "
                "helpers for US-13 decision briefs."
            ),
            "repositories": (
                "persistent repositories for approved templates, risk "
                "confirmations and decision brief versions."
            ),
            "service": (
                "DecisionBriefService facade and its private helpers."
            ),
        },
        "targets": {
            "DecisionBriefError": "models",
            "DecisionBriefValidationError": "models",
            "DecisionBriefConflictError": "models",
            "BriefType": "models",
            "BriefSourceKind": "models",
            "SourceReference": "models",
            "BriefConclusion": "models",
            "BriefContent": "models",
            "ApprovedTemplate": "models",
            "RiskConfirmation": "models",
            "WpsDocumentRequest": "models",
            "BriefVersion": "models",
            "DecisionBrief": "models",
            "ApprovedTemplateRegistry": "repositories",
            "RiskConfirmationRepository": "repositories",
            "DecisionBriefRepository": "repositories",
            "DecisionBriefService": "service",
            "_latest_receipt": "models",
            "_validate_bound_risk": "models",
            "_validate_risk_report": "models",
            "_risk_digest": "models",
            "_clone_risk_report": "models",
            "_clone_confirmation": "models",
            "_build_content": "models",
            "_risk_conclusion": "models",
            "_make_version": "models",
            "_version_digest": "models",
            "_version_digest_values": "models",
            "_content_digest": "models",
            "_content_plain": "models",
            "_validate_stored_brief": "models",
            "_validate_content_model": "models",
            "_clone_content": "models",
            "_clone_brief": "models",
            "_brief_id": "models",
            "_stable_sources": "models",
            "_content_sources": "models",
            "_source_sort_key": "models",
            "_validate_template_ref": "models",
            "_validate_docx": "models",
            "_is_link_or_reparse": "models",
            "_stat_is_reparse": "models",
            "_safe_string": "models",
            "_digest": "models",
            "_parse_utc": "models",
            "_encode_json": "models",
        },
        "default": "models",
    },
    "orchestrator": {
        "modules": ["models", "service"],
        "descriptions": {
            "models": (
                "US-4 domain models, enums, errors, registry and "
                "orchestration value objects."
            ),
            "service": (
                "deterministic Orchestrator facade (US-4 AC-3..AC-7)."
            ),
        },
        "targets": {
            "OrchestratorError": "models",
            "OrchestratorValidationError": "models",
            "OrchestratorConflictError": "models",
            "AgentCapability": "models",
            "AgentStatus": "models",
            "OrchestrationStepKind": "models",
            "FailurePolicy": "models",
            "OrchestrationEventKind": "models",
            "OrchestrationStepResult": "models",
            "OrchestrationOutcome": "models",
            "AgentSpec": "models",
            "AgentRegistration": "models",
            "AgentRegistry": "models",
            "OrchestrationStep": "models",
            "OrchestrationChain": "models",
            "OrchestrationEvent": "models",
            "OrchestrationTrace": "models",
            "OrchestrationReport": "models",
            "Orchestrator": "service",
            "_make_trace_id": "models",
            "_make_report_id": "models",
            "_SAFE_ID": "models",
            "_ISO_UTC_Z": "models",
        },
        "default": "models",
        "keep_in_init": ["MVP_FIXED_CHAIN"],
    },
    "progress_capture": {
        "modules": ["models", "service"],
        "descriptions": {
            "models": (
                "US-8 progress-capture domain models, enums, errors "
                "and shared validators."
            ),
            "service": (
                "ProgressCaptureService facade and its private helpers."
            ),
        },
        "targets": {
            "ProgressCaptureError": "models",
            "ProgressCaptureValidationError": "models",
            "ProgressCaptureConflictError": "models",
            "EvidenceKind": "models",
            "ProgressItemKind": "models",
            "ProgressItemStatus": "models",
            "EvidenceInput": "models",
            "EvidenceRef": "models",
            "ItemOverride": "models",
            "ProgressItem": "models",
            "ProgressCapture": "models",
            "ProgressDraft": "models",
            "ProgressCaptureService": "service",
            "_check_non_empty_str": "models",
            "_check_safe_id": "models",
            "_check_hex64": "models",
            "_check_iso_utc": "models",
            "_check_confidence": "models",
            "_classify": "service",
            "_make_item_id": "service",
            "_make_capture_id": "service",
        },
        "default": "models",
    },
    "knowledge_base": {
        "modules": ["models", "facade"],
        "descriptions": {
            "models": (
                "US-14 knowledge-base domain models, enums, errors "
                "and shared validators."
            ),
            "facade": (
                "KnowledgeBaseFacade aggregation and template/retrospective "
                "extraction helpers."
            ),
        },
        "targets": {
            "KnowledgeBaseError": "models",
            "KnowledgeBaseValidationError": "models",
            "ClassificationDenied": "models",
            "ReviewConflictError": "models",
            "KnowledgeClassification": "models",
            "KnowledgeSourceKind": "models",
            "ReusableTemplateKind": "models",
            "ReviewDecisionKind": "models",
            "ReusableTemplate": "models",
            "KnowledgeEntry": "models",
            "ReviewDecision": "models",
            "RetrospectiveDraft": "models",
            "KnowledgeBundle": "models",
            "KnowledgeBaseFacade": "facade",
            "_check_safe_id": "models",
            "_check_iso_utc": "models",
            "_check_class": "models",
            "_make_entry_id": "facade",
            "_make_bundle_id": "facade",
            "_make_template_id": "facade",
            "_rank_to_classification": "facade",
            "_entry_from_baseline": "facade",
            "_entry_from_source": "facade",
            "_source_index": "facade",
            "_extract_reusable_templates": "facade",
            "_generate_retrospective": "facade",
        },
        "default": "models",
    },
    "cockpit": {
        "modules": ["models", "facade"],
        "descriptions": {
            "models": (
                "US-7 cockpit domain models, enums, errors, view "
                "summaries, config/state and the WPS allow list."
            ),
            "facade": (
                "CockpitFacade route dispatch and audit projection."
            ),
        },
        "targets": {
            "CockpitError": "models",
            "CockpitValidationError": "models",
            "CockpitNotFoundError": "models",
            "CockpitRoute": "models",
            "CockpitResponseStatus": "models",
            "TaskSummary": "models",
            "MilestoneSummary": "models",
            "ArtifactSummary": "models",
            "RoleView": "models",
            "WorkspaceView": "models",
            "CockpitRequest": "models",
            "CockpitResponse": "models",
            "CockpitServerConfig": "models",
            "CockpitServerState": "models",
            "WPSAllowList": "models",
            "CockpitFacade": "facade",
            "_hash_path": "models",
            "_SAFE_ID": "models",
            "_ISO_UTC_Z": "models",
            "_HEX_64": "models",
        },
        "default": "models",
        "keep_in_init": ["LOOPBACK_HOST", "STATIC_ROOT"],
    },
    "app": {
        "modules": ["demo_support", "pipeline"],
        "descriptions": {
            "demo_support": (
                "demo-only support: PKI profile bootstrap, in-memory "
                "demo signer/freshness stand-ins and sample inputs. "
                "Explicitly NOT production code."
            ),
            "pipeline": (
                "offline demo pipeline composition root (dispatch chain "
                "E2E) and its result value object."
            ),
        },
        "targets": {
            "ROOT": "demo_support",
            "DEMO_PROFILE": "demo_support",
            "DEMO_REVISION": "demo_support",
            "DEMO_ACTOR": "demo_support",
            "now_utc_iso_z": "demo_support",
            "_DemoAuditAnchorError": "demo_support",
            "DemoSigner": "demo_support",
            "DemoFreshnessAuthority": "demo_support",
            "sample_project_input": "demo_support",
            "ensure_demo_profile": "demo_support",
            "DemoResult": "pipeline",
            "run_demo_pipeline": "pipeline",
        },
        "default": "demo_support",
    },
    "supervision": {
        "modules": ["models", "service"],
        "descriptions": {
            "models": (
                "US-12 supervision/meeting domain models, enums, errors "
                "and shared validators."
            ),
            "service": (
                "SupervisionCoordinator facade and its private helpers."
            ),
        },
        "targets": {
            "SUPERVISION_DOMAIN": "models",
            "SUPERVISION_SCHEMA": "models",
            "MEETING_DOMAIN": "models",
            "MEETING_SCHEMA": "models",
            "SUPERVISABLE_RISK_KINDS": "models",
            "COORDINATION_RECOMMENDED_KINDS": "models",
            "SupervisionError": "models",
            "SupervisionValidationError": "models",
            "EscalationLevel": "models",
            "MeetingConclusionKind": "models",
            "SupervisionItem": "models",
            "EscalationSuggestion": "models",
            "MeetingAgendaItem": "models",
            "MeetingProposal": "models",
            "MeetingConclusionProjection": "models",
            "SupervisionOutcome": "models",
            "SupervisionCoordinator": "service",
            "_closing_condition_for": "service",
            "_escalation_level_for": "service",
            "_escalation_reason_for": "service",
            "_meeting_proposal_for": "service",
            "_agenda_title_for": "service",
            "_conclusions_for": "service",
            "_supervision_item_id": "service",
            "_non_empty": "models",
            "_parse_utc": "models",
        },
        "default": "models",
    },
    "risk": {
        "modules": ["models", "analyzer"],
        "descriptions": {
            "models": (
                "US-11 risk domain models, enums, errors and shared "
                "validation helpers (merged from the former package __init__)."
            ),
            "analyzer": (
                "deterministic RiskAnalyzer facade, merge+analyze hook and "
                "their private helpers (US-11)."
            ),
        },
        "targets": {
            "SourceKind": "models",
            "RiskKind": "models",
            "Risk": "models",
            "RiskReport": "models",
            "RiskAnalysisError": "models",
            "RiskValidationError": "models",
            "MergeAndAnalyzeOutcome": "models",
            "RiskAnalyzer": "analyzer",
            "analyze_after_merge": "analyzer",
            "merge_and_analyze": "analyzer",
            "_validated_receipt": "analyzer",
            "_validated_graph": "analyzer",
            "_descendants": "analyzer",
            "_risk": "analyzer",
            "_plus_days": "analyzer",
            "_non_empty": "models",
            "_parse_utc": "models",
            "_source_kind_counts": "models",
        },
        "default": "models",
    },
    "benchmarks": {
        "modules": ["models", "harness"],
        "descriptions": {
            "models": (
                "SLA target definitions and scalability probes (merged from "
                "the former package __init__)."
            ),
            "harness": (
                "BenchmarkResult, measure() and report() measurement harness."
            ),
        },
        "targets": {
            "SlaTarget": "models",
            "SLA_TARGETS": "models",
            "SCALABILITY_PROBES": "models",
            "BenchmarkResult": "harness",
            "measure": "harness",
            "report": "harness",
        },
        "default": "models",
    },
}


def main() -> int:
    for pkg in sys.argv[1:] or list(CONFIGS):
        split_package(pkg, CONFIGS[pkg])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
