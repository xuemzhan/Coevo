# `knowledge_base/` — Knowledge Sedimentation (US-14)

## Scope

Aggregates baselines, merges, risks, meeting conclusions, briefs, progress and
model summaries into knowledge bundles, retrospective drafts and reusable
templates; entries require human review and classification checks.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `KnowledgeEntry`, `KnowledgeBundle`, `ReusableTemplate`, `RetrospectiveDraft`, `ReviewDecision` | Models + validation |
| `facade.py` | `KnowledgeBaseFacade.aggregate/review/to_audit_record` | Aggregation facade + approval |
| `store.py` | `KnowledgeStore` | SQLite persistence: JSON codec + atomic commits + audit hash chain |

## Security invariants

- Unreviewed model summaries never enter the formal knowledge base (AC-7);
- Every entry records source project and applicability; classification is the
  maximum of all entries;
- Facade is pure (no IO); audit projections are redacted.

## Testing

- `tests/unit/test_knowledge_base.py`, `test_knowledge_store.py`;
  `tests/integration/test_knowledge_store.py`.
