"""Unit tests for src/coevo/task_flow/models.py and mapping.py.

AC test matrix:
  AC-1  ``test_import_*`` — tabular / tree / canonical all produce a draft.
  AC-2  ``test_extracts_*`` — stages/nodes/roles/inputs/outputs/reviews.
  AC-3  ``test_source_mapping_*`` — every parsed field points at an input path.
  AC-4  ``test_traced_*`` — confidence in [0, 1] and SourceKind values.
  AC-5  ``test_overrides_*`` — reviewer's edits become Override entries.
  AC-6  ``test_version_*`` — confirm() bumps integer version, ignores order.
  AC-7  ``test_mapping_*`` — per-unit stage hints land on StandardStage.

Plus negative tests:
  - duplicate ids rejected,
  - unknown format rejected,
  - empty input rejected,
  - schema-missing required fields rejected,
  - confidence out of range rejected,
  - mapping without a matching rule rejected,
  - override on confirmed flow becomes a new flow at version+1.
"""
from __future__ import annotations

import unittest
from pathlib import Path
import importlib.util

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.coevo.task_flow import models, parser, mapping


# --------------------------- AC-1 ---------------------------

class ImportTests(unittest.TestCase):
    def test_import_canonical(self):
        raw = {
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
                    ]}
                ],
                "roles": [{"role_id": "a.role_a", "name": "PM",
                            "responsibility": "Owns intake review"}],
            },
        }
        flow = parser.parse_flow(raw)
        self.assertEqual("unit_a", flow.unit_id)
        self.assertEqual(1, flow.version)

    def test_import_tabular(self):
        raw = {
            "format": "tabular",
            "unit_id": "unit_b",
            "title": "Unit B",
            "columns": ["stage", "node_id", "title", "stage_hint",
                        "inputs", "outputs", "review_criteria", "responsible_roles"],
            "rows": [
                {
                    "stage": "intake",
                    "node_id": "n1", "title": "Receive",
                    "stage_hint": "intake",
                    "inputs": ["req"], "outputs": ["signed"],
                    "review_criteria": ["complete"], "responsible_roles": ["a.pm"],
                },
                {
                    "stage": "closure",
                    "node_id": "n2", "title": "Wrap",
                    "stage_hint": "closure",
                    "inputs": [], "outputs": ["final"],
                    "review_criteria": ["audit"], "responsible_roles": ["a.pm"],
                },
            ],
            "roles": [{"role_id": "a.pm", "name": "PM",
                        "responsibility": "Owns lifecycle"}],
        }
        flow = parser.parse_flow(raw)
        self.assertEqual("unit_b", flow.unit_id)
        self.assertEqual(2, len(flow.stages))

    def test_import_tree(self):
        raw = {
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
        flow = parser.parse_flow(raw)
        self.assertEqual("unit_c", flow.unit_id)


# --------------------------- AC-2 ---------------------------

class ExtractionTests(unittest.TestCase):
    def test_extracts_stages_nodes_roles(self):
        raw = {
            "format": "canonical",
            "flow": {
                "unit_id": "u2", "title": "U2",
                "stages": [
                    {"stage_id": "intake", "name": "intake", "nodes": [
                        {"node_id": "n1", "title": "Receive",
                         "stage_hint": "intake",
                         "inputs": ["req"], "outputs": ["signed"],
                         "review_criteria": ["complete"], "responsible_roles": ["a.pm"]},
                    ]},
                ],
                "roles": [{"role_id": "a.pm", "name": "PM",
                            "responsibility": "Owns intake review"}],
            },
        }
        flow = parser.parse_flow(raw)
        self.assertEqual(1, len(flow.stages))
        s = flow.stages[0]
        self.assertEqual("intake", s.stage_id)
        self.assertEqual(1, len(s.nodes))
        n = s.nodes[0]
        self.assertEqual(("req",), tuple(t.value for t in n.inputs))
        self.assertEqual(("signed",), tuple(t.value for t in n.outputs))
        self.assertEqual(("complete",), tuple(t.value for t in n.review_criteria))
        self.assertEqual(("a.pm",), tuple(t.value for t in n.responsible_roles))
        self.assertEqual(1, len(flow.roles))
        self.assertEqual("a.pm", flow.roles[0].role_id)


# --------------------------- AC-3 ---------------------------

class SourceMappingTests(unittest.TestCase):
    def test_source_mapping_pairs_title(self):
        raw = {
            "format": "canonical",
            "flow": {
                "unit_id": "u3", "title": "U3",
                "stages": [
                    {"stage_id": "intake", "name": "intake", "nodes": [
                        {"node_id": "n1", "title": "Receive",
                         "stage_hint": "intake",
                         "inputs": ["req"], "outputs": ["signed"],
                         "review_criteria": ["complete"], "responsible_roles": ["a.pm"]},
                    ]}
                ],
                "roles": [{"role_id": "a.pm", "name": "PM",
                            "responsibility": "Owns intake"}],
            },
        }
        flow = parser.parse_flow(raw)
        self.assertIsNotNone(flow.source_mapping.get("flow.title"))
        self.assertIsNotNone(flow.source_mapping.get("stages[0].name"))
        self.assertIsNotNone(flow.source_mapping.get("stages[0].nodes[0].title"))


# --------------------------- AC-4 ---------------------------

class TracedTests(unittest.TestCase):
    def test_confidence_in_range(self):
        for bad in (-0.1, 1.01, 2.0):
            with self.assertRaises(models.ProcessFlowError):
                models.Traced("x", "p", bad, models.SourceKind.LITERAL)

    def test_source_kind_values(self):
        flow = parser.parse_flow({
            "format": "canonical",
            "flow": {"unit_id": "u4", "title": "U4", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "Owns intake"}]},
        })
        for s in flow.stages:
            for n in s.nodes:
                self.assertIn(n.stage_hint.source_kind, set(models.SourceKind))


# --------------------------- AC-5 ---------------------------

class OverrideTests(unittest.TestCase):
    def test_reviewers_apply_overrides(self):
        flow = parser.parse_flow({
            "format": "canonical",
            "flow": {"unit_id": "u5", "title": "U5", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "Owns intake"}]},
        })
        override = models.Override(
            target_path="stages[0].nodes[0].title",
            original_value="Receive",
            edited_value="Receive & validate",
            reason="PM clarified acceptance phrasing",
        )
        next_flow = flow.with_overrides((override,), new_created_at="2026-07-25T00:00:00Z")
        self.assertEqual(2, next_flow.version)
        self.assertEqual((override,), next_flow.overrides)

    def test_empty_overrides_rejected(self):
        flow = parser.parse_flow({
            "format": "canonical",
            "flow": {"unit_id": "u6", "title": "U6", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "Owns"}]},
        })
        with self.assertRaises(models.ProcessFlowError):
            flow.with_overrides(tuple(), new_created_at="2026-07-25T00:00:00Z")


# --------------------------- AC-6 ---------------------------

class VersionTests(unittest.TestCase):
    def test_version_is_integer_and_monotonic(self):
        flow = parser.parse_flow({
            "format": "canonical",
            "flow": {"unit_id": "u7", "title": "U7", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "Owns"}]},
        })
        self.assertEqual(1, flow.version)
        override = models.Override("stages[0].nodes[0].title", "Receive", "Receive+", "edit")
        next_flow = flow.with_overrides((override,), new_created_at="2026-07-25T00:00:00Z")
        self.assertEqual(2, next_flow.version)
        self.assertLess(flow.version, next_flow.version)


# --------------------------- AC-7 ---------------------------

class MappingTests(unittest.TestCase):
    def _flow(self):
        return parser.parse_flow({
            "format": "canonical",
            "flow": {"unit_id": "u8", "title": "U8", "stages": [
                {"stage_id": "intake", "name": "intake", "nodes": [
                    {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    {"node_id": "n2", "title": "Plan", "stage_hint": "策划",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    {"node_id": "n3", "title": "Build", "stage_hint": "开发阶段",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    {"node_id": "n4", "title": "QA", "stage_hint": "评审",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    {"node_id": "n5", "title": "Submit", "stage_hint": "验收",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    {"node_id": "n6", "title": "Review", "stage_hint": "复盘",
                     "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                ]}
            ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "Owns"}]},
        })

    def test_default_mapping_resolves_known_hints(self):
        mapped = mapping.apply_mapping(self._flow())
        self.assertEqual(6, len(mapped.nodes))
        stages = {n.node.node_id: n.standard_stage for n in mapped.nodes}
        self.assertEqual(models.StandardStage.INTAKE,   stages["n1"])
        self.assertEqual(models.StandardStage.PLANNING, stages["n2"])
        self.assertEqual(models.StandardStage.EXECUTION, stages["n3"])
        self.assertEqual(models.StandardStage.REVIEW,   stages["n4"])
        self.assertEqual(models.StandardStage.DELIVERY, stages["n5"])
        self.assertEqual(models.StandardStage.CLOSURE,  stages["n6"])

    def test_unknown_hint_rejected(self):
        flow = self._flow()
        # tamper: change a hint to one not in the table
        node0 = flow.stages[0].nodes[0]
        new_node = models.Node(
            node_id=node0.node_id, title=node0.title,
            stage_hint=models.Traced("Nonexistent", "src", 0.5, models.SourceKind.LITERAL),
            inputs=node0.inputs, outputs=node0.outputs,
            review_criteria=node0.review_criteria,
            responsible_roles=node0.responsible_roles,
        )
        new_stage = models.Stage(flow.stages[0].stage_id,
                                  flow.stages[0].name,
                                  (new_node,) + flow.stages[0].nodes[1:])
        bad_flow = models.ProcessFlow(
            unit_id=flow.unit_id, version=flow.version,
            created_at=flow.created_at, title=flow.title,
            stages=(new_stage,), roles=flow.roles,
            source_mapping=flow.source_mapping,
            overrides=flow.overrides,
            mapping_rules_version=flow.mapping_rules_version,
        )
        with self.assertRaises(models.ProcessFlowError):
            mapping.apply_mapping(bad_flow)

    def test_custom_rule_priority_and_tie_break(self):
        # OPTIMIZE-13: custom rules sort by (priority ASC, rule_id ASC);
        # lower priority number wins, ties break on rule_id.
        node = models.Node(
            node_id="n1", title="T",
            stage_hint=models.Traced(
                "custom-hint", "src", 0.9, models.SourceKind.LITERAL,
            ),
            inputs=(), outputs=(), review_criteria=(), responsible_roles=(),
        )
        stage = models.Stage("s1", "S", (node,))
        flow = models.ProcessFlow(
            unit_id="u", version=1, created_at="2026-08-01T00:00:00Z",
            title="T", stages=(stage,), roles=(),
            source_mapping={}, overrides=(), mapping_rules_version=1,
        )

        # Priority: rule.low (10) must beat rule.high (20).
        mapped = mapping.apply_mapping(
            flow,
            rules=(
                models.MappingRule(
                    "rule.high", "custom-hint", models.StandardStage.PLANNING, 20,
                ),
                models.MappingRule(
                    "rule.low", "custom-hint", models.StandardStage.EXECUTION, 10,
                ),
            ),
        )
        self.assertEqual(
            models.StandardStage.EXECUTION, mapped.nodes[0].standard_stage,
        )

        # Tie: same priority -> lexicographically smaller rule_id wins.
        mapped = mapping.apply_mapping(
            flow,
            rules=(
                models.MappingRule(
                    "rule.b", "custom-hint", models.StandardStage.DELIVERY, 5,
                ),
                models.MappingRule(
                    "rule.a", "custom-hint", models.StandardStage.CLOSURE, 5,
                ),
            ),
        )
        self.assertEqual(
            models.StandardStage.CLOSURE, mapped.nodes[0].standard_stage,
        )
        self.assertEqual("rule.a", mapped.nodes[0].rule_id)

    def test_default_rule_table_is_non_empty(self):
        self.assertGreater(len(mapping.DEFAULT_MAPPING_RULES), 0)


# --------------------------- Negative tests ---------------------------

class NegativeTests(unittest.TestCase):
    def test_duplicate_stage_id_rejected(self):
        with self.assertRaises(models.ProcessFlowParseError):
            parser.parse_flow({
                "format": "canonical",
                "flow": {"unit_id": "ux", "title": "X", "stages": [
                    {"stage_id": "intake", "name": "intake", "nodes": [
                        {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                         "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    ]},
                    {"stage_id": "intake", "name": "intake", "nodes": [
                        {"node_id": "n2", "title": "Receive2", "stage_hint": "intake",
                         "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    ]},
                ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "O"}]},
            })

    def test_duplicate_node_id_rejected(self):
        with self.assertRaises(models.ProcessFlowParseError):
            parser.parse_flow({
                "format": "canonical",
                "flow": {"unit_id": "ux2", "title": "X", "stages": [
                    {"stage_id": "intake", "name": "intake", "nodes": [
                        {"node_id": "n1", "title": "Receive", "stage_hint": "intake",
                         "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                        {"node_id": "n1", "title": "Receive2", "stage_hint": "intake",
                         "inputs": [], "outputs": [], "review_criteria": [], "responsible_roles": ["a.pm"]},
                    ]},
                ], "roles": [{"role_id": "a.pm", "name": "PM", "responsibility": "O"}]},
            })

    def test_unknown_format_rejected(self):
        with self.assertRaises(models.ProcessFlowParseError):
            parser.parse_flow({"format": "bogus", "flow": {}, "stages": []})

    def test_empty_stages_rejected(self):
        with self.assertRaises(models.ProcessFlowParseError):
            parser.parse_flow({
                "format": "canonical",
                "flow": {"unit_id": "ux3", "title": "X", "stages": [], "roles": []},
            })

    def test_unknown_tabular_column_rejected(self):
        with self.assertRaises(models.ProcessFlowParseError):
            parser.parse_flow({
                "format": "tabular",
                "unit_id": "ux4", "title": "X",
                "columns": ["stage", "node_id", "title"],
                "rows": [{"stage": "intake", "node_id": "n1", "title": "T", "unknown_col": "boom"}],
                "roles": [],
            })


if __name__ == "__main__":
    unittest.main()
