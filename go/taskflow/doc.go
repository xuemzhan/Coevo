// Package taskflow implements the US-1 task-flow understanding domain slice
// in Go.
//
// It is a behavior-preserving port of src/coevo/task_flow/models.py and
// src/coevo/task_flow/mapping.py (the Python reference implementation):
//
//   * every model type is immutable by convention (constructors copy slices);
//   * version is a monotonic integer, never a timestamp (AGENTS.md §3 item 2);
//   * every extracted attribute carries provenance (Traced: source path,
//     confidence in [0,1], SourceKind);
//   * reviewer edits are recorded as Override entries;
//   * per-unit stage hints are translated to the standardized StandardStage
//     taxonomy through a versioned, deterministic rule table.
//
// The package is pure data: no IO, no network, no model inference. The
// deterministic parser and the service facade are ported in later
// GO-MIGRATE slices.
package taskflow
