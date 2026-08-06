# `report/` — Result Submission (US-9)

## Scope

Result-submission manifest and package builder producing `Report.agent`
packages; reuses the US-5 wire layout so reports share the exact encryption and
signing mechanism as dispatch packages.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `ReportManifest`, `ReportArtifact`, `ReportStatus`, `ReportOverride` | Manifest/artifact/status models + validation |
| `builder.py` | `ReportBuilder.build()`, `ReportSubmissionSequence` | Monotonic submission sequence, package assembly, audit projection |

## Invariants

- Manifest fields strictly validated (size/enums/time); invalid timestamps
  fail closed;
- Carries project/task ids + base revision + package id + submission sequence;
- Original deliverables stay local; export is audited.

## Testing

- `tests/unit/test_report_builder.py` (25 tests);
  `tests/e2e/test_return_chain.py`.
