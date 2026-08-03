"""Unit tests for US-1-AC-2 service layer (src/coevo/task_flow/service.py).

Coverage matrix (each test method asserts one AC of the service slice):

  AC-2/S1  ``test_service_*`` — end-to-end over canonical / tabular / tree.
  AC-2/S2  ``test_graph_*`` — stage order + node adjacency are deterministic.
  AC-2/S3  ``test_reviewer_view_*`` — source_mapping lookup + confidence.
  AC-2/S4  ``test_confirm_*`` — overrides bump version; empty rejected.
  AC-2/S5  ``test_audit_record_*`` — deterministic, JSON-safe, no PII.
  AC-2/S6  ``test_failure_paths_*`` — bad schema / unknown format / parser
            errors all surface as TaskFlowValidationError.

Service-layer invariants:
* No IO, no network, no model call.
* Stage graph is deterministic regardless of input ordering.
* All exceptions are subclasses of ProcessFlowError (fail-closed).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.task_flow import (
    DEFAULT_MAPPING_RULES,
    FlowUnderstanding,
    FlowUnderstandingService,
    MappingRule,
    Node,
    Override,
    ProcessFlow,
    ProcessFlowError,
    ProcessFlowParseError,
    ReviewerView,
    Role,
    SourceKind,
    StandardStage,
    StageGraph,
    TaskFlowValidationError,
    Traced,
    models,
)


# ----------------------- fixtures -----------------------


_CANONICAL = {
    "format": "canonical",
    "flow": {
        "unit_id": "unit_a",
        "title": "Unit A process",
        "stages": [
            {"stage_id": "intake", "name": "intake", "nodes": [
                {"node_id": "n1", "title": "Receive requirement",
                 "stage_hint": "intake",
                 "inputs": ["requirement_doc"], "outputs": ["signed_doc"],
                 "review_criteria": ["completeness"],
                 "responsible_roles": ["a.role_a"]},
            ]},
            {"stage_id": "execution", "name": "execution", "nodes": [
                {"node_id": "n2", "title": "Develop",
                 "stage_hint": "开发阶段",
                 "inputs": ["signed_doc"], "outputs": ["code"],
                 "review_criteria": ["unit_tests"],
                 "responsible_roles": ["a.role_a"]},
            ]},
            {"stage_id": "delivery", "name": "delivery", "nodes": [
                {"node_id": "n3", "title": "Submit",
                 "stage_hint": "验收",
                 "inputs": ["code"], "outputs": ["release"],
                 "review_criteria": ["signoff"],
                 "responsible_roles": ["a.role_a"]},
            ]},
        ],
        "roles": [{"role_id": "a.role_a", "name": "PM",
                    "responsibility": "Owns intake review"}],
    },
}


_TABULAR = {
    "format": "tabular",
    "unit_id": "unit_b",
    "title": "Unit B",
    "columns": ["stage", "node_id", "title", "stage_hint",
                "inputs", "outputs", "review_criteria", "responsible_roles"],
    "rows": [
        {"stage": "intake", "node_id": "n1", "title": "Receive",
         "stage_hint": "intake",
         "inputs": ["req"], "outputs": ["signed"],
         "review_criteria": ["complete"], "responsible_roles": ["a.pm"]},
        {"stage": "planning", "node_id": "n2", "title": "Plan",
         "stage_hint": "策划",
         "inputs": [], "outputs": ["plan"],
         "review_criteria": ["signoff"], "responsible_roles": ["a.pm"]},
        {"stage": "execution", "node_id": "n3", "title": "Build",
         "stage_hint": "实施",
         "inputs": ["plan"], "outputs": ["artifact"],
         "review_criteria": ["unit_tests"], "responsible_roles": ["a.pm"]},
    ],
    "roles": [{"role_id": "a.pm", "name": "PM",
                "responsibility": "Owns lifecycle"}],
}


_TREE = {
    "format": "tree",
    "unit_id": "unit_c",
    "title": "Unit C",
    "root": {
        "name": "intake",
        "children": [],
        "nodes": [
            {"id": "n1", "title": "Receive",
             "stage_hint": "intake",
             "inputs": ["req"], "outputs": ["signed"],
             "review_criteria": ["complete"], "responsible_roles": ["a.pm"]},
        ],
    },
    "roles": [{"role_id": "a.pm", "name": "PM",
                "responsibility": "Owns lifecycle"}],
}


# ----------------------- AC-2/S1: end-to-end -----------------------


class ServiceEndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FlowUnderstandingService()

    def test_service_canonical_schema_produces_understanding(self):
        result = self.service.understand(_CANONICAL)
        self.assertIsInstance(result, FlowUnderstanding)
        self.assertEqual("unit_a", result.flow.unit_id)
        self.assertEqual(1, result.flow.version)
        # 3 stages x 1 node each, all mapped
        self.assertEqual(3, len(result.graph.stage_ids_in_order))
        self.assertEqual(3, len(result.mapped.nodes))

    def test_service_tabular_schema_produces_understanding(self):
        result = self.service.understand(_TABULAR)
        self.assertEqual("unit_b", result.flow.unit_id)
        self.assertEqual(3, len(result.mapped.nodes))
        standard_by_node = {n.node.node_id: n.standard_stage for n in result.mapped.nodes}
        self.assertEqual(StandardStage.INTAKE,   standard_by_node["n1"])
        self.assertEqual(StandardStage.PLANNING, standard_by_node["n2"])
        self.assertEqual(StandardStage.EXECUTION, standard_by_node["n3"])

    def test_service_tree_schema_produces_understanding(self):
        result = self.service.understand(_TREE)
        self.assertEqual("unit_c", result.flow.unit_id)
        self.assertEqual(1, len(result.mapped.nodes))

    def test_service_returns_four_components(self):
        result = self.service.understand(_CANONICAL)
        self.assertIsInstance(result.flow, ProcessFlow)
        self.assertIsInstance(result.graph, StageGraph)
        self.assertIsInstance(result.reviewer_view, ReviewerView)


# ----------------------- AC-2/S2: graph -----------------------


class StageGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FlowUnderstandingService()
        self.result = self.service.understand(_CANONICAL)

    def test_graph_stage_order_preserved(self):
        self.assertEqual(("intake", "execution", "delivery"),
                         self.result.graph.stage_ids_in_order)

    def test_graph_node_to_stage_lookup(self):
        self.assertEqual("intake",    self.result.graph.stage_id_for_node("n1"))
        self.assertEqual("execution", self.result.graph.stage_id_for_node("n2"))
        self.assertEqual("delivery",  self.result.graph.stage_id_for_node("n3"))
        self.assertIsNone(self.result.graph.stage_id_for_node("n_unknown"))

    def test_graph_nodes_in_stage(self):
        self.assertEqual(("n1",), self.result.graph.nodes_in_stage("intake"))
        self.assertEqual(tuple(), self.result.graph.nodes_in_stage("nonexistent"))

    def test_graph_standard_stage_for_node(self):
        self.assertEqual(StandardStage.INTAKE,    self.result.graph.standard_stage_for("n1"))
        self.assertEqual(StandardStage.EXECUTION, self.result.graph.standard_stage_for("n2"))
        self.assertEqual(StandardStage.DELIVERY,  self.result.graph.standard_stage_for("n3"))

    def test_graph_is_deterministic_across_repeated_calls(self):
        a = self.service.understand(_CANONICAL)
        b = self.service.understand(_CANONICAL)
        self.assertEqual(a.graph.stage_ids_in_order, b.graph.stage_ids_in_order)
        self.assertEqual(a.graph.node_to_stage, b.graph.node_to_stage)


# ----------------------- AC-2/S3: reviewer view -----------------------


class ReviewerViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FlowUnderstandingService()
        self.result = self.service.understand(_CANONICAL)

    def test_source_mapping_lookup_returns_input_path(self):
        # flow.title was recorded under flow.title by parser
        self.assertIsNotNone(self.result.reviewer_view.source_mapping_lookup("flow.title"))
        # node title is mapped to its source via parser's table
        self.assertIsNotNone(
            self.result.reviewer_view.source_mapping_lookup("stages[0].nodes[0].title")
        )

    def test_source_mapping_lookup_returns_none_for_missing(self):
        self.assertIsNone(
            self.result.reviewer_view.source_mapping_lookup("nonexistent.path")
        )

    def test_confidence_in_range(self):
        title_conf = self.result.reviewer_view.confidence_for("stages[0].nodes[0].title")
        self.assertIsNotNone(title_conf)
        self.assertGreaterEqual(title_conf, 0.0)
        self.assertLessEqual(title_conf, 1.0)
        # explicit: parser stamps node titles with 0.95 confidence
        self.assertAlmostEqual(0.95, title_conf, places=6)

    def test_confidence_for_unknown_path_is_none(self):
        self.assertIsNone(
            self.result.reviewer_view.confidence_for("nonexistent.path")
        )


# ----------------------- AC-2/S4: confirm -----------------------


class ConfirmTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FlowUnderstandingService()
        self.result = self.service.understand(_CANONICAL)

    def test_confirm_with_overrides_bumps_version(self):
        flow_v1 = self.result.flow
        override = Override(
            target_path="stages[0].nodes[0].title",
            original_value="Receive requirement",
            edited_value="Receive & validate",
            reason="PM clarified acceptance phrasing",
        )
        flow_v2 = self.service.confirm(
            flow_v1, (override,), new_created_at="2026-07-25T01:00:00Z"
        )
        self.assertEqual(2, flow_v2.version)
        self.assertEqual((override,), flow_v2.overrides)
        self.assertGreater(flow_v2.version, flow_v1.version)

    def test_confirm_empty_overrides_rejected(self):
        with self.assertRaises(TaskFlowValidationError):
            self.service.confirm(self.result.flow, tuple(), new_created_at="2026-07-25T01:00:00Z")

    def test_confirm_empty_created_at_rejected(self):
        override = Override("x", "y", "z", "r")
        with self.assertRaises(TaskFlowValidationError):
            self.service.confirm(self.result.flow, (override,), new_created_at="")


# ----------------------- AC-2/S5: audit record -----------------------


class AuditRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FlowUnderstandingService()
        self.result = self.service.understand(_CANONICAL)

    def test_audit_record_is_json_safe(self):
        record = self.service.to_audit_record(self.result)
        # JSON-safe means json.dumps succeeds with no default
        s = json.dumps(record)
        self.assertIsInstance(s, str)
        # round-trip
        self.assertEqual(record, json.loads(s))

    def test_audit_record_excludes_sensitive_fields(self):
        record = self.service.to_audit_record(self.result)
        # No role responsibility texts, no raw input, no node titles
        self.assertNotIn("responsibility", record)
        self.assertNotIn("title", record)
        self.assertNotIn("stages", record)
        # structural facts are present
        self.assertEqual("unit_a", record["unit_id"])
        self.assertEqual(1,        record["version"])
        self.assertEqual(3,        record["stage_count"])
        self.assertEqual(3,        record["node_count"])
        self.assertEqual(1,        record["role_count"])
        self.assertIn("task_flow.understanding", record["kind"])
        self.assertEqual("1.0",    record["schema_version"])

    def test_audit_record_has_sorted_standard_stage_set(self):
        record = self.service.to_audit_record(self.result)
        # INTAKE / EXECUTION / DELIVERY
        self.assertEqual(["delivery", "execution", "intake"], record["standard_stage_set"])

    def test_audit_record_override_count_tracks_flow(self):
        record_v1 = self.service.to_audit_record(self.result)
        self.assertEqual(0, record_v1["override_count"])
        # Re-parse with override
        flow_v2 = self.service.confirm(
            self.result.flow,
            (Override("p", "o", "e", "r"),),
            "2026-07-25T01:00:00Z",
        )
        # Build a synthetic FlowUnderstanding from the confirmed flow.
        # We do this manually here to exercise the override_count branch
        # without bypassing the service's confirm path.
        from src.coevo.task_flow.mapping import apply_mapping
        remapped = apply_mapping(flow_v2)
        from src.coevo.task_flow.service import FlowUnderstandingService as _S
        graph = _S._build_graph(flow_v2, remapped)
        reviewer = _S._build_reviewer_view(flow_v2)
        result_v2 = FlowUnderstanding(
            flow=flow_v2, mapped=remapped, graph=graph, reviewer_view=reviewer
        )
        record_v2 = self.service.to_audit_record(result_v2)
        self.assertEqual(1, record_v2["override_count"])
        self.assertEqual(2, record_v2["version"])


# ----------------------- AC-2/S6: failure paths -----------------------


class FailurePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FlowUnderstandingService()

    def test_non_mapping_input_rejected(self):
        with self.assertRaises(TaskFlowValidationError):
            self.service.understand("not a mapping")  # type: ignore[arg-type]

    def test_unknown_schema_rejected(self):
        with self.assertRaises(TaskFlowValidationError):
            self.service.understand({"format": "bogus"})

    def test_missing_format_rejected(self):
        with self.assertRaises(TaskFlowValidationError):
            self.service.understand({"flow": {}})

    def test_parser_error_wrapped_in_service_error(self):
        # Parser will reject duplicate node_ids.
        bad = {
            "format": "canonical",
            "flow": {"unit_id": "u", "title": "U", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "t", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [],
                     "responsible_roles": ["a.pm"]},
                    {"node_id": "n1", "title": "t2", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [],
                     "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "o"}]},
        }
        with self.assertRaises(TaskFlowValidationError):
            self.service.understand(bad)

    def test_empty_rule_table_rejected_at_construction(self):
        with self.assertRaises(TaskFlowValidationError):
            FlowUnderstandingService(rules=tuple())

    def test_unknown_hint_in_mapping_wrapped(self):
        bad = {
            "format": "canonical",
            "flow": {"unit_id": "u", "title": "U", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "t", "stage_hint": "NotInTable",
                     "inputs": [], "outputs": [], "review_criteria": [],
                     "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "o"}]},
        }
        with self.assertRaises(TaskFlowValidationError):
            self.service.understand(bad)

    def test_task_flow_validation_error_is_subclass_of_process_flow_error(self):
        # Caller code that catches ProcessFlowError continues to work.
        err = TaskFlowValidationError("x")
        self.assertIsInstance(err, ProcessFlowError)


if __name__ == "__main__":
    unittest.main()