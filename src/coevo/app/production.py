"""app.production - production composition root contract (PRODUCT-REVIEW T-05).

The demo composition root (``app/pipeline.py``) is explicitly NOT
production: it injects ``DemoSigner`` / ``DemoFreshnessAuthority`` / the
GmSSL prototype provider / allow-all structural RBAC. Production entry
points MUST validate the composition before touching the real chain:
reject demo components and require an ``APPROVED_PRODUCT`` crypto provider.

Wiring note (T-06): the approved SM2/SM4 product and certificate-chain
resolver land here. Until then the validated entry runs only in tests with
injected real-shaped components.
"""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 生产组合根契约：先验组合（拒绝 demo/原型），再走真实链；
# 与 demo 组合根（pipeline.py）隔离，防止演示注入污染生产路径。
from __future__ import annotations

from pathlib import Path
from typing import Any

from src.coevo.crypto.contract import ProviderScope


_DEMO_TYPE_NAMES: frozenset[str] = frozenset({
    "DemoSigner",
    "DemoFreshnessAuthority",
    "_AllowAllScopeRbac",
})


class ProductionCompositionError(RuntimeError):
    """A production composition gate rejected a demo/prototype component."""


def validate_production_composition(
    *,
    provider: Any,
    signer: Any,
    authorizer: Any,
    freshness: Any,
) -> None:
    """Fail-closed composition gate for the production chain entry."""
    scope = getattr(provider, "scope", None)
    if scope != ProviderScope.APPROVED_PRODUCT:
        raise ProductionCompositionError(
            "provider must be APPROVED_PRODUCT; got "
            f"{type(provider).__name__!r}"
        )
    for label, component in (
        ("signer", signer),
        ("freshness", freshness),
        ("authorizer", authorizer),
    ):
        type_name = type(component).__name__
        if type_name in _DEMO_TYPE_NAMES:
            raise ProductionCompositionError(
                f"{label} must not use demo component {type_name!r}"
            )


def production_entry_contract() -> dict[str, str]:
    """Declare the ports a production entry must satisfy (for docs/tests)."""
    return {
        "provider": "CryptoProvider with scope APPROVED_PRODUCT",
        "signer": "Signer (not DemoSigner)",
        "freshness": "FreshnessAuthority (not DemoFreshnessAuthority)",
        "authorizer": "Authorizer (not allow-all structural RBAC)",
        "registry": "AgentRegistry built with production resolver/verifier",
        "executor": "RealChainExecutor with production facades",
    }


def run_production_pipeline(
    runtime_dir: Path,
    *,
    provider: Any,
    signer: Any,
    authorizer: Any,
    freshness: Any,
    registry: Any,
    executor: Any,
    chain: Any,
    event: Any,
    workspace: Any,
    project_input: dict[str, Any],
    actor: Any,
    now: str,
    grants: dict[str, frozenset[str]] | None = None,
) -> tuple[Any, Any]:
    """Validated production entry: run the fixed chain with injected ports.

    Composition is validated first; any demo/prototype component aborts
    before the real chain is touched. Returns ``(completed, store)``; the
    caller owns the store lifecycle.
    """
    if authorizer is None:
        if grants is None:
            raise ProductionCompositionError(
                "production entry requires an authorizer or explicit grants"
            )
        from src.coevo.identity.service import PolicyAuthorizer

        authorizer = PolicyAuthorizer(grants)
    validate_production_composition(
        provider=provider,
        signer=signer,
        authorizer=authorizer,
        freshness=freshness,
    )
    from src.coevo.orchestrator import (
        Orchestrator,
        RealChainStore,
    )

    store = RealChainStore.create(
        Path(runtime_dir) / "real-chain.db",
        signer=signer,
        freshness=freshness,
    )
    held = Orchestrator.dispatch_event_with_real_facades(
        registry,
        chain,
        event,
        workspace=workspace,
        executor=executor,
        project_input=project_input,
        store=store,
        now=now,
    )
    confirmed = Orchestrator.confirm_real_chain(
        held,
        preview=held.package_preview,
        actor=actor,
        authorizer=authorizer,
        store=store,
        now=now,
    )
    completed = Orchestrator.resume_real_chain(
        confirmed,
        registry=registry,
        chain=chain,
        event=event,
        workspace=workspace,
        executor=executor,
        store=store,
        now=now,
        crypto_provider=provider,
    )
    return completed, store
