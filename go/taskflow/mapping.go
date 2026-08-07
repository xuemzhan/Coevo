// US-1 stage mapping (AC-7; Go port of src/coevo/task_flow/mapping.py).
//
// Per-unit flow nodes carry an arbitrary StageHint string. The system has a
// closed set of standardized stages (StandardStage) that all UI and
// orchestration code speaks. This file turns a per-unit hint into a
// StandardStage using a deterministic, versioned rule table.
package taskflow

import (
	"fmt"
	"sort"
)

// MappedNode is a per-unit node with its standardized stage attached.
type MappedNode struct {
	Node          Node
	StandardStage StandardStage
	RuleID        string
}

// MappedFlow is the mapped view of a ProcessFlow used by downstream slices.
type MappedFlow struct {
	UnitID  string
	Version int
	Nodes   []MappedNode
}

// DefaultMappingRules returns a defensive copy of the version-1 default rule
// table (27 rules, identical to Python DEFAULT_MAPPING_RULES).
func DefaultMappingRules() []MappingRule {
	return append([]MappingRule(nil), defaultMappingRules...)
}

// defaultMappingRules mirrors Python mapping.DEFAULT_MAPPING_RULES exactly:
// lower Priority wins ties; RuleID is the secondary key.
var defaultMappingRules = []MappingRule{
	{RuleID: "m1", UnitStageHint: "intake", StandardStage: StandardStageIntake, Priority: 10},
	{RuleID: "m2", UnitStageHint: "Intake", StandardStage: StandardStageIntake, Priority: 11},
	{RuleID: "m3", UnitStageHint: "接收", StandardStage: StandardStageIntake, Priority: 12},
	{RuleID: "m4", UnitStageHint: "接收阶段", StandardStage: StandardStageIntake, Priority: 13},
	{RuleID: "m10", UnitStageHint: "planning", StandardStage: StandardStagePlanning, Priority: 10},
	{RuleID: "m11", UnitStageHint: "Planning", StandardStage: StandardStagePlanning, Priority: 11},
	{RuleID: "m12", UnitStageHint: "策划", StandardStage: StandardStagePlanning, Priority: 12},
	{RuleID: "m13", UnitStageHint: "方案策划", StandardStage: StandardStagePlanning, Priority: 13},
	{RuleID: "m20", UnitStageHint: "execution", StandardStage: StandardStageExecution, Priority: 10},
	{RuleID: "m21", UnitStageHint: "Execution", StandardStage: StandardStageExecution, Priority: 11},
	{RuleID: "m22", UnitStageHint: "执行", StandardStage: StandardStageExecution, Priority: 12},
	{RuleID: "m23", UnitStageHint: "实施", StandardStage: StandardStageExecution, Priority: 13},
	{RuleID: "m24", UnitStageHint: "开发阶段", StandardStage: StandardStageExecution, Priority: 14},
	{RuleID: "m30", UnitStageHint: "review", StandardStage: StandardStageReview, Priority: 10},
	{RuleID: "m31", UnitStageHint: "Review", StandardStage: StandardStageReview, Priority: 11},
	{RuleID: "m32", UnitStageHint: "审核", StandardStage: StandardStageReview, Priority: 12},
	{RuleID: "m33", UnitStageHint: "评审", StandardStage: StandardStageReview, Priority: 13},
	{RuleID: "m40", UnitStageHint: "delivery", StandardStage: StandardStageDelivery, Priority: 10},
	{RuleID: "m41", UnitStageHint: "Delivery", StandardStage: StandardStageDelivery, Priority: 11},
	{RuleID: "m42", UnitStageHint: "交付", StandardStage: StandardStageDelivery, Priority: 12},
	{RuleID: "m43", UnitStageHint: "验收", StandardStage: StandardStageDelivery, Priority: 13},
	{RuleID: "m44", UnitStageHint: "提交", StandardStage: StandardStageDelivery, Priority: 14},
	{RuleID: "m50", UnitStageHint: "closure", StandardStage: StandardStageClosure, Priority: 10},
	{RuleID: "m51", UnitStageHint: "Closure", StandardStage: StandardStageClosure, Priority: 11},
	{RuleID: "m52", UnitStageHint: "收尾", StandardStage: StandardStageClosure, Priority: 12},
	{RuleID: "m53", UnitStageHint: "结束", StandardStage: StandardStageClosure, Priority: 13},
	{RuleID: "m54", UnitStageHint: "复盘", StandardStage: StandardStageClosure, Priority: 14},
}

// ApplyMapping maps every node in flow to a StandardStage using rules, or the
// default rule table when rules is nil. Behavior mirrors the Python
// apply_mapping:
//
//   * rules are sorted by (Priority ASC, RuleID ASC); the first rule per hint
//     wins by construction;
//   * each node resolves its hint with a single O(1) lookup;
//   * unknown hints and duplicate unit:node keys fail closed;
//   * only mapping_rules_version 1 is supported.
func ApplyMapping(flow ProcessFlow, rules []MappingRule) (MappedFlow, error) {
	if rules == nil {
		rules = DefaultMappingRules()
	}
	if len(rules) == 0 {
		return MappedFlow{}, Errorf("mapping rule table must be non-empty")
	}
	sorted := append([]MappingRule(nil), rules...)
	sort.Slice(sorted, func(i, j int) bool {
		if sorted[i].Priority != sorted[j].Priority {
			return sorted[i].Priority < sorted[j].Priority
		}
		return sorted[i].RuleID < sorted[j].RuleID
	})
	bestByHint := make(map[string]MappingRule, len(sorted))
	for _, rule := range sorted {
		if _, ok := bestByHint[rule.UnitStageHint]; !ok {
			bestByHint[rule.UnitStageHint] = rule
		}
	}

	seen := make(map[string]struct{})
	var nodes []MappedNode
	for _, stage := range flow.Stages {
		for _, node := range stage.Nodes {
			hintValue, ok := node.StageHint.Value.(string)
			if !ok {
				return MappedFlow{}, Errorf("stage_hint must be a string for node %q in unit %q", node.NodeID, flow.UnitID)
			}
			rule, ok := bestByHint[hintValue]
			if !ok {
				return MappedFlow{}, Errorf("no mapping rule matches stage_hint %q for node %q in unit %q", hintValue, node.NodeID, flow.UnitID)
			}
			key := fmt.Sprintf("%s:%s", flow.UnitID, node.NodeID)
			if _, duplicate := seen[key]; duplicate {
				return MappedFlow{}, Errorf("duplicate node key %q during mapping", key)
			}
			seen[key] = struct{}{}
			nodes = append(nodes, MappedNode{Node: node, StandardStage: rule.StandardStage, RuleID: rule.RuleID})
		}
	}

	if flow.MappingRulesVersion != 1 {
		return MappedFlow{}, Errorf("unsupported mapping_rules_version %d; only 1 is supported", flow.MappingRulesVersion)
	}
	return MappedFlow{UnitID: flow.UnitID, Version: flow.Version, Nodes: nodes}, nil
}
