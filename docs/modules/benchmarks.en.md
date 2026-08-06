# `benchmarks/` — Scalability Probes

## Scope

Offline performance baselines: SLA reference table and probe inventory driven
by `scripts/benchmark.py`. Timing probes are intentionally excluded from
`make quality` (environment-dependent).

## Files

| File | Key functions | Responsibility |
|---|---|---|
| `harness.py` | `measure()`, `report()`, `BenchmarkResult` | Timing, limit comparison, JSON output |
| `models.py` | `SLA_TARGETS`, `SCALABILITY_PROBES`, `SlaTarget` | SLA table + probe inventory (le comparisons, positive caps) |

## Constraints

- Fully offline; deterministic, reproducible measurements; probe results are
  not written to the audit chain.

## Testing

- `tests/unit/test_benchmark_suite.py` (probe inventory/cap validity);
  `tests/unit/test_benchmark_http.py` (cockpit HTTP probe: zero errors, latency
  bound binding).
