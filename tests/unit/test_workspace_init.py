"""Unit tests for US-6-AC-1 workspace initialization slice.

Coverage matrix (each TestCase class locks one AC of the slice):

  AC-2  ``TestQuarantinePath``        - quarantine path generation + safe-id.
  AC-4  ``TestWorkspacePath``          - final-workspace path generation + safe-id.
  AC-5  ``TestWorkspaceRegistry``      - in-memory registry + duplicate detection.
  AC-7  ``TestWorkspaceInitService``  - end-to-end init facade + AC-8 idempotence.

Service-layer invariants:
* No IO, no network, no model call.
* Re-running the same init is byte-deterministic.
* Init NEVER produces a workspace for a non-committed import.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.coevo.protocol import (
    AgentPackageImportError,
    DEFAULT_EMPTY_STORE,
    ImportOutcome,
    ImportStep,
    ImportTransaction,
    PackageImportService,
    ProcessedPackage,
    ProcessedPackageRecord,
    ProcessedPackageStore,
    ReplayDecision,
    ReplayOutcome,
)
from src.coevo.workspace import (
    DEFAULT_QUARANTINE_ROOT,
    DEFAULT_WORKSPACE_ROOT,
    InitOutcome,
    QuarantinePath,
    WorkspaceEntry,
    WorkspaceInitError,
    WorkspaceInitService,
    WorkspaceInitValidationError,
    WorkspacePath,
    WorkspacePathError,
    WorkspacePaths,
    WorkspaceRegistry,
    WorkspaceRole,
    build_paths,
    default_workspace_root,
    sanitize_id,
)
from src.coevo.workspace.paths import (
    PROJECT_ID_MAX,
    ROLE_ID_MAX,
)


def _build_committed_outcome(
    *,
    project_id: str = "PRJ001",
    package_id: str = "00000000-0000-0000-0000-000000000001",
    role_id_hint: str | None = None,
) -> ImportOutcome:
    """Build a synthetic ImportOutcome that has reached COMMITTED.

    Uses the real PackageImportService with an empty replay
    decision so the resulting transaction is in the COMMITTED
    state — the same shape the real import path produces.
    """
    # Build a minimal envelope + package via the protocol layer.
    import base64
    from src.coevo.protocol import (
        assemble_payload_block,
        build_envelope_template,
        build_key_transport_block,
        build_unsigned_package,
        check_replay,
    )
    # Use the package_id the caller passed, but if it's the
    # auto-generated UUID (None) the build_envelope_template will
    # mint its own. For the AC-8 idempotence test we need a
    # deterministic UUID, so callers must pass an explicit
    # package_id; the helper signature already enforces this via
    # the default below.
    import uuid as _uuid
    effective_package_id = package_id or str(_uuid.uuid4())
    nonce_b64 = base64.b64encode(b"\x00" * 12).decode("ascii")
    # We can't pass package_id into build_envelope_template; instead
    # build with no package_id and patch the resulting envelope.
    env = build_envelope_template(
        sender_cert_id="CERT-SENDER",
        recipient_cert_id="CERT-RECIPIENT",
        project_id=project_id,
        package_type="TASK_ASSIGNMENT",
        sequence_no=1,
        payload_length=16,
        nonce_b64=nonce_b64,
    )
    object.__setattr__(env, "package_id", effective_package_id)
    pkg = build_unsigned_package(
        envelope=env,
        key_block=build_key_transport_block(recipient_cert_id="CERT-RECIPIENT"),
        payload_block=assemble_payload_block(b"\x42" * 16),
    )
    replay = check_replay(candidate=ProcessedPackage(
        package_id=env.package_id,
        package_digest=f"{env.package_id}|{env.sequence_no}|{pkg.expected_total_length()}",
        sender_cert_id=env.sender_cert_id,
        recipient_cert_id=env.recipient_cert_id,
        project_id=env.project_id,
        sequence_no=env.sequence_no,
    ))
    service = PackageImportService()
    return service.import_package(
        package=pkg,
        replay_decision=replay,
        store=DEFAULT_EMPTY_STORE,
    )


# ----------------------- AC-2: QuarantinePath -----------------------


class TestQuarantinePath(unittest.TestCase):
    def test_quarantine_path_layout(self):
        qp = QuarantinePath(quarantine_root="quarantine", package_id="p.1")
        self.assertEqual("quarantine/p.1.agent", qp.as_posix())

    def test_quarantine_path_default_root(self):
        qp = QuarantinePath(quarantine_root=DEFAULT_QUARANTINE_ROOT, package_id="p.1")
        self.assertEqual(f"{DEFAULT_QUARANTINE_ROOT}/p.1.agent", qp.as_posix())

    def test_quarantine_path_rejects_traversal(self):
        with self.assertRaises(WorkspacePathError):
            QuarantinePath(quarantine_root="../etc", package_id="p.1")

    def test_quarantine_path_rejects_invalid_id(self):
        with self.assertRaises(WorkspacePathError):
            QuarantinePath(quarantine_root="quarantine", package_id="bad id with spaces")

    def test_quarantine_path_rejects_empty_root(self):
        with self.assertRaises(WorkspacePathError):
            QuarantinePath(quarantine_root="", package_id="p.1")


# ----------------------- AC-4: WorkspacePath -----------------------


class TestWorkspacePath(unittest.TestCase):
    def test_workspace_path_layout(self):
        wp = WorkspacePath(workspace_root="workspaces", project_id="PRJ001", role_id="a.pm")
        self.assertEqual("workspaces/PRJ001/a.pm", wp.as_posix())

    def test_workspace_path_default_root(self):
        wp = WorkspacePath(
            workspace_root=DEFAULT_WORKSPACE_ROOT, project_id="PRJ001", role_id="a.pm",
        )
        self.assertEqual(f"{DEFAULT_WORKSPACE_ROOT}/PRJ001/a.pm", wp.as_posix())

    def test_workspace_path_rejects_traversal(self):
        with self.assertRaises(WorkspacePathError):
            WorkspacePath(workspace_root="ws/../escaped", project_id="PRJ001", role_id="a.pm")

    def test_workspace_path_rejects_invalid_project_id(self):
        with self.assertRaises(WorkspacePathError):
            WorkspacePath(workspace_root="ws", project_id="bad project", role_id="a.pm")

    def test_workspace_path_rejects_invalid_role_id(self):
        with self.assertRaises(WorkspacePathError):
            WorkspacePath(workspace_root="ws", project_id="PRJ001", role_id="bad role")

    def test_workspace_path_rejects_empty_root(self):
        with self.assertRaises(WorkspacePathError):
            WorkspacePath(workspace_root="", project_id="PRJ001", role_id="a.pm")

    def test_sanitize_id_rejects_empty(self):
        with self.assertRaises(WorkspacePathError):
            sanitize_id("", name="x")

    def test_sanitize_id_rejects_too_long(self):
        with self.assertRaises(WorkspacePathError):
            sanitize_id("a" * (PROJECT_ID_MAX + 1), name="x")

    def test_sanitize_id_accepts_safe(self):
        self.assertEqual("a-b_c.d", sanitize_id("a-b_c.d", name="x"))


# ----------------------- AC-5: WorkspaceRegistry -----------------------


class TestWorkspaceRegistry(unittest.TestCase):
    def test_empty_registry(self):
        reg = WorkspaceRegistry.empty()
        self.assertEqual(0, len(reg))
        self.assertIsNone(reg.get("PRJ", "a.pm"))

    def test_register_then_get(self):
        reg = WorkspaceRegistry.empty()
        entry = WorkspaceEntry(
            project_id="PRJ", role_id="a.pm", package_id="p.1", revision="PRJ-R0001",
        )
        reg = reg.register(entry)
        self.assertEqual(1, len(reg))
        self.assertEqual(entry, reg.get("PRJ", "a.pm"))

    def test_register_rejects_duplicate_role(self):
        reg = WorkspaceRegistry.empty().register(
            WorkspaceEntry("PRJ", "a.pm", "p.1", "PRJ-R0001")
        )
        with self.assertRaises(WorkspaceInitValidationError):
            reg.register(WorkspaceEntry("PRJ", "a.pm", "p.2", "PRJ-R0002"))

    def test_register_rejects_duplicate_package_for_same_role(self):
        reg = WorkspaceRegistry.empty().register(
            WorkspaceEntry("PRJ", "a.pm", "p.1", "PRJ-R0001")
        )
        # Even with a different revision, same (project, role, package)
        # is rejected — AC-8 idempotence rule.
        with self.assertRaises(WorkspaceInitValidationError):
            reg.register(WorkspaceEntry("PRJ", "a.pm", "p.1", "PRJ-R0002"))

    def test_register_allows_same_package_for_different_role(self):
        reg = WorkspaceRegistry.empty()
        reg = reg.register(WorkspaceEntry("PRJ", "a.pm", "p.1", "PRJ-R0001"))
        reg = reg.register(WorkspaceEntry("PRJ", "a.eng", "p.1", "PRJ-R0001"))
        self.assertEqual(2, len(reg))

    def test_by_package(self):
        reg = WorkspaceRegistry.empty()
        reg = reg.register(WorkspaceEntry("PRJ1", "a.pm", "p.1", "PRJ1-R0001"))
        reg = reg.register(WorkspaceEntry("PRJ2", "a.pm", "p.1", "PRJ2-R0001"))
        recs = reg.by_package("p.1")
        self.assertEqual(2, len(recs))


# ----------------------- AC-7 + AC-8: WorkspaceInitService -----------------------


class TestWorkspaceInitService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = WorkspaceInitService()

    def test_init_creates_workspace_for_committed_import(self):
        outcome = _build_committed_outcome()
        self.assertEqual(ImportStep.COMMITTED, outcome.transaction.step)
        reg = WorkspaceRegistry.empty()
        result = self.service.init_from_import(
            import_outcome=outcome, registry=reg, role_id="a.pm",
        )
        self.assertTrue(result.created)
        self.assertIsNotNone(result.entry)
        self.assertEqual(1, len(result.registry))
        # Path layout: quarantine / staging / workspace all populated
        self.assertTrue(result.paths.quarantine.as_posix().endswith(".agent"))
        self.assertIn("PRJ001", result.paths.workspace.as_posix())
        self.assertIn("a.pm", result.paths.workspace.as_posix())

    def test_init_rejects_rolled_back_import(self):
        # Build a synthetic rolled-back transaction directly
        # (faster than the full import path; the service is
        # already validated by the previous test).
        tx = ImportTransaction(
            package_id="p.1", project_id="PRJ001",
            base_revision=None, current_revision=None,
            step=ImportStep.ROLLED_BACK,
            failure_reason="simulated",
            completed_steps=(),
        )
        outcome = ImportOutcome(
            transaction=tx, store=ProcessedPackageStore.empty(), record=None,
        )
        reg = WorkspaceRegistry.empty()
        result = self.service.init_from_import(
            import_outcome=outcome, registry=reg, role_id="a.pm",
        )
        self.assertFalse(result.created)
        self.assertIsNone(result.entry)
        self.assertEqual(0, len(result.registry))
        self.assertIn("not COMMITTED", result.failure_reason)

    def test_init_idempotent_on_duplicate_package(self):
        # AC-8: same package_id re-imported for the same
        # (project, role) is a no-op.
        outcome = _build_committed_outcome()
        reg = WorkspaceRegistry.empty()
        first = self.service.init_from_import(
            import_outcome=outcome, registry=reg, role_id="a.pm",
        )
        self.assertTrue(first.created)
        # Re-import: a new ImportOutcome with the same package_id.
        outcome2 = _build_committed_outcome()  # same package_id (UUID is fixed above)
        second = self.service.init_from_import(
            import_outcome=outcome2, registry=first.registry, role_id="a.pm",
        )
        self.assertFalse(second.created)
        self.assertEqual(1, len(second.registry))
        self.assertIn("already initialized", second.failure_reason)

    def test_init_allows_same_package_different_role(self):
        outcome = _build_committed_outcome()
        reg = WorkspaceRegistry.empty()
        first = self.service.init_from_import(
            import_outcome=outcome, registry=reg, role_id="a.pm",
        )
        second = self.service.init_from_import(
            import_outcome=outcome, registry=first.registry, role_id="a.eng",
        )
        self.assertTrue(first.created)
        self.assertTrue(second.created)
        self.assertEqual(2, len(second.registry))

    def test_init_rejects_invalid_role_id(self):
        outcome = _build_committed_outcome()
        with self.assertRaises(WorkspaceInitValidationError):
            self.service.init_from_import(
                import_outcome=outcome,
                registry=WorkspaceRegistry.empty(),
                role_id="bad role with spaces",
            )

    def test_init_rejects_non_import_outcome(self):
        with self.assertRaises(WorkspaceInitError):
            self.service.init_from_import(
                import_outcome="not an ImportOutcome",
                registry=WorkspaceRegistry.empty(),
                role_id="a.pm",
            )

    def test_audit_record_is_json_safe_on_success(self):
        outcome = _build_committed_outcome()
        reg = WorkspaceRegistry.empty()
        result = self.service.init_from_import(
            import_outcome=outcome, registry=reg, role_id="a.pm",
        )
        record = self.service.to_audit_record(result)
        s = json.dumps(record)
        self.assertEqual(record, json.loads(s))
        self.assertTrue(record["created"])
        self.assertEqual("PRJ001", record["project_id"])
        self.assertEqual("a.pm", record["role_id"])

    def test_audit_record_on_rejection(self):
        tx = ImportTransaction(
            package_id="p.1", project_id="PRJ001",
            base_revision=None, current_revision=None,
            step=ImportStep.ROLLED_BACK, failure_reason="simulated",
            completed_steps=(),
        )
        outcome = ImportOutcome(
            transaction=tx, store=ProcessedPackageStore.empty(), record=None,
        )
        result = self.service.init_from_import(
            import_outcome=outcome, registry=WorkspaceRegistry.empty(), role_id="a.pm",
        )
        record = self.service.to_audit_record(result)
        s = json.dumps(record)
        self.assertEqual(record, json.loads(s))
        self.assertFalse(record["created"])
        self.assertIn("not COMMITTED", record["failure_reason"])


# ----------------------- build_paths -----------------------


class TestBuildPaths(unittest.TestCase):
    def test_build_paths_default_roots(self):
        paths = build_paths(project_id="PRJ", role_id="a.pm", package_id="p.1")
        self.assertEqual(f"{DEFAULT_QUARANTINE_ROOT}/p.1.agent", paths.quarantine.as_posix())
        self.assertEqual("staging/p.1", paths.staging_root)
        self.assertEqual(f"{DEFAULT_WORKSPACE_ROOT}/PRJ/a.pm", paths.workspace.as_posix())

    def test_build_paths_custom_roots(self):
        paths = build_paths(
            project_id="PRJ", role_id="a.pm", package_id="p.1",
            quarantine_root="q", workspace_root="w", staging_root="s/p.1",
        )
        self.assertEqual("q/p.1.agent", paths.quarantine.as_posix())
        self.assertEqual("s/p.1", paths.staging_root)
        self.assertEqual("w/PRJ/a.pm", paths.workspace.as_posix())


if __name__ == "__main__":
    unittest.main()