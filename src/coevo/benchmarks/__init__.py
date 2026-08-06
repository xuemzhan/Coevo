"""Offline performance benchmark suite (MVP reference architecture 14).

Establishes reproducible, offline measurements for the reference SLA
targets so the project stops guessing and starts tracking:

* page open / project view       <= 3s
* local task query               <= 2s
* small package baseline check   <= 10s
* directory file discovery       <= 5s
* package generation success     >= 95%

The harness is pure and small; the actual measurements live in
``scripts/benchmark.py`` so they are not part of the quality gate
(timing runs are environment-dependent and must not gate CI)."""

from __future__ import annotations

from .models import (SCALABILITY_PROBES, SLA_TARGETS, SlaTarget)

from .harness import (BenchmarkResult, measure, report)
