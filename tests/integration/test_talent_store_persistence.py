"""Integration tests for US-3-AC-2: cross-restart talent-store persistence."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.coevo.talent import (
    AvailabilityWindow,
    RedactedIdentity,
    SkillTag,
    Talent,
    TalentPool,
    TalentRecommenderService,
    TalentStore,
    TalentStoreDuplicateError,
    TalentStoreIntegrityError,
)
from src.coevo.talent.recommender import TaskRequirement


def _talent(
    *,
    talent_code: str = "t.1",
    skill_tags: tuple[str, ...] = ("tech:python",),
    credentials: tuple[str, ...] = ("cert.pmp",),
) -> Talent:
    return Talent(
        talent_code=talent_code,
        skill_tags=tuple(SkillTag(tag) for tag in skill_tags),
        credentials=credentials,
        current_task_count=1,
        max_parallel_tasks=2,
        availability=AvailabilityWindow(
            "2026-08-01T00:00:00Z", "2026-08-31T00:00:00Z"
        ),
        redacted_identity=RedactedIdentity(
            pool_code="pool.1",
            display_hint="ab12cd34",
            identity_hash="a" * 64,
        ),
    )


def _tmpdir(test: unittest.TestCase) -> str:
    td = tempfile.TemporaryDirectory()
    test.addCleanup(td.cleanup)
    return td.name


class CrossRestartPersistenceTests(unittest.TestCase):
    def test_registered_talents_survive_restart(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.addCleanup(store.close)
        store.register(_talent())
        store.close()

        reopened = TalentStore.open(path)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.get("t.1"), _talent())
        self.assertEqual(len(reopened), 1)
        self.assertEqual(reopened.pool_code, "pool.1")

    def test_duplicate_talent_code_detected_across_restart(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.addCleanup(store.close)
        store.register(_talent())
        store.close()

        reopened = TalentStore.open(path)
        self.addCleanup(reopened.close)
        with self.assertRaises(TalentStoreDuplicateError):
            reopened.register(_talent(talent_code="t.1"))

    def test_snapshot_after_restart_drives_recommender(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.addCleanup(store.close)
        store.register(_talent())
        store.register(
            _talent(
                talent_code="t.2",
                skill_tags=("tech:go",),
                credentials=(),
            )
        )
        store.close()

        reopened = TalentStore.open(path)
        self.addCleanup(reopened.close)
        pool = reopened.snapshot()
        self.assertIsInstance(pool, TalentPool)
        self.assertEqual(2, len(pool.talents))
        recommendations = TalentRecommenderService().recommend_for_requirements(
            pool,
            (
                TaskRequirement(
                    task_type="backend",
                    required_skill_tags=("tech:python",),
                    required_credentials=("cert.pmp",),
                    window=AvailabilityWindow(
                        "2026-08-10T00:00:00Z", "2026-08-20T00:00:00Z"
                    ),
                ),
            ),
        )
        self.assertEqual(2, len(recommendations))
        self.assertEqual("t.1", recommendations[0].talent.talent_code)

    def test_tampered_file_is_refused_on_reopen(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.addCleanup(store.close)
        store.register(_talent())
        store.close()

        connection = sqlite3.connect(str(path))
        connection.execute(
            "UPDATE talents SET max_parallel_tasks = 999 "
            "WHERE talent_code = 't.1'"
        )
        connection.commit()
        connection.close()

        with self.assertRaises(TalentStoreIntegrityError):
            TalentStore.open(path)

    def test_append_after_reopen_extends_store(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        store = TalentStore.create(path, pool_code="pool.1")
        self.addCleanup(store.close)
        store.register(_talent())
        store.close()

        reopened = TalentStore.open(path)
        self.addCleanup(reopened.close)
        reopened.register(
            _talent(
                talent_code="t.2",
                skill_tags=("tech:go",),
                credentials=(),
            )
        )
        reopened.close()

        reopened_again = TalentStore.open(path)
        self.addCleanup(reopened_again.close)
        self.assertEqual(2, len(reopened_again))
        self.assertIsNotNone(reopened_again.get("t.2"))

    def test_from_pool_then_reopen_round_trip(self):
        tmp = _tmpdir(self)
        path = Path(tmp) / "talent.db"
        pool = TalentPool(
            pool_code="pool.1",
            schema_version="1.0",
            talents=(_talent(),),
        )
        store = TalentStore.from_pool(path, pool)
        store.close()

        reopened = TalentStore.open(path)
        self.addCleanup(reopened.close)
        restored = reopened.snapshot()
        self.assertEqual(pool, restored)


if __name__ == "__main__":
    unittest.main()
