# `decision_brief/` — Decision Briefs (US-13)

## Scope

Generates decision briefs only from owner-key-confirmed risks bound to the
latest verified merge receipt; controlled DOCX templates and a CAS revision
store keep briefs traceable and auditable.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `DecisionBrief`, `BriefContent`, `BriefType`, `RiskConfirmation`, `WpsDocumentRequest` | Models + validation (macro-free DOCX, size/entry caps) |
| `repositories.py` | `DecisionBriefRepository`, `ApprovedTemplateRegistry`, `RiskConfirmationRepository` | CAS revisions + event idempotency + content hash chain; template re-verification; authoritative confirmations |
| `service.py` | `DecisionBriefService.generate/revise/to_audit_record` | Facade: consumes latest verified receipt + owner-signed risk confirmation |

## Security invariants

- Briefs use only confirmed state (latest verified receipt); candidates are
  never admitted;
- Risk confirmation binds receipt_id + snapshot_digest + risk_digest, signed by
  the owner's pinned key;
- Templates must be macro-free DOCX under a controlled root; replay fail-closed;
- Audit projections exclude brief text and sensitive bases (hashes/counts only).

## Testing

- `tests/unit/test_decision_brief.py` (20 tests: binding, four sections/three
  types, source tracing, caps, CAS/replay/hash-chain, template tamper/macro,
  WPS approval, audit redaction).
