// US-1 task-flow domain model (Go port of src/coevo/task_flow/models.py).
//
// Design notes (kept identical to the Python reference so behavior stays
// aligned during the Go migration):
//
//   * Version is an integer and is never a timestamp (AGENTS.md §3 item 2).
//   * Every extracted attribute carries provenance (SourcePath, Confidence,
//     SourceKind). Reviewer edits are recorded as Override entries so the
//     original trace is never lost.
//   * Stage names follow the standardized taxonomy (StandardStage); per-unit
//     nodes may carry arbitrary hints that the mapping layer (mapping.go)
//     translates.
package taskflow

import (
	"fmt"
	"math"
)

// ProcessFlowError is the base error for all task-flow failures. The model
// fails closed: every invalid input returns an error instead of a partial
// value (AGENTS.md §3 item 7).
type ProcessFlowError struct {
	message string
}

func (e *ProcessFlowError) Error() string { return e.message }

// Errorf builds a *ProcessFlowError with the given format and arguments.
func Errorf(format string, args ...any) error {
	return &ProcessFlowError{message: fmt.Sprintf(format, args...)}
}

// SourceKind describes how an attribute value entered the model.
//
//   - SourceKindLiteral: copied verbatim from the raw input.
//   - SourceKindDerived: deterministically computed from one or more inputs.
//   - SourceKindDefaulted: bound by a default because the input did not supply it.
//   - SourceKindOverridden: reviewer-edited value that replaced the model's
//     original extraction; the original trace is preserved via Override.
type SourceKind string

const (
	SourceKindLiteral    SourceKind = "literal"
	SourceKindDerived    SourceKind = "derived"
	SourceKindDefaulted  SourceKind = "defaulted"
	SourceKindOverridden SourceKind = "overridden"
)

// Valid reports whether k is one of the closed set of source kinds.
func (k SourceKind) Valid() bool {
	switch k {
	case SourceKindLiteral, SourceKindDerived, SourceKindDefaulted, SourceKindOverridden:
		return true
	default:
		return false
	}
}

// String returns the canonical wire value of k.
func (k SourceKind) String() string { return string(k) }

// Traced wraps a single extracted value with its provenance. SourcePath is a
// dotted JSON-pointer-like path inside the raw input mapping; an empty string
// means "synthesized at parse time without an input counterpart".
type Traced struct {
	Value      any
	SourcePath string
	Confidence float64 // in [0,1]
	SourceKind SourceKind
}

// NewTraced validates confidence in [0,1] and the source kind, mirroring the
// Python frozen dataclass __post_init__ fail-closed behavior (NaN is rejected
// too).
func NewTraced(value any, sourcePath string, confidence float64, kind SourceKind) (Traced, error) {
	if math.IsNaN(confidence) || confidence < 0 || confidence > 1 {
		return Traced{}, Errorf("confidence must be in [0, 1]; got %v", confidence)
	}
	if !kind.Valid() {
		return Traced{}, Errorf("invalid source kind %q", kind)
	}
	return Traced{Value: value, SourcePath: sourcePath, Confidence: confidence, SourceKind: kind}, nil
}

// Override records a reviewer edit that replaces a previously extracted value.
type Override struct {
	TargetPath    string
	OriginalValue any
	EditedValue   any
	Reason        string
}

// Role is a role in the unit's task process (e.g. "QAC reviewer").
type Role struct {
	RoleID         string
	Name           string
	Responsibility Traced
}

// Node is a single process node (= a task step).
type Node struct {
	NodeID           string
	Title            string
	StageHint        Traced
	Inputs           []Traced
	Outputs          []Traced
	ReviewCriteria   []Traced
	ResponsibleRoles []Traced
}

// Stage is an ordered group of nodes.
type Stage struct {
	StageID string
	Name    string
	Nodes   []Node
}

// StandardStage is the system's standardized stage taxonomy. Per AC-7,
// per-unit flow nodes are mapped onto this closed set.
type StandardStage string

const (
	StandardStageIntake    StandardStage = "intake"
	StandardStagePlanning  StandardStage = "planning"
	StandardStageExecution StandardStage = "execution"
	StandardStageReview    StandardStage = "review"
	StandardStageDelivery  StandardStage = "delivery"
	StandardStageClosure   StandardStage = "closure"
)

// String returns the canonical wire value of s.
func (s StandardStage) String() string { return string(s) }

// SourceMappingEntry is a single (parsed path -> raw input path) pair.
type SourceMappingEntry struct {
	Key   string
	Value string
}

// SourceMapping maps each parsed output attribute back to raw input (AC-3).
// Duplicate keys keep the FIRST value, matching the original Python
// setdefault semantics exactly. Missing entries mean "no input counterpart
// (synthesized)" — never silently dropped.
type SourceMapping struct {
	entries []SourceMappingEntry
	index   map[string]string
}

// NewSourceMapping builds the mapping with an O(1) lookup index.
func NewSourceMapping(entries []SourceMappingEntry) SourceMapping {
	index := make(map[string]string, len(entries))
	for _, entry := range entries {
		if _, ok := index[entry.Key]; !ok {
			index[entry.Key] = entry.Value
		}
	}
	return SourceMapping{entries: append([]SourceMappingEntry(nil), entries...), index: index}
}

// Get returns the raw input path for key and whether it exists.
func (m SourceMapping) Get(key string) (string, bool) {
	value, ok := m.index[key]
	return value, ok
}

// Entries returns a defensive copy of the entry pairs in insertion order.
func (m SourceMapping) Entries() []SourceMappingEntry {
	return append([]SourceMappingEntry(nil), m.entries...)
}

// MappingRule maps a per-unit stage hint to a standard stage. Lower Priority
// wins; ties are broken by RuleID (lexicographic).
type MappingRule struct {
	RuleID        string
	UnitStageHint string
	StandardStage StandardStage
	Priority      int
}

// ProcessFlow is a confirmed, versioned unit task-process model (AC-6).
// CreatedAt is an ISO-8601 UTC string with a 'Z' suffix and is informational
// only — ordering is the job of Version.
type ProcessFlow struct {
	UnitID              string
	Version             int
	CreatedAt           string
	Title               Traced
	Stages              []Stage
	Roles               []Role
	SourceMapping       SourceMapping
	Overrides           []Override
	MappingRulesVersion int
}

// NewProcessFlow builds a flow with mapping_rules_version=1 and copies the
// slice fields so later caller mutations cannot leak in.
func NewProcessFlow(unitID string, version int, createdAt string, title Traced, stages []Stage, roles []Role, sourceMapping SourceMapping, overrides []Override) ProcessFlow {
	return ProcessFlow{
		UnitID:              unitID,
		Version:             version,
		CreatedAt:           createdAt,
		Title:               title,
		Stages:              append([]Stage(nil), stages...),
		Roles:               append([]Role(nil), roles...),
		SourceMapping:       sourceMapping,
		Overrides:           append([]Override(nil), overrides...),
		MappingRulesVersion: 1,
	}
}

// WithOverrides returns a copy of f at version+1 with the overrides recorded.
// It fails closed on an empty override set, mirroring the Python helper. The
// actual value substitutions are the caller's responsibility (the model layer
// is pure data).
func (f ProcessFlow) WithOverrides(overrides []Override, newCreatedAt string) (ProcessFlow, error) {
	if len(overrides) == 0 {
		return ProcessFlow{}, Errorf("with_overrides requires non-empty overrides")
	}
	out := f
	out.Version = f.Version + 1
	out.CreatedAt = newCreatedAt
	out.Overrides = append([]Override(nil), overrides...)
	return out, nil
}
