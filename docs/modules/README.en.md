# Coevo Module Documentation (English Overview)

Each package under `src/coevo` has a Chinese doc with the full template (scope,
boundaries, per-file responsibilities, entry points, data flow, security
invariants, test coverage, dependencies, config/error semantics). This page
provides a one-paragraph English summary per module. Requirements-to-code-to-test
mapping: `docs/traceability/requirements-test-matrix.md`; guided tour:
`docs/code-guide.md`.

| Module | Summary |
|---|---|
| `app/` | Composition root: assembles the fixed orchestration chains into an offline, reproducible end-to-end demo (`run_demo_pipeline`); demo-only PKI bootstrap and sample inputs; never contains domain logic. |
| `audit_governance/` | US-15: unified `AuditEvent` model, five-class interception decisions, paged query/export, and a JSONL + SHA-256 hash-chained durable audit stream; sensitive text is stored as hashes/counts. |
| `benchmarks/` | Offline scalability probes and SLA reference table driven by `scripts/benchmark.py`; timing probes are excluded from `make quality` by design. |
| `cockpit/` | US-7: loopback-only local HTTP dashboard with bearer-token sessions, Host/Origin/CSRF checks, state checkpointing, localized static assets, and an allow-listed WPS launcher; single-instance lock with heartbeat + liveness probe. |
| `crypto/` | National-crypto engine adapters: provider scope governance, locked GmSSL 3.2.0 one-shot helper, CNG KEK-backed protected key handles, pure-Python SM3; private-key bytes never enter Python. |
| `decision_brief/` | US-13: decision briefs generated only from owner-key-confirmed risks bound to the latest verified merge receipt; controlled DOCX templates, CAS revision store, replay fail-closed. |
| `identity/` | US-0: offline identity, trusted certificates, private-key handle interface (metadata only), SQLite repository and signed audit anchors with freshness monotonicity. |
| `knowledge_base/` | US-14: aggregates baselines, merges, risks, meeting conclusions, briefs, progress and model summaries into knowledge bundles, retrospective drafts and reusable templates; model summaries need explicit approval. |
| `merge/` | US-10: field-level merge with verified-import binding, decision-maker allow-list, no timestamp-only overrides, signed commit receipts and a sealed, row-validated SQLite receipt chain. |
| `model/` | Model-adapter layer: replaceable providers (offline/deepseek/local_openai), versioned config and prompt registry, OpenAI-compatible client with 4 MiB response cap; model output is always a draft. |
| `orchestrator/` | US-4: fixed-chain orchestration with agent registry/status, human-confirmation gates, SQLite idempotent real-chain store and audit recovery; failures escalate to humans, never silently degrade. |
| `progress_capture/` | US-8: workspace watcher (lstat-once, digest reuse, stability gating) and pure service mapping evidence to progress items; formal acceptance always requires user confirmation. |
| `protocol/` | US-5: `.agent` wire format — fixed header, canonical envelope, SM2 key wrap, SM4-GCM payload, signing, replay/duplicate detection (strictly increasing sequence numbers), 7-step atomic import. |
| `report/` | US-9: result-submission manifest and builder reusing the US-5 wire layout; monotonic submission sequence; original deliverables stay local. |
| `risk/` | US-11: deterministic risk analysis from the latest verified merge receipt (delay, missing predecessors, silence, insufficient evidence, contagion); owner confirmation required before formal release. |
| `supervision/` | US-12: converts confirmed risks into supervision items, escalation/reminder suggestions and meeting proposals with three conclusion projections; produces suggestions only, never convenes meetings. |
| `talent/` | US-3: redacted talent pool (PII never enters models), deterministic scoring with pre-warmed indexes, SQLite persistence with hash chain; load/capacity alerts. |
| `task_decomposition/` | US-2: baseline factory, dependency graph (heap topological sort, explicit-stack cycle detection), audited task editing and a model-assisted suggestion agent (drafts only). |
| `task_flow/` | US-1: deterministic parsing of canonical/tabular/tree flow inputs, stage mapping (O(1) rule lookup), StageGraph and review view; versioned, immutable flow models. |
| `workspace/` | US-6: safe path policy (dual POSIX/Windows traversal checks), project/role registry with idempotence, and the init service that only releases COMMITTED imports. |
| root modules | `config.py` (fail-closed env config), `version.py` (semantic versioning), `logging_setup.py` (rotating app logs, audit kept separate), `records_archive.py` (record archiving policy). |

Domain vocabulary (closed-set enums/constants) is indexed in
[README.md](README.md) ("关键常量与闭集枚举索引").
