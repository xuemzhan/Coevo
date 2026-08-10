// Parity tests: this package MUST stay aligned with the Python reference
// implementation (src/coevo/task_flow/mapping.py). The shared golden corpus in
// testdata/mapping-rules.json is consumed by BOTH this test and
// tests/unit/test_arch_review_10_go_python_parity.py, so a drift on either
// side fails the corresponding suite. See docs/architecture/go-python-parity.md.
package taskflow

import (
	"encoding/json"
	"os"
	"testing"
)

type goldenCorpus struct {
	SchemaVersion string       `json:"schema_version"`
	SourceOfTruth string       `json:"source_of_truth"`
	RuleCount     int          `json:"rule_count"`
	Rules         []goldenRule `json:"rules"`
	Cases         []goldenCase `json:"cases"`
}

type goldenRule struct {
	RuleID        string `json:"rule_id"`
	Hint          string `json:"hint"`
	StandardStage string `json:"standard_stage"`
	Priority      int    `json:"priority"`
}

type goldenCase struct {
	Hint           string `json:"hint"`
	ExpectedStage  string `json:"expected_stage,omitempty"`
	ExpectedRuleID string `json:"expected_rule_id,omitempty"`
	NonStringHint  bool   `json:"non_string_hint,omitempty"`
	DuplicateNode  bool   `json:"duplicate_node,omitempty"`
	ExpectedError  bool   `json:"expected_error,omitempty"`
}

func loadGoldenCorpus(t *testing.T) goldenCorpus {
	t.Helper()
	raw, err := os.ReadFile("testdata/mapping-rules.json")
	if err != nil {
		t.Fatalf("read golden corpus: %v", err)
	}
	var corpus goldenCorpus
	if err := json.Unmarshal(raw, &corpus); err != nil {
		t.Fatalf("parse golden corpus: %v", err)
	}
	return corpus
}

func parityFlow(t *testing.T, hint any, duplicate bool) ProcessFlow {
	t.Helper()
	node := Node{
		NodeID: "n1",
		Title:  "T",
		StageHint: Traced{
			Value:      hint,
			SourcePath: "stages[0].nodes[0].stage_hint",
			Confidence: 1.0,
			SourceKind: SourceKindLiteral,
		},
	}
	stages := []Stage{{StageID: "s1", Name: "S", Nodes: []Node{node}}}
	if duplicate {
		stages = append(stages, Stage{StageID: "s2", Name: "S2", Nodes: []Node{node}})
	}
	return NewProcessFlow(
		"parity",
		1,
		"2026-08-10T00:00:00Z",
		Traced{Value: "Parity", SourcePath: "flow.title", Confidence: 1.0, SourceKind: SourceKindLiteral},
		stages,
		nil,
		SourceMapping{},
		nil,
	)
}

func TestGoldenCorpusRulesMatchPython(t *testing.T) {
	corpus := loadGoldenCorpus(t)
	rules := DefaultMappingRules()
	if corpus.RuleCount != len(rules) {
		t.Fatalf("rule count mismatch: corpus=%d go=%d", corpus.RuleCount, len(rules))
	}
	if corpus.SourceOfTruth != "src/coevo/task_flow/mapping.py" {
		t.Fatalf("source_of_truth changed: %q", corpus.SourceOfTruth)
	}
	for _, want := range corpus.Rules {
		var match *MappingRule
		for i := range rules {
			if rules[i].RuleID == want.RuleID {
				match = &rules[i]
				break
			}
		}
		if match == nil {
			t.Errorf("rule %s missing in Go table", want.RuleID)
			continue
		}
		if match.UnitStageHint != want.Hint ||
			match.StandardStage.String() != want.StandardStage ||
			match.Priority != want.Priority {
			t.Errorf("rule %s drift: go=%+v corpus=%+v", want.RuleID, *match, want)
		}
	}
	if len(rules) != len(corpus.Rules) {
		t.Errorf("extra rules in Go table: go=%d corpus=%d", len(rules), len(corpus.Rules))
	}
}

func TestGoldenCorpusCasesMatchPython(t *testing.T) {
	corpus := loadGoldenCorpus(t)
	for _, tc := range corpus.Cases {
		switch {
		case tc.NonStringHint:
			if _, err := ApplyMapping(parityFlow(t, 123, false), nil); err == nil {
				t.Error("case non_string_hint: expected fail-closed error, got success")
			}
		case tc.DuplicateNode:
			if _, err := ApplyMapping(parityFlow(t, "intake", true), nil); err == nil {
				t.Error("case duplicate_node: expected fail-closed error, got success")
			}
		case tc.ExpectedError:
			if _, err := ApplyMapping(parityFlow(t, tc.Hint, false), nil); err == nil {
				t.Errorf("case %q: expected fail-closed error, got success", tc.Hint)
			}
		default:
			mapped, err := ApplyMapping(parityFlow(t, tc.Hint, false), nil)
			if err != nil {
				t.Errorf("case %q: ApplyMapping failed: %v", tc.Hint, err)
				continue
			}
			if len(mapped.Nodes) != 1 {
				t.Errorf("case %q: expected 1 mapped node, got %d", tc.Hint, len(mapped.Nodes))
				continue
			}
			if mapped.Nodes[0].StandardStage.String() != tc.ExpectedStage {
				t.Errorf("case %q: stage mismatch: got %s want %s", tc.Hint, mapped.Nodes[0].StandardStage, tc.ExpectedStage)
			}
			if mapped.Nodes[0].RuleID != tc.ExpectedRuleID {
				t.Errorf("case %q: rule mismatch: got %s want %s", tc.Hint, mapped.Nodes[0].RuleID, tc.ExpectedRuleID)
			}
		}
	}
}
