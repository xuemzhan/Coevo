"""benchmarks.harness - BenchmarkResult, measure() and report() measurement harness."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 基准测量框架：BenchmarkResult / measure / report，SLA 比较与采样。

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class BenchmarkResult:
    """A single measured result against its SLA target."""

    name: str
    metric: str
    value: float
    unit: str
    limit: float
    comparison: str
    ok: bool
    samples: int
    detail: str = ""

    def to_mapping(self) -> dict[str, Any]:
        """Project the benchmark result to a JSON-safe mapping."""
        return {
            "name": self.name,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "limit": self.limit,
            "comparison": self.comparison,
            "ok": self.ok,
            "samples": self.samples,
            "detail": self.detail,
        }

def measure(
    name: str,
    metric: str,
    fn: Callable[[], Any],
    *,
    limit: float,
    unit: str,
    comparison: str = "le",
    samples: int = 1,
) -> BenchmarkResult:
    """Time ``fn`` (optionally repeated) and compare against the limit."""
    if not callable(fn):
        raise TypeError("fn must be callable")
    if not isinstance(samples, int) or samples < 1:
        raise ValueError("samples must be a positive integer")
    if not isinstance(limit, (int, float)) or limit <= 0:
        raise ValueError("limit must be positive")
    if comparison not in {"le", "ge"}:
        raise ValueError("comparison must be 'le' or 'ge'")
    start = time.perf_counter()
    outcome: Any = None
    for _ in range(samples):
        outcome = fn()
    elapsed = time.perf_counter() - start
    value = elapsed / samples if comparison == "le" else float(outcome)
    ok = value <= limit if comparison == "le" else value >= limit
    return BenchmarkResult(
        name=name,
        metric=metric,
        value=round(value, 4),
        unit=unit,
        limit=limit,
        comparison=comparison,
        ok=ok,
        samples=samples,
    )

def report(results: tuple[BenchmarkResult, ...]) -> dict[str, Any]:
    """JSON-safe report for the record."""
    if not results:
        raise ValueError("report requires at least one result")
    return {
        "schema_version": "1.0",
        "all_ok": all(result.ok for result in results),
        "results": [result.to_mapping() for result in results],
    }
