package taskflow

import (
	"fmt"
	"testing"
)

func sampleFlow(t *testing.T, hints ...string) ProcessFlow {
	t.Helper()
	nodes := make([]Node, 0, len(hints))
	for i, hint := range hints {
		nodes = append(nodes, Node{
			NodeID:    fmt.Sprintf("n%d", i+1),
			Title:     "T",
			StageHint: mustTraced(t, hint, fmt.Sprintf("stages[0].nodes[%d].stage_hint", i), 0.85, SourceKindLiteral),
		})
	}
	return NewProcessFlow("u8", 1, "2026-08-01T00:00:00Z",
		mustTraced(t, "U8", "flow.title", 0.95, SourceKindLiteral),
		[]Stage{{StageID: "intake", Name: "intake", Nodes: nodes}},
		nil, SourceMapping{}, nil)
}

func TestDefaultMappingResolvesKnownHints(t *testing.T) {
	flow := sampleFlow(t, "intake", "策划", "开发阶段", "评审", "验收", "复盘")
	mapped, err := ApplyMapping(flow, nil)
	if err != nil {
		t.Fatalf("ApplyMapping: %v", err)
	}
	if len(mapped.Nodes) != 6 {
		t.Fatalf("expected 6 mapped nodes, got %d", len(mapped.Nodes))
	}
	got := map[string]StandardStage{}
	for _, node := range mapped.Nodes {
		got[node.Node.NodeID] = node.StandardStage
	}
	want := map[string]StandardStage{
		"n1": StandardStageIntake,
		"n2": StandardStagePlanning,
		"n3": StandardStageExecution,
		"n4": StandardStageReview,
		"n5": StandardStageDelivery,
		"n6": StandardStageClosure,
	}
	for id, stage := range want {
		if got[id] != stage {
			t.Errorf("node %s: expected %s, got %s", id, stage, got[id])
		}
	}
	if mapped.UnitID != "u8" || mapped.Version != 1 {
		t.Errorf("mapped flow metadata mismatch: %+v", mapped)
	}
}

func TestUnknownHintRejected(t *testing.T) {
	flow := sampleFlow(t, "Nonexistent")
	if _, err := ApplyMapping(flow, nil); err == nil {
		t.Fatal("expected unknown stage hint to fail closed")
	}
}

func TestCustomRulePriorityAndTieBreak(t *testing.T) {
	node := Node{NodeID: "n1", Title: "T", StageHint: mustTraced(t, "custom-hint", "src", 0.9, SourceKindLiteral)}
	stage := Stage{StageID: "s1", Name: "S", Nodes: []Node{node}}
	flow := NewProcessFlow("u", 1, "2026-08-01T00:00:00Z",
		mustTraced(t, "T", "flow.title", 0.95, SourceKindLiteral),
		[]Stage{stage}, nil, SourceMapping{}, nil)

	// Priority: rule.low (10) must beat rule.high (20).
	mapped, err := ApplyMapping(flow, []MappingRule{
		{RuleID: "rule.high", UnitStageHint: "custom-hint", StandardStage: StandardStagePlanning, Priority: 20},
		{RuleID: "rule.low", UnitStageHint: "custom-hint", StandardStage: StandardStageExecution, Priority: 10},
	})
	if err != nil {
		t.Fatalf("ApplyMapping: %v", err)
	}
	if mapped.Nodes[0].StandardStage != StandardStageExecution {
		t.Errorf("expected EXECUTION (lower priority wins), got %s", mapped.Nodes[0].StandardStage)
	}

	// Tie: same priority -> lexicographically smaller rule_id wins.
	mapped, err = ApplyMapping(flow, []MappingRule{
		{RuleID: "rule.b", UnitStageHint: "custom-hint", StandardStage: StandardStageDelivery, Priority: 5},
		{RuleID: "rule.a", UnitStageHint: "custom-hint", StandardStage: StandardStageClosure, Priority: 5},
	})
	if err != nil {
		t.Fatalf("ApplyMapping: %v", err)
	}
	if mapped.Nodes[0].StandardStage != StandardStageClosure || mapped.Nodes[0].RuleID != "rule.a" {
		t.Errorf("expected CLOSURE from rule.a, got stage=%s rule=%s", mapped.Nodes[0].StandardStage, mapped.Nodes[0].RuleID)
	}
}

func TestEmptyRulesRejectedAndNilUsesDefaults(t *testing.T) {
	if _, err := ApplyMapping(sampleFlow(t, "intake"), []MappingRule{}); err == nil {
		t.Fatal("expected an explicit empty rule table to fail closed")
	}
	mapped, err := ApplyMapping(sampleFlow(t, "intake"), nil)
	if err != nil {
		t.Fatalf("nil rules must fall back to defaults: %v", err)
	}
	if mapped.Nodes[0].StandardStage != StandardStageIntake {
		t.Errorf("expected INTAKE via default rules, got %s", mapped.Nodes[0].StandardStage)
	}
}

func TestUnsupportedMappingRulesVersionRejected(t *testing.T) {
	flow := sampleFlow(t, "intake")
	flow.MappingRulesVersion = 2
	if _, err := ApplyMapping(flow, nil); err == nil {
		t.Fatal("expected mapping_rules_version 2 to fail closed")
	}
}

func TestDuplicateNodeKeyRejected(t *testing.T) {
	node := Node{NodeID: "n1", Title: "T", StageHint: mustTraced(t, "intake", "src", 0.85, SourceKindLiteral)}
	flow := NewProcessFlow("u", 1, "2026-08-01T00:00:00Z",
		mustTraced(t, "T", "flow.title", 0.95, SourceKindLiteral),
		[]Stage{
			{StageID: "s1", Name: "S1", Nodes: []Node{node}},
			{StageID: "s2", Name: "S2", Nodes: []Node{node}},
		},
		nil, SourceMapping{}, nil)
	if _, err := ApplyMapping(flow, nil); err == nil {
		t.Fatal("expected duplicate unit:node key to fail closed")
	}
}

func TestMappedNodesPreserveStageAndNodeOrder(t *testing.T) {
	flow := sampleFlow(t, "intake", "intake", "intake")
	mapped, err := ApplyMapping(flow, nil)
	if err != nil {
		t.Fatalf("ApplyMapping: %v", err)
	}
	if len(mapped.Nodes) != 3 {
		t.Fatalf("expected 3 mapped nodes, got %d", len(mapped.Nodes))
	}
	for i, node := range mapped.Nodes {
		wantID := fmt.Sprintf("n%d", i+1)
		if node.Node.NodeID != wantID {
			t.Errorf("node %d: expected %s, got %s", i, wantID, node.Node.NodeID)
		}
	}
}
