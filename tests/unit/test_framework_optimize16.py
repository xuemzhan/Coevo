"""PERF-REPLAY-1: check_replay single-pass scan correctness + structure."""
from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.protocol.replay_detector import (
    ProcessedPackage,
    ReplayOutcome,
    check_replay,
)


ROOT = Path(__file__).resolve().parents[2]


def _record(
    package_id: str,
    digest: str,
    sequence_no: int,
    *,
    sender: str = "S",
    recipient: str = "R",
    project: str = "P",
) -> ProcessedPackage:
    return ProcessedPackage(
        package_id=package_id,
        package_digest=digest,
        sender_cert_id=sender,
        recipient_cert_id=recipient,
        project_id=project,
        sequence_no=sequence_no,
    )


class SinglePassDecisionTests(unittest.TestCase):
    def test_package_id_hit_wins_over_earlier_digest_hit(self):
        # The digest match appears FIRST in the scope, but the package_id
        # match appears later; the id precedence must win (no early break).
        candidate = _record("id-new", "digest-shared", 3)
        registry = (
            _record("id-other", "digest-shared", 1),
            _record("id-new", "digest-other", 2),
        )
        decision = check_replay(candidate=candidate, registry=registry)
        self.assertEqual(ReplayOutcome.DUPLICATE_PACKAGE_ID, decision.outcome)
        self.assertEqual(2, decision.previous_sequence_no)

    def test_digest_hit_returns_digest_when_no_id_hit(self):
        candidate = _record("id-new", "digest-shared", 3)
        registry = (_record("id-other", "digest-shared", 1),)
        decision = check_replay(candidate=candidate, registry=registry)
        self.assertEqual(ReplayOutcome.DUPLICATE_DIGEST, decision.outcome)
        self.assertEqual(1, decision.previous_sequence_no)

    def test_sequence_replay_still_detected_after_full_scan(self):
        # No id/digest hit: the max sequence must come from the FULL scope.
        candidate = _record("id-new", "digest-new", 2)
        registry = (
            _record("a", "da", 1),
            _record("b", "db", 5),
            _record("c", "dc", 3),
        )
        decision = check_replay(candidate=candidate, registry=registry)
        self.assertEqual(ReplayOutcome.REPLAY_SEQUENCE, decision.outcome)
        self.assertEqual(5, decision.previous_sequence_no)

    def test_accept_keeps_previous_sequence(self):
        candidate = _record("id-new", "digest-new", 6)
        registry = (_record("a", "da", 5),)
        decision = check_replay(candidate=candidate, registry=registry)
        self.assertEqual(ReplayOutcome.ACCEPT, decision.outcome)
        self.assertEqual(5, decision.previous_sequence_no)

    def test_revoked_package_still_takes_precedence(self):
        candidate = _record("id-revoked", "digest-new", 1)
        decision = check_replay(
            candidate=candidate,
            revoked_package_ids=("id-revoked",),
        )
        self.assertEqual(ReplayOutcome.REVOKED_PACKAGE, decision.outcome)


class SinglePassStructureTests(unittest.TestCase):
    def test_no_three_separate_scope_loops(self):
        source = (
            ROOT / "src" / "coevo" / "protocol" / "replay_detector.py"
        ).read_text(encoding="utf-8")
        # The merged implementation uses one "for record in same_scope" loop.
        self.assertEqual(1, source.count("for record in same_scope"))


if __name__ == "__main__":
    unittest.main()
