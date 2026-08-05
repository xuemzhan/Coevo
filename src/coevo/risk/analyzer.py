"""risk.analyzer - deterministic RiskAnalyzer facade, merge+analyze hook and their private helpers (US-11)."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 风险预警引擎（US-11）：
#   analyze_after_merge()：只分析“最新权威回执”对应的合并后状态，
#     回执链不连续或非最新即拒绝（防止用旧状态算风险）。
#   识别四类基础风险（AC-2）：
#     DEADLINE_OVERRUN（事实型：任务/项目截止已过，严重度 4 → 建议会议）；
#     INSUFFICIENT_EVIDENCE（事实型：权威回执中的完成标记不足）；
#     LONG_SILENCE（事实型：超过阈值无合并反馈）；
#     PREDECESSOR_UNFINISHED（规则型：前置任务无完成标记，影响后继）。
#   另支持 AT_RISK/BLOCKED 传染（推断型）与严重协调建议
#     SEVERE_COORDINATION_NEEDED（规则型）。
#   merge_and_analyze()：合并 + 回执 + 风险分析一站式钩子，供回传链
#     调用；合并未接受则不产生风险报告。
#   关键不变量：风险报告仅“候选”，正式发布前必须负责人确认
#     （requires_owner_confirmation=True 强制）。

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable
from src.coevo.merge import MergeEngine
from src.coevo.merge.receipt import BASELINE_DIGEST_ALGORITHM, BASELINE_SCHEMA, MergeCommitReceipt
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.protocol.import_service import ImportOutcome
from src.coevo.protocol.processed_package_store import ProcessedPackageStore
from src.coevo.report import ReportManifest, ReportStatus
from src.coevo.task_decomposition import ProjectBaseline

from .models import MergeAndAnalyzeOutcome, Risk, RiskAnalysisError, RiskKind, RiskReport, RiskValidationError, SourceKind, _parse_utc, _source_kind_counts

@dataclass(frozen=True)
class RiskAnalyzer:
    silence_threshold_days: int = 14
    evidence_shortfall_threshold: int = 1
    severe_severity_threshold: int = 4

    def __post_init__(self) -> None:
        for value, name in (
            (self.silence_threshold_days, "silence_threshold_days"),
            (self.evidence_shortfall_threshold, "evidence_shortfall_threshold"),
            (self.severe_severity_threshold, "severe_severity_threshold"),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
        if self.silence_threshold_days < 1:
            raise ValueError("silence_threshold_days must be positive")
        if self.evidence_shortfall_threshold < 1:
            raise ValueError("evidence_shortfall_threshold must be positive")
        if not 1 <= self.severe_severity_threshold <= 5:
            raise ValueError("severe_severity_threshold must be in [1, 5]")

    def analyze_after_merge(
        self,
        *,
        receipt_id: str,
        receipt_repository: MergeReceiptRepository,
        now: str,
    ) -> RiskReport:
        """Analyze only an authoritative receipt selected from its store."""
        receipt, baseline, history = _validated_receipt(
            receipt_id=receipt_id,
            receipt_repository=receipt_repository,
            now=now,
        )
        return self._analyze(
            receipt=receipt,
            receipt_history=history,
            baseline=baseline,
            now=now,
        )

    def _analyze(
        self,
        *,
        receipt: MergeCommitReceipt,
        receipt_history: tuple[MergeCommitReceipt, ...],
        baseline: ProjectBaseline,
        now: str,
    ) -> RiskReport:
        reference_time = _parse_utc(now, field="now")
        decided_time = _parse_utc(
            receipt.commit_decided_at, field="receipt.commit_decided_at",
        )
        if reference_time < decided_time:
            raise RiskValidationError("now must not precede receipt commit_decided_at")

        tasks, successors = _validated_graph(baseline)
        all_tasks = tuple(sorted(tasks))
        package_id = receipt.package_id
        risks: list[Risk] = []
        project_receipts = tuple(
            item for item in receipt_history if item.project_id == baseline.project_id
        )
        if not project_receipts or project_receipts[-1] != receipt:
            raise RiskValidationError(
                "receipt must be the latest authoritative project commit"
            )
        completed_task_ids = {
            historical.completed_task_id
            for historical in project_receipts
            if historical.completed_task_id is not None
        }
        if not completed_task_ids.issubset(tasks):
            raise RiskValidationError(
                "receipt history contains completion for an unknown task"
            )

        overdue = tuple(sorted(
            task_id for task_id, task in tasks.items()
            if _parse_utc(task.plan_end, field=f"task {task_id}.plan_end") < reference_time
        ))
        project_end = _parse_utc(baseline.plan_end, field="baseline.plan_end")
        if overdue or project_end < reference_time:
            risks.append(_risk(
                package_id, RiskKind.DEADLINE_OVERRUN, SourceKind.FACTUAL,
                f"task/project deadline precedes now {now!r} (AC-2 deadline)",
                overdue or all_tasks,
                "renegotiate the plan or escalate to the project owner",
                reference_time, 7, 4, "factual deadline overrun",
            ))

        if len(completed_task_ids) < self.evidence_shortfall_threshold:
            risks.append(_risk(
                package_id, RiskKind.INSUFFICIENT_EVIDENCE, SourceKind.FACTUAL,
                "authoritative receipts contain insufficient completed tasks (AC-2 evidence)",
                all_tasks, "request accepted completed-work evidence",
                reference_time, 3, 2, "factual evidence shortfall",
            ))

        if reference_time - decided_time >= dt.timedelta(days=self.silence_threshold_days):
            risks.append(_risk(
                package_id, RiskKind.LONG_SILENCE, SourceKind.FACTUAL,
                f"no merged feedback for at least {self.silence_threshold_days} days (AC-2 silence)",
                all_tasks, "follow up with the reporter and review the task plan",
                reference_time, 2, 3, "factual long-silence detection",
            ))

        unfinished = tuple(sorted({
            edge.predecessor_task_id for edge in baseline.dependencies
            if edge.predecessor_task_id not in completed_task_ids
        }))
        if unfinished:
            affected = _descendants(unfinished, successors)
            risks.append(_risk(
                package_id, RiskKind.PREDECESSOR_UNFINISHED, SourceKind.RULE,
                f"predecessors {unfinished!r} lack accepted completion markers (AC-2 predecessor)",
                affected, "confirm predecessor completion before starting successors",
                reference_time, 5, 3, "deterministic dependency-edge rule",
            ))

        dependent_tasks = tuple(sorted({
            task_id for values in successors.values() for task_id in values
        })) or all_tasks
        if receipt.report_status is ReportStatus.AT_RISK:
            risks.append(_risk(
                package_id, RiskKind.AT_RISK_BLOOM, SourceKind.INFERRED,
                "merged status is AT_RISK; dependent tasks may inherit risk (AC-4 inferred)",
                dependent_tasks, "schedule a checkpoint before the next deliverable",
                reference_time, 3, 2, "deterministic AT_RISK propagation heuristic",
            ))
        elif receipt.report_status is ReportStatus.BLOCKED:
            risks.append(_risk(
                package_id, RiskKind.BLOCKED_BLOOM, SourceKind.INFERRED,
                "merged status is BLOCKED; dependent tasks may stall (AC-4 inferred)",
                dependent_tasks, "prepare a coordination-meeting proposal for owner review",
                reference_time, 1, 4, "deterministic BLOCKED propagation heuristic",
            ))

        coordination = any(
            risk.severity >= self.severe_severity_threshold for risk in risks
        )
        if coordination:
            affected = tuple(sorted({
                task_id for risk in risks for task_id in risk.affected_tasks
            }))
            risks.append(_risk(
                package_id, RiskKind.SEVERE_COORDINATION_NEEDED, SourceKind.RULE,
                f"risk severity reached {self.severe_severity_threshold} (AC-7 suggestion only)",
                affected, "request owner confirmation before starting a meeting",
                reference_time, 2, 4,
                "coordination threshold rule; no meeting was started",
            ))

        risks.sort(key=lambda risk: (risk.kind.value, risk.risk_id))
        return RiskReport(
            merge_reporter_package_id=package_id,
            project_id=baseline.project_id,
            analysed_at=now,
            risks=tuple(risks),
            coordination_meeting_recommended=coordination,
        )

    def to_audit_record(self, report: RiskReport) -> dict[str, object]:
        """Project a risk report to an audit record."""
        if not isinstance(report, RiskReport):
            raise RiskAnalysisError("report must be RiskReport")
        return {
            "kind": "risk.analysis",
            "schema_version": "1.0",
            "merge_reporter_package_id": report.merge_reporter_package_id,
            "project_id": report.project_id,
            "analysed_at": report.analysed_at,
            "risk_count": len(report.risks),
            "risk_ids": [risk.risk_id for risk in report.risks],
            "source_kind_counts": _source_kind_counts(report.risks),
            "coordination_meeting_recommended": report.coordination_meeting_recommended,
            "requires_owner_confirmation": True,
            "formally_released": False,
        }

def analyze_after_merge(
    *,
    receipt_id: str,
    receipt_repository: MergeReceiptRepository,
    now: str,
    analyzer: RiskAnalyzer | None = None,
) -> RiskReport:
    """Pure authoritative-receipt risk-analysis hook."""
    risk_analyzer = analyzer if analyzer is not None else RiskAnalyzer()
    if not isinstance(risk_analyzer, RiskAnalyzer):
        raise RiskAnalysisError("analyzer must be RiskAnalyzer")
    return risk_analyzer.analyze_after_merge(
        receipt_id=receipt_id,
        receipt_repository=receipt_repository,
        now=now,
    )

def merge_and_analyze(
    *,
    engine: MergeEngine,
    import_outcome: ImportOutcome,
    report: ReportManifest,
    baseline: ProjectBaseline,
    store: ProcessedPackageStore,
    receipt_repository: MergeReceiptRepository,
    decided_at: str,
    now: str,
    authorized_recipient_certs: frozenset[str] | None = None,
    analyzer: RiskAnalyzer | None = None,
) -> MergeAndAnalyzeOutcome:
    """Real merge→receipt→risk facade; failed merges produce no risk."""
    if not isinstance(engine, MergeEngine):
        raise RiskAnalysisError("engine must be MergeEngine")
    risk_analyzer = analyzer if analyzer is not None else RiskAnalyzer()
    if not isinstance(risk_analyzer, RiskAnalyzer):
        raise RiskAnalysisError("analyzer must be RiskAnalyzer")
    commit = engine.merge_and_commit(
        import_outcome=import_outcome,
        report=report,
        baseline=baseline,
        store=store,
        decided_at=decided_at,
        authorized_recipient_certs=authorized_recipient_certs,
    )
    if commit.receipt is None:
        return MergeAndAnalyzeOutcome(commit=commit, risk_report=None)
    risk_report = risk_analyzer.analyze_after_merge(
        receipt_id=commit.receipt.receipt_id,
        receipt_repository=receipt_repository,
        now=now,
    )
    return MergeAndAnalyzeOutcome(commit=commit, risk_report=risk_report)

def _validated_receipt(
    *,
    receipt_id: str,
    receipt_repository: MergeReceiptRepository,
    now: str,
) -> tuple[MergeCommitReceipt, ProjectBaseline, tuple[MergeCommitReceipt, ...]]:
    if not isinstance(receipt_id, str) or not receipt_id:
        raise RiskValidationError("receipt_id must be a non-empty string")
    if type(receipt_repository) is not MergeReceiptRepository:
        raise RiskValidationError("receipt_repository must be controlled repository")
    try:
        trusted_time = _parse_utc(now, field="now")
        receipt = receipt_repository.get_verified(
            receipt_id, trusted_time=trusted_time,
        )
        history = receipt_repository.verified_history(trusted_time=trusted_time)
    except Exception as exc:
        raise RiskValidationError("receipt signature/trust verification failed") from exc
    snapshot = receipt.snapshot
    baseline = snapshot.baseline
    expected_revision = f"{baseline.project_id}-R{baseline.version:04d}"
    if receipt.merged_revision != expected_revision:
        raise RiskValidationError("receipt revision does not match baseline version")
    if receipt.baseline_digest_algorithm != BASELINE_DIGEST_ALGORITHM:
        raise RiskValidationError("receipt uses unsupported baseline digest")
    if receipt.baseline_schema != BASELINE_SCHEMA:
        raise RiskValidationError("receipt uses unsupported baseline schema")
    if receipt.baseline_digest != snapshot.digest:
        raise RiskValidationError("baseline digest does not match committed receipt")
    if receipt.decision_maker != receipt.recipient_cert_id:
        raise RiskValidationError("receipt decision maker is not the verified recipient")
    return receipt, baseline, history

def _validated_graph(baseline: ProjectBaseline) -> tuple[dict[str, object], dict[str, set[str]]]:
    tasks: dict[str, object] = {}
    for package in baseline.work_packages:
        for task in package.tasks:
            if not isinstance(task.task_id, str) or not task.task_id.strip():
                raise RiskValidationError("task_id must be a non-empty string")
            if task.task_id in tasks:
                raise RiskValidationError(f"duplicate task ID {task.task_id!r}")
            tasks[task.task_id] = task
    if not tasks:
        raise RiskValidationError("baseline must contain at least one task")
    successors = {task_id: set() for task_id in tasks}
    for edge in baseline.dependencies:
        if edge.predecessor_task_id not in tasks or edge.successor_task_id not in tasks:
            raise RiskValidationError("dependency references an unknown task")
        successors[edge.predecessor_task_id].add(edge.successor_task_id)
    return tasks, successors

def _descendants(roots: Iterable[str], successors: dict[str, set[str]]) -> tuple[str, ...]:
    pending = list(sorted(roots))
    seen: set[str] = set()
    while pending:
        current = pending.pop(0)
        for successor in sorted(successors[current]):
            if successor not in seen:
                seen.add(successor)
                pending.append(successor)
    return tuple(sorted(seen))

def _risk(
    package_id: str, kind: RiskKind, source: SourceKind, basis: str,
    affected: tuple[str, ...], recommendation: str, now: dt.datetime,
    due_days: int, severity: int, rationale: str,
) -> Risk:
    return Risk(
        risk_id=f"risk.{kind.value}.{package_id}",
        kind=kind, source=source, basis=basis,
        affected_tasks=tuple(sorted(set(affected))),
        recommendation=recommendation,
        suggested_deadline=_plus_days(now, due_days),
        severity=severity, rationale=rationale,
    )

def _plus_days(value: dt.datetime, days: int) -> str:
    return (value + dt.timedelta(days=days)).isoformat().replace("+00:00", "Z")
