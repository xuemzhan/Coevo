"""PRODUCT-REVIEW T-05: production composition root contract guard.

The production entry must exist, reject demo/prototype components by
default, and stay isolated from the demo composition root.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

from src.coevo.app.production import (
    ProductionCompositionError,
    run_production_pipeline,
    validate_production_composition,
)
from src.coevo.app.demo_support import (
    DemoFreshnessAuthority,
    DemoSigner,
)
from src.coevo.crypto.contract import ProviderScope
from src.coevo.framework.policy import (
    PolicyValidationError,
    get_default_profile,
)
from src.coevo.identity.service import PolicyAuthorizer


class _FakeApprovedProvider:
    scope = ProviderScope.APPROVED_PRODUCT


class _FakePrototypeProvider:
    scope = ProviderScope.MVP_PROTOTYPE


class _AllowAllScopeRbac:  # 演示结构性放行器，类型名与 demo 一致
    pass


class _RealSigner:
    def sign(self, content: bytes) -> bytes:
        return b"sig"

    def verify(self, content: bytes, signature: bytes) -> None:
        return None


class _RealFreshness:
    def create_marker(self, store_id, generation, binding):
        return {}

    def verify_marker(self, marker):
        return None

    def delete_marker(self, marker):
        return None

    def verify_retired(self, marker):
        return None

    def sign(self, content, marker):
        return b"sig"

    def verify_signature(self, content, signature, marker):
        return None

    def store_retirement(self, tombstone, main_sig, backup_sig):
        return None


class _RealAuthorizer:
    def authorize(self, actor, action):
        return True


class ProductionCompositionTests(unittest.TestCase):
    def test_accepts_approved_composition(self):
        validate_production_composition(
            provider=_FakeApprovedProvider(),
            signer=_RealSigner(),
            authorizer=_RealAuthorizer(),
            freshness=_RealFreshness(),
        )

    def test_rejects_prototype_provider(self):
        with self.assertRaises(ProductionCompositionError):
            validate_production_composition(
                provider=_FakePrototypeProvider(),
                signer=_RealSigner(),
                authorizer=_RealAuthorizer(),
                freshness=_RealFreshness(),
            )

    def test_rejects_demo_signer(self):
        with self.assertRaises(ProductionCompositionError):
            validate_production_composition(
                provider=_FakeApprovedProvider(),
                signer=DemoSigner(),
                authorizer=_RealAuthorizer(),
                freshness=_RealFreshness(),
            )

    def test_rejects_demo_freshness(self):
        with self.assertRaises(ProductionCompositionError):
            validate_production_composition(
                provider=_FakeApprovedProvider(),
                signer=_RealSigner(),
                authorizer=_RealAuthorizer(),
                freshness=DemoFreshnessAuthority(),
            )

    def test_rejects_allow_all_rbac(self):
        with self.assertRaises(ProductionCompositionError):
            validate_production_composition(
                provider=_FakeApprovedProvider(),
                signer=_RealSigner(),
                authorizer=_AllowAllScopeRbac(),
                freshness=_RealFreshness(),
            )

    def test_run_pipeline_rejects_demo_before_touching_chain(self):
        # 组合校验必须先于真实链：demo signer 必须在不创建 store 的情况下失败。
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            with self.assertRaises(ProductionCompositionError):
                run_production_pipeline(
                    run_dir,
                    provider=_FakeApprovedProvider(),
                    signer=DemoSigner(),
                    authorizer=_RealAuthorizer(),
                    freshness=_RealFreshness(),
                    registry=None,
                    executor=None,
                    chain=None,
                    event=None,
                    workspace=None,
                    project_input={},
                    actor=None,
                    now="2026-08-12T00:00:00Z",
                )
            self.assertFalse((run_dir / "real-chain.db").exists())

    def test_production_entry_calls_validation_first(self):
        source = (
            ROOT / "src" / "coevo" / "app" / "production.py"
        ).read_text(encoding="utf-8")
        # 生产入口必须显式调用组合校验；demo 组合根不得反向依赖生产入口。
        self.assertIn("validate_production_composition(", source)
        idx_run = source.find("def run_production_pipeline")
        idx_validate = source.find("validate_production_composition(")
        self.assertLess(idx_validate, idx_run)

    def test_policy_authorizer_is_fail_closed(self):
        auth = PolicyAuthorizer(
            {"u.pm": frozenset({"orchestrator:confirm-package:PRJ001"})},
            policy=get_default_profile("INTERACTIVE"),
        )
        self.assertTrue(
            auth.is_allowed("u.pm", "orchestrator:confirm-package:PRJ001")
        )
        self.assertFalse(auth.is_allowed("u.pm", "merge:apply"))
        self.assertFalse(auth.is_allowed("u.qa", "orchestrator:confirm-package:PRJ001"))
        self.assertFalse(auth.is_allowed("", "orchestrator:confirm-package:PRJ001"))

    def test_policy_authorizer_rejects_invalid_policy(self):
        with self.assertRaises(PolicyValidationError):
            PolicyAuthorizer(
                {"u.pm": frozenset({"x:y"})},
                policy=get_default_profile("NOT-A-PROFILE"),
            )

    def test_run_pipeline_defaults_authorizer_from_grants(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            # authorizer 缺省时由 grants 构造 PolicyAuthorizer；demo signer
            # 仍必须先于真实链被拒绝。
            with self.assertRaises(ProductionCompositionError):
                run_production_pipeline(
                    run_dir,
                    provider=_FakeApprovedProvider(),
                    signer=DemoSigner(),
                    authorizer=None,
                    freshness=_RealFreshness(),
                    registry=None,
                    executor=None,
                    chain=None,
                    event=None,
                    workspace=None,
                    project_input={},
                    actor=None,
                    now="2026-08-12T00:00:00Z",
                    grants={"u.pm": frozenset({"orchestrator:confirm-package:PRJ001"})},
                )
            self.assertFalse((run_dir / "real-chain.db").exists())

    def test_run_pipeline_requires_grants_when_authorizer_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            with self.assertRaises(ProductionCompositionError):
                run_production_pipeline(
                    run_dir,
                    provider=_FakeApprovedProvider(),
                    signer=_RealSigner(),
                    authorizer=None,
                    freshness=_RealFreshness(),
                    registry=None,
                    executor=None,
                    chain=None,
                    event=None,
                    workspace=None,
                    project_input={},
                    actor=None,
                    now="2026-08-12T00:00:00Z",
                )

    def test_protected_provider_declares_approved_scope(self):
        """T-06 前置：受保护提供者必须满足生产入口的 scope 门禁。"""
        provider_src = (
            ROOT / "src" / "coevo" / "crypto" / "protected_provider.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "ProviderScope.APPROVED_PRODUCT",
            provider_src,
        )
        production_src = (
            ROOT / "src" / "coevo" / "app" / "production.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "ProviderScope.APPROVED_PRODUCT",
            production_src,
        )


if __name__ == "__main__":
    unittest.main()
