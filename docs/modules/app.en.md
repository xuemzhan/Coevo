# `app/` — Application Composition Root (Demo Pipeline)

## Scope

Assembles the domain facades into the fixed orchestration chains to produce an
offline, reproducible end-to-end demo. It is the official entry point for
`scripts/run_demo.py` and the e2e tests. Composition only; no domain logic.

## Files

| File | Key functions | Responsibility |
|---|---|---|
| `pipeline.py` | `run_demo_pipeline()` | Seven-stage demo pipeline (PKI bootstrap → real chain → encrypted package → cockpit → knowledge → audit) |
| `demo_support.py` | `DemoSigner`, `DemoFreshnessAuthority`, `ensure_demo_profile()`, `sample_project_input()` | Demo-only PKI bootstrap, simulated signing/freshness, sample inputs |

## Invariants

- Fully offline: no network, no runtime downloads;
- Python never touches private-key bytes (operations go through the controlled
  crypto helper);
- Demo stand-ins (HMAC signer, in-memory freshness) are explicitly non-production.

## Testing

- `tests/e2e/test_demo_runner.py` (CLI smoke, real package + persistence, cockpit
  server lifecycle); `tests/e2e/test_return_chain.py` (real encrypted report
  drives merge→risk→brief→knowledge).
