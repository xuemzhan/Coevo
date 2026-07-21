---
description: Run exactly one controlled MVP engineering cycle for one work item; accepts $ITEM as an explicit item id.
agent: loop-engineer
---

Execute exactly one engineering cycle.

Workspace rules:

- Treat the current session `cwd` / project root as the only repository root.
- Use repository-relative paths. Never guess `/workspace`, `C:\workspace`, a parent repository, or another external root.
- This is Windows PowerShell. Run the quality gate only as `make quality` or through `quality_gate`; never rewrite it as `cd /workspace && ...`.
- Base conclusions only on the current `loop/STATE.json`, this cycle's actual gate results, and this cycle's reviewer results.
- Historical failures in verification or audit logs are evidence of history, not current blockers. A current block requires a non-null `STATE.json.blocking_issue` or a fresh failing gate/reviewer result.

Read:

- `loop/STATE.json`
- `loop/BACKLOG.yaml`
- `loop/GOAL.md`
- `loop/VERIFICATION.md`
- current `git diff` and uncommitted changes

If `$ITEM` is present, it is the only target. Otherwise select the smallest ready item from `loop/BACKLOG.yaml`.

Follow DISCOVER -> PLAN -> IMPLEMENT -> VERIFY -> REVIEW -> RECORD -> DECIDE. Do not process multiple items and do not skip testing or required security review.

At the end report the item id, each met and unmet AC, actual test fingerprint and failures, reviewer conclusions, exact STATE field changes, and the next action or current blocker.
