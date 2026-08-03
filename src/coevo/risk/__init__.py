"""Deterministic, pure post-merge risk analysis for US-11-AC-1."""

from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass
from typing import Iterable
from src.coevo.merge import MergeCommitOutcome, MergeEngine
from src.coevo.merge.receipt import BASELINE_DIGEST_ALGORITHM, BASELINE_SCHEMA, MergeCommitReceipt
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.processed_package_store import ProcessedPackageStore
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import ProjectBaseline

from .models import (MergeAndAnalyzeOutcome, Risk, RiskAnalysisError, RiskKind, RiskReport, RiskValidationError, SourceKind, _non_empty, _parse_utc, _source_kind_counts)

from .analyzer import (RiskAnalyzer, _descendants, _plus_days, _risk, _validated_graph, _validated_receipt, analyze_after_merge, merge_and_analyze)

__all__ = [
    "MergeAndAnalyzeOutcome", "Risk", "RiskAnalyzer", "RiskAnalysisError",
    "RiskKind", "RiskReport", "RiskValidationError", "SourceKind",
    "analyze_after_merge", "merge_and_analyze",
]
