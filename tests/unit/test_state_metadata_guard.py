"""MATURITY-R-03: guard that loop/STATE.json metadata stays fresh and truthful.

Background (2026-08-12 independent review): loop/STATE.json was left pointing at
ARCH-REVIEW-17 with ``last_verified_commit`` 18c3baa and ``updated_at``
2026-08-10 while the formal BACKLOG had already advanced to ARCH-REVIEW-18 and
the HEAD (631d46a) had been verified by a full quality gate
(fingerprint b5c12e15ae7c559f). This guard makes that class of staleness a
hard failure:

* ``current_item`` must equal the **last** formal BACKLOG item (queue comments
  are excluded, so a completed loop item can never be left unrecorded);
* ``current_story`` must match that item's story;
* ``last_verified_commit`` must be a 40-hex commit reachable from HEAD;
* ``updated_at`` must be ISO-8601 UTC and not in the future;
* the envelope (schema/iteration/phase/status) must stay well-formed.
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "loop" / "STATE.json"
BACKLOG_PATH = ROOT / "loop" / "BACKLOG.yaml"

KNOWN_STATUSES = {
    "ready",
    "in-progress",
    "blocked",
    "security-blocked",
    "decision-required",
    "done",
    "mvp-complete",
}
KNOWN_PHASES = {"ready", "discover", "plan", "implement", "verify", "review", "record", "decide"}


def formal_item_blocks(text: str) -> list[tuple[str, str]]:
    """Return (id, story) for formal BACKLOG items in file order.

    Comment lines (including the PRODUCT-REVIEW queue annotations) are
    skipped; only real ``- id:`` blocks with a following ``story:`` are
    counted, mirroring the fail-closed line parser used by run_validation.
    """

    items: list[tuple[str, str]] = []
    current_id: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - id: "):
            current_id = stripped.split(":", 1)[1].strip()
            continue
        if line.startswith("    story: ") and current_id is not None:
            story = stripped.split(":", 1)[1].strip()
            items.append((current_id, story))
            current_id = None
    return items


def is_reachable_from_head(commit: str) -> bool:
    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


class BacklogParserTests(unittest.TestCase):
    def test_skips_queue_comments_and_returns_last_item(self):
        text = (
            'version: "1.0"\n'
            "items:\n"
            "  # ---------- PRODUCT-REVIEW queue (not formal items) ----------\n"
            "  #   T-01 pending owner decision\n"
            "  - id: ENG-BASE-AC-1\n"
            "    story: ENG-BASE\n"
            "    status: done\n"
            "  - id: ARCH-REVIEW-18\n"
            "    story: ARCH-REVIEW\n"
            "    status: done\n"
        )
        items = formal_item_blocks(text)
        self.assertEqual([("ENG-BASE-AC-1", "ENG-BASE"), ("ARCH-REVIEW-18", "ARCH-REVIEW")], items)
        self.assertEqual(("ARCH-REVIEW-18", "ARCH-REVIEW"), items[-1])

    def test_item_without_story_is_skipped(self):
        text = "items:\n  - id: NO-STORY\n    status: done\n"
        self.assertEqual([], formal_item_blocks(text))


class StateMetadataGuardTests(unittest.TestCase):
    def test_state_is_well_formed(self):
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual("1.0", state["schema_version"])
        self.assertIsInstance(state["iteration"], int)
        self.assertGreater(state["iteration"], 0)
        self.assertIn(state["phase"], KNOWN_PHASES)
        self.assertIn(state["status"], KNOWN_STATUSES)
        self.assertTrue(state["current_item"])

    def test_state_points_to_last_formal_backlog_item(self):
        """R-03 freshness: STATE must record the newest formal loop item."""

        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        items = formal_item_blocks(BACKLOG_PATH.read_text(encoding="utf-8"))
        self.assertTrue(items, "BACKLOG must contain formal items")
        last_id, last_story = items[-1]
        self.assertEqual(
            last_id,
            state["current_item"],
            "STATE.current_item must equal the last formal BACKLOG item",
        )
        self.assertEqual(
            last_story,
            state["current_story"],
            "STATE.current_story must match the last formal BACKLOG item",
        )

    def test_last_verified_commit_is_reachable_from_head(self):
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        commit = state["last_verified_commit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$", "last_verified_commit must be 40 hex")
        self.assertTrue(
            is_reachable_from_head(commit),
            "last_verified_commit must be an ancestor of (or equal to) HEAD",
        )

    def test_updated_at_is_iso_utc_and_not_future(self):
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        stamp = datetime.fromisoformat(state["updated_at"].replace("Z", "+00:00"))
        self.assertEqual(UTC, stamp.tzinfo, "updated_at must carry a UTC offset")
        self.assertLessEqual(
            stamp,
            datetime.now(UTC) + timedelta(minutes=5),
            "updated_at must not be in the future",
        )


if __name__ == "__main__":
    unittest.main()
