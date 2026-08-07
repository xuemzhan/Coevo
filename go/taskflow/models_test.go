package taskflow

import (
	"math"
	"testing"
)

func mustTraced(t *testing.T, value any, sourcePath string, confidence float64, kind SourceKind) Traced {
	t.Helper()
	traced, err := NewTraced(value, sourcePath, confidence, kind)
	if err != nil {
		t.Fatalf("NewTraced(%v, %q, %v, %q): %v", value, sourcePath, confidence, kind, err)
	}
	return traced
}

func TestTracedConfidenceInRange(t *testing.T) {
	for _, confidence := range []float64{-0.1, 1.01, 2.0, math.NaN()} {
		if _, err := NewTraced("x", "p", confidence, SourceKindLiteral); err == nil {
			t.Fatalf("NewTraced accepted out-of-range confidence %v", confidence)
		}
	}
	if _, err := NewTraced("x", "p", 0.5, SourceKindLiteral); err != nil {
		t.Fatalf("NewTraced rejected valid confidence: %v", err)
	}
	if _, err := NewTraced("x", "p", 0.5, SourceKind("bogus")); err == nil {
		t.Fatal("NewTraced accepted an invalid source kind")
	}
}

func TestSourceKindValues(t *testing.T) {
	valid := []SourceKind{SourceKindLiteral, SourceKindDerived, SourceKindDefaulted, SourceKindOverridden}
	for _, kind := range valid {
		if !kind.Valid() {
			t.Errorf("expected %q to be valid", kind)
		}
	}
	if SourceKind("bogus").Valid() {
		t.Error("expected bogus source kind to be invalid")
	}
}

func TestSourceMappingKeepsFirstValueForDuplicateKeys(t *testing.T) {
	mapping := NewSourceMapping([]SourceMappingEntry{
		{Key: "stages[0].name", Value: "title"},
		{Key: "stages[0].name", Value: "later"},
	})
	value, ok := mapping.Get("stages[0].name")
	if !ok || value != "title" {
		t.Fatalf("expected first value, got ok=%v value=%q", ok, value)
	}
	if _, ok := mapping.Get("missing"); ok {
		t.Error("expected missing key to report not-found")
	}
	if got := len(mapping.Entries()); got != 2 {
		t.Errorf("entries must preserve insertion order and duplicates, got %d", got)
	}
}

func TestWithOverridesBumpsVersionAndRecordsOverrides(t *testing.T) {
	flow := NewProcessFlow("u5", 1, "2026-07-25T00:00:00Z",
		mustTraced(t, "U5", "flow.title", 0.95, SourceKindLiteral), nil, nil, SourceMapping{}, nil)
	override := Override{
		TargetPath:    "stages[0].nodes[0].title",
		OriginalValue: "Receive",
		EditedValue:   "Receive & validate",
		Reason:        "PM clarified acceptance phrasing",
	}
	next, err := flow.WithOverrides([]Override{override}, "2026-07-25T01:00:00Z")
	if err != nil {
		t.Fatalf("WithOverrides: %v", err)
	}
	if next.Version != 2 {
		t.Errorf("expected version 2, got %d", next.Version)
	}
	if len(next.Overrides) != 1 || next.Overrides[0] != override {
		t.Errorf("overrides not recorded: %+v", next.Overrides)
	}
	if flow.Version != 1 {
		t.Error("WithOverrides must not mutate the original flow")
	}
}

func TestWithOverridesRejectsEmptyOverrides(t *testing.T) {
	flow := NewProcessFlow("u6", 1, "2026-07-25T00:00:00Z",
		mustTraced(t, "U6", "flow.title", 0.95, SourceKindLiteral), nil, nil, SourceMapping{}, nil)
	if _, err := flow.WithOverrides(nil, "2026-07-25T01:00:00Z"); err == nil {
		t.Fatal("expected empty overrides to be rejected")
	}
}

func TestDefaultMappingRuleTableIsNonEmpty(t *testing.T) {
	rules := DefaultMappingRules()
	if len(rules) == 0 {
		t.Fatal("default mapping rule table must be non-empty")
	}
	if len(rules) != 27 {
		t.Errorf("expected 27 default rules to match Python, got %d", len(rules))
	}
}
