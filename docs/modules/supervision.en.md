# `supervision/` — Supervision and Meeting Coordination (US-12)

## Scope

Converts confirmed risks into supervision items, escalation/reminder
suggestions and meeting proposals with three conclusion projections
(new task / risk disposition / new supervision item). Produces suggestions
only — it never convenes meetings.

## Files

| File | Key types/functions | Responsibility |
|---|---|---|
| `models.py` | `SupervisionItem`, `EscalationSuggestion`, `ReminderSuggestion`, `MeetingProposal`, `MeetingConclusionProjection` | Models + validation (closed enums/constants) |
| `service.py` | `SupervisionCoordinator.coordinate()`, `to_audit_record()` | Pure facade: risk → items/escalations/reminders/meeting/conclusions |

## Security invariants

- Pure functions, no IO/LLM; input must be authoritative (verified risk/receipt);
- Formal supervision and cross-unit reminders require authorized-person
  confirmation (mandatory constraint §8.4);
- Audit projections exclude basis/recommendation/rationale sensitive fields.

## Testing

- `tests/unit/test_supervision_meeting.py` (10 tests).
