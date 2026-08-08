"""Unit tests for the US-7-AC-2 HTTP layer (pure parts)."""
from __future__ import annotations

import tempfile
import os
import time
import unittest
from pathlib import Path

from src.coevo.cockpit import (
    STATIC_ROOT,
    CockpitHttpConfig,
    CockpitSessionManager,
    CockpitValidationError,
    SingleInstanceLock,
    resolve_static_path,
)
from src.coevo.cockpit.server import _process_exists


T0 = "2026-08-22T00:00:00Z"


class CockpitHttpConfigTests(unittest.TestCase):
    def test_default_config_is_valid(self):
        config = CockpitHttpConfig()
        self.assertEqual("127.0.0.1", config.bind_host)
        self.assertIn("127.0.0.1", config.allowed_hosts)

    def test_non_loopback_bind_is_rejected(self):
        with self.assertRaises(CockpitValidationError):
            CockpitHttpConfig(bind_host="0.0.0.0")
        with self.assertRaises(CockpitValidationError):
            CockpitHttpConfig(bind_host="10.0.0.1")

    def test_invalid_port_is_rejected(self):
        with self.assertRaises(CockpitValidationError):
            CockpitHttpConfig(bind_port=0)
        with self.assertRaises(CockpitValidationError):
            CockpitHttpConfig(bind_port=70000)

    def test_static_root_outside_cockpit_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(CockpitValidationError):
                CockpitHttpConfig(static_root=Path(tmp))

    def test_static_root_inside_cockpit_is_accepted(self):
        config = CockpitHttpConfig(static_root=STATIC_ROOT)
        self.assertEqual(STATIC_ROOT, config.static_root)

    def test_non_positive_limits_are_rejected(self):
        for kwargs in (
            {"max_request_bytes": 0},
            {"request_timeout_sec": 0},
            {"session_timeout_sec": 0},
        ):
            with self.assertRaises(CockpitValidationError):
                CockpitHttpConfig(**kwargs)

    def test_external_allowed_host_is_rejected(self):
        with self.assertRaises(CockpitValidationError):
            CockpitHttpConfig(allowed_hosts=frozenset({"192.168.1.5"}))

    def test_lock_path_must_be_path(self):
        with self.assertRaises(CockpitValidationError):
            CockpitHttpConfig(lock_path="C:\\lock")  # type: ignore[arg-type]

    def test_lock_path_defaults_to_single_instance(self):
        config = CockpitHttpConfig()
        self.assertIsNotNone(config.lock_path)
        self.assertTrue(str(config.lock_path).endswith("cockpit.lock"))

    def test_invalid_concurrency_limit_is_rejected(self):
        for value in (0, -1, True, 1.5, "16"):
            with self.assertRaises(CockpitValidationError):
                CockpitHttpConfig(max_concurrent_requests=value)

    def test_invalid_snapshot_interval_is_rejected(self):
        for value in (0, -1, True, "5"):
            with self.assertRaises(CockpitValidationError):
                CockpitHttpConfig(state_snapshot_interval_sec=value)

    def test_invalid_lock_heartbeat_interval_is_rejected(self):
        for value in (0, -1, True, "5"):
            with self.assertRaises(CockpitValidationError):
                CockpitHttpConfig(lock_heartbeat_interval_sec=value)

    def test_lock_heartbeat_interval_default_and_none(self):
        self.assertEqual(60.0, CockpitHttpConfig().lock_heartbeat_interval_sec)
        config = CockpitHttpConfig(lock_heartbeat_interval_sec=None)
        self.assertIsNone(config.lock_heartbeat_interval_sec)

    def test_hardening_defaults(self):
        config = CockpitHttpConfig()
        self.assertEqual(16, config.max_concurrent_requests)
        self.assertEqual(300.0, config.state_snapshot_interval_sec)


class CockpitSessionManagerTests(unittest.TestCase):
    def test_create_and_validate(self):
        manager = CockpitSessionManager(timeout_sec=60)
        token = manager.create(now=T0)
        self.assertTrue(token)
        self.assertEqual(1, manager.session_count)
        self.assertTrue(manager.validate(token, now=T0))

    def test_revoke(self):
        manager = CockpitSessionManager(timeout_sec=60)
        token = manager.create(now=T0)
        self.assertTrue(manager.revoke(token))
        self.assertFalse(manager.validate(token, now=T0))
        self.assertEqual(0, manager.session_count)

    def test_rotate_issues_fresh_token_and_revokes_old(self):
        manager = CockpitSessionManager(timeout_sec=60)
        old = manager.create(now=T0)
        new = manager.rotate(old, now=T0)
        self.assertNotEqual(old, new)
        self.assertFalse(manager.validate(old, now=T0))
        self.assertTrue(manager.validate(new, now=T0))
        self.assertEqual(1, manager.session_count)

    def test_rotate_unknown_token_is_rejected(self):
        manager = CockpitSessionManager(timeout_sec=60)
        with self.assertRaises(CockpitValidationError):
            manager.rotate("unknown-token", now=T0)

    def test_max_session_age_forces_rotation(self):
        manager = CockpitSessionManager(
            timeout_sec=600,
            max_session_age_sec=60,
        )
        token = manager.create(now="2026-08-22T00:00:00Z")
        self.assertTrue(manager.validate(token, now="2026-08-22T00:00:30Z"))
        self.assertFalse(manager.validate(token, now="2026-08-22T00:01:30Z"))
        self.assertEqual(0, manager.session_count)

    def test_inactivity_timeout_expires_session(self):
        manager = CockpitSessionManager(timeout_sec=1)
        token = manager.create(now="2026-08-22T00:00:00Z")
        self.assertTrue(manager.validate(token, now="2026-08-22T00:00:00Z"))
        self.assertFalse(manager.validate(token, now="2026-08-22T00:00:03Z"))
        self.assertEqual(0, manager.session_count)

    def test_activity_touches_session(self):
        manager = CockpitSessionManager(timeout_sec=5)
        token = manager.create(now="2026-08-22T00:00:00Z")
        self.assertTrue(manager.validate(token, now="2026-08-22T00:00:04Z"))
        self.assertTrue(manager.validate(token, now="2026-08-22T00:00:08Z"))

    def test_max_sessions_evicts_oldest(self):
        manager = CockpitSessionManager(timeout_sec=60, max_sessions=2)
        first = manager.create(now="2026-08-22T00:00:00Z")
        manager.create(now="2026-08-22T00:00:01Z")
        manager.create(now="2026-08-22T00:00:02Z")
        self.assertEqual(2, manager.session_count)
        self.assertFalse(manager.validate(first, now="2026-08-22T00:00:03Z"))

    def test_max_sessions_keeps_the_newest(self):
        # PERF-SESS-1: the eviction must remove the oldest and keep the rest.
        manager = CockpitSessionManager(timeout_sec=60, max_sessions=2)
        first = manager.create(now="2026-08-22T00:00:00Z")
        second = manager.create(now="2026-08-22T00:00:01Z")
        third = manager.create(now="2026-08-22T00:00:02Z")
        self.assertEqual(2, manager.session_count)
        self.assertTrue(manager.validate(second, now="2026-08-22T00:00:03Z"))
        self.assertTrue(manager.validate(third, now="2026-08-22T00:00:03Z"))

    def test_eviction_uses_bounded_heap_selection(self):
        # Source guard: the eviction must not do a full O(n log n) sort.
        root = Path(__file__).resolve().parents[2]
        source = (root / "src/coevo/cockpit/sessions.py").read_text(encoding="utf-8")
        self.assertIn("heapq.nsmallest", source)
        self.assertNotIn("sorted(\n            self._sessions", source)

    def test_empty_and_unknown_tokens_fail(self):
        manager = CockpitSessionManager(timeout_sec=60)
        self.assertFalse(manager.validate("", now=T0))
        self.assertFalse(manager.validate("unknown-token", now=T0))

    def test_invalid_constructor_arguments(self):
        with self.assertRaises(CockpitValidationError):
            CockpitSessionManager(timeout_sec=0)
        with self.assertRaises(CockpitValidationError):
            CockpitSessionManager(max_sessions=0)


class SingleInstanceLockTests(unittest.TestCase):
    def test_acquire_release_reacquire(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            lock = SingleInstanceLock(path)
            lock.acquire()
            self.assertTrue(path.exists())
            lock.release()
            self.assertFalse(path.exists())
            lock.acquire()
            lock.release()

    def test_second_lock_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            first = SingleInstanceLock(path)
            first.acquire()
            second = SingleInstanceLock(path)
            with self.assertRaises(CockpitValidationError):
                second.acquire()
            first.release()
            second.acquire()
            second.release()

    def test_stale_lock_is_recovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            # A pid that is no longer running: recovery must proceed once
            # both the mtime is stale AND the recorded owner is dead.
            path.write_text(str(999_999_999), encoding="ascii")
            old = time.time() - SingleInstanceLock.STALE_AFTER_SECONDS - 60
            os.utime(path, (old, old))
            lock = SingleInstanceLock(path)
            lock.acquire()
            try:
                self.assertTrue(path.exists())
            finally:
                lock.release()
            self.assertFalse(path.exists())

    def test_stale_lock_with_live_pid_is_not_reclaimed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            path.write_text(str(os.getpid()), encoding="ascii")
            old = time.time() - SingleInstanceLock.STALE_AFTER_SECONDS - 60
            os.utime(path, (old, old))
            lock = SingleInstanceLock(path)
            with self.assertRaises(CockpitValidationError):
                lock.acquire()
            self.assertTrue(path.exists())

    def test_process_exists_probe(self):
        # The current test process is alive; a far-out pid is not.
        self.assertTrue(_process_exists(os.getpid()))
        self.assertFalse(_process_exists(999_999_999))
        self.assertFalse(_process_exists(0))
        self.assertFalse(_process_exists(-1))

    def test_heartbeat_refreshes_lock_mtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            lock = SingleInstanceLock(path)
            lock.acquire()
            try:
                old = time.time() - SingleInstanceLock.STALE_AFTER_SECONDS - 60
                os.utime(path, (old, old))
                lock.refresh()
                self.assertGreater(path.stat().st_mtime, old + 1)
            finally:
                lock.release()

    def test_refresh_without_acquire_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            SingleInstanceLock(path).refresh()
            self.assertFalse(path.exists())

    def test_context_manager(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cockpit.lock"
            with SingleInstanceLock(path):
                self.assertTrue(path.exists())
            self.assertFalse(path.exists())


class ResolveStaticPathTests(unittest.TestCase):
    def test_valid_assets_resolve(self):
        for name in ("index.html", "app.js", "style.css"):
            self.assertIsNotNone(resolve_static_path(STATIC_ROOT, name))

    def test_traversal_and_absolute_paths_are_rejected(self):
        for bad in (
            "../secret.txt",
            "a/../b.js",
            "/etc/passwd",
            "..\\secret.js",
            "",
            "a//b.js",
            "./app.js",
        ):
            self.assertIsNone(resolve_static_path(STATIC_ROOT, bad), bad)

    def test_disallowed_extension_is_rejected(self):
        self.assertIsNone(resolve_static_path(STATIC_ROOT, "index.php"))
        self.assertIsNone(resolve_static_path(STATIC_ROOT, "payload.exe"))

    def test_missing_file_is_rejected(self):
        self.assertIsNone(resolve_static_path(STATIC_ROOT, "missing.css"))


if __name__ == "__main__":
    unittest.main()
