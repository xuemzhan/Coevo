"""ARCH-REVIEW-10: Go↔Python task-flow mapping parity via shared golden corpus.

The Go port (go/taskflow) and the Python reference (src/coevo/task_flow) must
stay aligned. Both sides consume the SAME golden corpus
(go/taskflow/testdata/mapping-rules.json); this test is the Python half and
go/taskflow/parity_test.go is the Go half. Any rule-table or behavior drift
fails the corresponding suite. Contract: docs/architecture/go-python-parity.md.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.task_flow.mapping import DEFAULT_MAPPING_RULES, apply_mapping
from src.coevo.task_flow.models import (
    Node,
    ProcessFlow,
    ProcessFlowError,
    SourceKind,
    SourceMapping,
    Stage,
    Traced,
)

CORPUS = ROOT / "go" / "taskflow" / "testdata" / "mapping-rules.json"


def _load_corpus() -> dict:
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def _parity_flow(hint, duplicate: bool = False) -> ProcessFlow:
    node = Node(
        node_id="n1",
        title="T",
        stage_hint=Traced(
            hint, "stages[0].nodes[0].stage_hint", 1.0, SourceKind.LITERAL
        ),
        inputs=(),
        outputs=(),
        review_criteria=(),
        responsible_roles=(),
    )
    stages = [Stage(stage_id="s1", name="S", nodes=(node,))]
    if duplicate:
        stages.append(Stage(stage_id="s2", name="S2", nodes=(node,)))
    return ProcessFlow(
        unit_id="parity",
        version=1,
        created_at="2026-08-10T00:00:00Z",
        title=Traced("Parity", "flow.title", 1.0, SourceKind.LITERAL),
        stages=tuple(stages),
        roles=(),
        source_mapping=SourceMapping(entries=()),
        overrides=(),
    )


class GoPythonParityTests(unittest.TestCase):
    def test_corpus_exists_and_source_of_truth(self) -> None:
        self.assertTrue(CORPUS.is_file(), "golden corpus missing")
        corpus = _load_corpus()
        self.assertEqual(corpus["source_of_truth"], "src/coevo/task_flow/mapping.py")
        self.assertEqual(corpus["rule_count"], len(DEFAULT_MAPPING_RULES))

    def test_default_rules_match_corpus(self) -> None:
        corpus = _load_corpus()
        by_id = {rule.rule_id: rule for rule in DEFAULT_MAPPING_RULES}
        self.assertEqual(len(by_id), len(DEFAULT_MAPPING_RULES))
        for want in corpus["rules"]:
            rule = by_id.get(want["rule_id"])
            self.assertIsNotNone(rule, f"rule {want['rule_id']} missing in Python")
            self.assertEqual(rule.unit_stage_hint, want["hint"])
            self.assertEqual(rule.standard_stage.value, want["standard_stage"])
            self.assertEqual(rule.priority, want["priority"])

    def test_mapping_cases_match_corpus(self) -> None:
        corpus = _load_corpus()
        for case in corpus["cases"]:
            if case.get("non_string_hint"):
                with self.assertRaises(ProcessFlowError):
                    apply_mapping(_parity_flow(123))
            elif case.get("duplicate_node"):
                with self.assertRaises(ProcessFlowError):
                    apply_mapping(_parity_flow("intake", duplicate=True))
            elif case.get("expected_error"):
                with self.assertRaises(ProcessFlowError):
                    apply_mapping(_parity_flow(case["hint"]))
            else:
                mapped = apply_mapping(_parity_flow(case["hint"]))
                self.assertEqual(len(mapped.nodes), 1)
                self.assertEqual(
                    mapped.nodes[0].standard_stage.value, case["expected_stage"]
                )
                self.assertEqual(mapped.nodes[0].rule_id, case["expected_rule_id"])


if __name__ == "__main__":
    unittest.main()
