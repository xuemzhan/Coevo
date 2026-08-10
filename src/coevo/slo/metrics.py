"""SLO metric aggregators (ARCH-REVIEW-6).

Maps the gateable subset of system-requirements §20 acceptance metrics to
deterministic, offline-computable ratios. Model/network-dependent metrics
(accuracy rates, human-adoption rates) are explicitly pilot-measured and
documented in docs/architecture/slo-metrics.md -- they are NOT computed here.

Fail-closed conventions:
* an empty denominator yields 0.0 (a metric with no evidence fails the gate);
* `assert_slo_thresholds` rejects unknown metric names.
"""

from __future__ import annotations

from typing import Mapping, Sequence


class SloValidationError(ValueError):
    """Raised when SLO inputs are malformed (fail-closed)."""


SLO_DEFAULTS: Mapping[str, float] = {
    "dispatch_success": 0.95,     # §20.2 常规调度成功率 >= 95%
    "replay_rejection": 1.0,      # §20.3 重复包识别率 100%
    "interception": 1.0,          # §20.3 非法/损坏/验签失败包拦截率 100%
    "audit_coverage": 1.0,        # §20.4 关键操作审计覆盖率 100%
    "package_round_trip": 1.0,    # §20.3 任务包生成/加密/导入/验签闭环
}


def _ratio(ok: int, total: int, label: str) -> float:
    if not isinstance(ok, int) or not isinstance(total, int) or ok < 0 or total < 0:
        raise SloValidationError(f"{label} counts must be non-negative integers")
    if total == 0:
        return 0.0  # no evidence -> fail closed
    if ok > total:
        raise SloValidationError(f"{label} ok count exceeds total")
    return ok / total


def dispatch_success_rate(outcomes: Sequence[str]) -> float:
    """Fraction of orchestration dispatches that completed (empty -> 0.0)."""

    if not isinstance(outcomes, Sequence) or isinstance(outcomes, (str, bytes)):
        raise SloValidationError("outcomes must be a sequence of outcome strings")
    return _ratio(
        sum(1 for outcome in outcomes if outcome == "completed"),
        len(outcomes),
        "dispatch_success",
    )


def replay_rejection_rate(rejected: int, total: int) -> float:
    """Duplicate-package rejection rate (§20.3: 100%)."""

    return _ratio(rejected, total, "replay_rejection")


def interception_rate(blocked: int, total: int) -> float:
    """Invalid/tampered package interception rate (§20.3: 100%)."""

    return _ratio(blocked, total, "interception")


def audit_coverage(
    observed: Sequence[str], required: Sequence[str]
) -> float:
    """Key-operation audit coverage (required actions all observed).

    An empty `required` set is trivially covered (1.0); a non-empty
    `required` with no observations fails closed (0.0).
    """

    if not isinstance(observed, Sequence) or isinstance(observed, (str, bytes)):
        raise SloValidationError("observed must be a sequence of action names")
    if not isinstance(required, Sequence) or isinstance(required, (str, bytes)):
        raise SloValidationError("required must be a sequence of action names")
    if not required:
        return 1.0
    seen = set(observed)
    return len([action for action in required if action in seen]) / len(required)


def package_round_trip_rate(round_trips_ok: int, total: int) -> float:
    """Encrypted package build/parse/open round-trip success (§20.3)."""

    return _ratio(round_trips_ok, total, "package_round_trip")


def assert_slo_thresholds(
    metrics: Mapping[str, float],
    *,
    thresholds: Mapping[str, float] | None = None,
) -> list[str]:
    """Return threshold violations; unknown metrics are violations too."""

    if not isinstance(metrics, Mapping):
        raise SloValidationError("metrics must be a mapping")
    rules = dict(SLO_DEFAULTS if thresholds is None else thresholds)
    violations: list[str] = []
    for name, value in metrics.items():
        if name not in rules:
            violations.append(f"unknown SLO metric: {name!r}")
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            violations.append(f"{name}: value must be numeric")
            continue
        if value < rules[name]:
            violations.append(
                f"{name}: {value:.3f} < threshold {rules[name]:.3f}"
            )
    return violations


__all__ = [
    "SLO_DEFAULTS",
    "SloValidationError",
    "assert_slo_thresholds",
    "audit_coverage",
    "dispatch_success_rate",
    "interception_rate",
    "package_round_trip_rate",
    "replay_rejection_rate",
]
