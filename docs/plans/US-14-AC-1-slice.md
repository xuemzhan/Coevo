# US-14-AC-1 Slice Plan: knowledge base facade

> Loop-engineer PLAN 阶段产物, 2026-08-01.
> 对应 BACKLOG items[US-14-AC-1].test_knowledge_base.
> 本切片遵守 AGENTS.md §1 文档优先级与 §2 七阶段; 不修改 .agent wire, 不修改
> 密码方案, 不修改既有模块.

## 1. 用户故事与 AC

US-14: "成果沉淀 - 项目知识包和复盘材料生成"
1. 汇总任务流程、任务结构、风险、会议决策和成果;
2. 自动生成复盘报告草稿;
3. 提取可复用流程模板、任务模板和风险规则;
4. 所有知识条目记录来源项目和适用范围;
5. 入库前进行密级和权限检查;
6. 用户可选择批准入库、修改后入库或不入库;
7. 未经审核的模型总结不得进入正式知识库.

## 2. 切片范围

### 2.1 新增模块

- `src/coevo/knowledge_base/__init__.py` (≤ 1200 行, 与 US-11/12/13/8/15/4 单文件风格一致)
- `tests/unit/test_knowledge_base.py` (≥ 12 测试)

### 2.2 不修改

- 既有 `src/coevo/{identity,protocol,workspace,report,merge,risk,supervision,decision_brief,progress_capture,audit_governance,orchestrator,cockpit,task_flow,task_decomposition,talent}` 等任何模块
- `.agent` wire / `loop/audit-signing.json` / `loop/audit-head.{json,p7s}`
- `toolchain-lock.json` (无新增依赖)

### 2.3 边界

- 不引入 IO; KnowledgeBaseFacade 只消费 in-memory 输入 (US-2 baseline + US-10 merge + US-11 risk + US-12 conclusion + US-13 brief + US-8 progress)
- 不调用既有 facade 的副作用 API; 只演示"如果汇总会得到什么"
- 安全等级 security_review=true; 涉及密级检查 + 入库审核 (AC-5/AC-6/AC-7) 都是 security-relevant 边界

## 3. 数据模型

```text
KnowledgeClassification (Enum, closed set; AC-5 密级)
  PUBLIC            -- 公开
  INTERNAL          -- 内部
  CONFIDENTIAL      -- 机密
  RESTRICTED        -- 核心机密

KnowledgeSourceKind (Enum)
  PROJECT_BASELINE  -- US-2 baseline
  MERGE_RECORD      -- US-10 merge
  RISK_REPORT       -- US-11 risk
  MEETING_CONCLUSION -- US-12 supervision
  DECISION_BRIEF    -- US-13 brief
  PROGRESS_CAPTURE  -- US-8 progress
  MODEL_SUMMARY     -- 模型自动总结 (AC-7 禁止直接入库)

ReusableTemplateKind (Enum; AC-3)
  PROCESS_TEMPLATE   -- 流程模板
  TASK_TEMPLATE      -- 任务模板
  RISK_RULE          -- 风险规则

ReusableTemplate (不可变)
  template_id       -- safe-id
  kind              -- ReusableTemplateKind
  source_project_id -- safe-id
  scope             -- str ("all_projects" / "similar_domains" / "this_project_only")
  body              -- dict (kind-specific structure)
  extracted_at      -- ISO-8601 UTC 'Z'

KnowledgeEntry (不可变; AC-1/AC-4 汇总 + 来源)
  entry_id          -- safe-id
  kind              -- KnowledgeSourceKind
  source_ref        -- str (e.g. project_id / merge_record_id)
  title             -- str
  body_summary      -- str (人类可读; 不进 audit)
  classification    -- KnowledgeClassification
  scope             -- str ("all_projects" / "similar_domains" / "this_project_only")
  requires_owner_approval -- bool (AC-6; MODEL_SUMMARY 默认 True)
  recorded_at       -- ISO-8601 UTC 'Z'

ReviewDecisionKind (Enum; AC-6)
  APPROVE           -- 批准入库
  REVISE            -- 修改后入库
  REJECT            -- 不入库

ReviewDecision (不可变)
  decision_id       -- safe-id
  entry_id          -- safe-id
  decision          -- ReviewDecisionKind
  decided_by        -- safe-id (reviewer user)
  reason            -- str
  decided_at        -- ISO-8601 UTC 'Z'

RetrospectiveDraft (不可变; AC-2 复盘草稿)
  draft_id          -- safe-id
  project_id        -- safe-id
  title             -- str
  body_sections     -- tuple[str, ...] (复盘章节: 总体进展/重要变化/高风险/待决策/最佳实践)
  sources           -- tuple[str, ...] (entry_id 引用)
  generated_at      -- ISO-8601 UTC 'Z'
  requires_user_review -- bool (恒 True, AC-7)

KnowledgeBundle (不可变; 最终产出)
  bundle_id         -- safe-id
  project_id        -- safe-id
  entries           -- tuple[KnowledgeEntry, ...]
  retrospective     -- RetrospectiveDraft
  reusable_templates -- tuple[ReusableTemplate, ...]
  accepted_entries  -- tuple[str, ...] (entry_id 列表; AC-6 批准后才填)
  rejected_entries  -- tuple[str, ...] (entry_id 列表)
  bundle_classification -- KnowledgeClassification (max of all entries)
  requires_user_confirmation -- bool (恒 True, AC-7)
  formally_committed -- bool (默认 False)
  committed_at      -- "" 默认
  committed_by      -- "" 默认
  created_at        -- ISO-8601 UTC 'Z'
```

## 4. 服务层

```text
class KnowledgeBaseFacade:
    @staticmethod
    def aggregate(
        *,
        project_id: str,
        baseline: dict | None = None,
        merge_records: tuple[dict, ...] = (),
        risk_reports: tuple[dict, ...] = (),
        meeting_conclusions: tuple[dict, ...] = (),
        decision_briefs: tuple[dict, ...] = (),
        progress_captures: tuple[dict, ...] = (),
        model_summaries: tuple[dict, ...] = (),  # AC-7 禁止直接入库
        now: str,
    ) -> KnowledgeBundle:
        """AC-1/AC-2/AC-3/AC-4/AC-7 汇总 + 复盘 + 模板提取.

        - 每个输入按 source_kind 转 KnowledgeEntry;
        - baseline/merge/risk/conclusion/brief/progress: requires_owner_approval=False;
        - model_summaries: requires_owner_approval=True (AC-7);
        - retrospectively 自动生成 5 段 (AC-2): 总体进展/重要变化/高风险/待决策/最佳实践;
        - reusable templates: 自动从 baseline 提取 process_template + task_template,
          从 risk_reports 提取 risk_rule (AC-3).
        - requires_user_confirmation=True; formally_committed=False 默认 (AC-7).
        """

    @staticmethod
    def review(
        bundle: KnowledgeBundle,
        *,
        decisions: tuple[ReviewDecision, ...],
        now: str,
    ) -> KnowledgeBundle:
        """AC-6: apply reviewer decisions.

        - APPROVE -> entry 进入 accepted_entries;
        - REVISE -> entry 仍 accepted 但带 reason (人工修改后入库);
        - REJECT -> entry 进入 rejected_entries.

        只接受 requires_owner_approval=True 的 entry 的 REVISE/REJECT;
        requires_owner_approval=False 的 entry 默认 APPROVE.

        formally_committed=True iff all REVIEWED entries accepted and
        所有 requires_owner_approval=True 的 entries 都有 decision.
        """

    @staticmethod
    def check_classification(
        bundle: KnowledgeBundle,
        *,
        actor_clearances: frozenset[KnowledgeClassification],
        now: str,
    ) -> KnowledgeBundle:
        """AC-5: 密级检查. bundle.bundle_classification 必须 <= actor_clearances.
        否则 raise ClassificationDenied; bundle 不变 (返回新实例仍
        requires_user_confirmation=True, formally_committed=False).
        """

KnowledgeBaseFacade.to_audit_record(bundle: KnowledgeBundle) -> dict:
    """审计投影: 排除 body_summary / body_sections / template body (敏感);
    保留 entry_id / source_kind / classification / scope / requires_owner_approval
    计数 + accepted/rejected 计数.
    """
```

## 5. AC 映射

| AC | 实现位置 | 失败模式 |
|---|---|---|
| AC-1 汇总 | aggregate 按 6 种 source_kind 入 KnowledgeEntry | 缺 now / project_id 不安全 |
| AC-2 复盘草稿 | aggregate 自动生成 5 段 | -- |
| AC-3 模板提取 | aggregate 从 baseline/risk 自动抽 reusable_templates | baseline/risk 为空 -> 空元组 |
| AC-4 来源标记 | 每个 KnowledgeEntry.source_ref + scope | -- |
| AC-5 密级检查 | check_classification (actor_clearances 必须包含 bundle.bundle_classification) | 不足 -> ClassificationDenied |
| AC-6 用户审核 | review 接受 APPROVE/REVISE/REJECT | 缺 decisions 或 now 非法 -> ValidationError |
| AC-7 未经审核不得入库 | requires_user_confirmation=True; formally_committed=False; model_summaries 默认 requires_owner_approval=True | 直接构造 formally_committed=True -> ValidationError |

## 6. 测试点 (≥ 12)

1. test_knowledge_classification_closed_set (AC-5)
2. test_knowledge_source_kind_includes_model_summary (AC-7)
3. test_aggregate_with_baseline_only (AC-1)
4. test_aggregate_with_all_six_kinds (AC-1)
5. test_aggregate_generates_retrospective_draft_with_five_sections (AC-2)
6. test_aggregate_extracts_process_template_from_baseline (AC-3)
7. test_aggregate_extracts_risk_rule_from_risk_reports (AC-3)
8. test_aggregate_marks_model_summary_requires_owner_approval (AC-7)
9. test_review_approve_moves_entry_to_accepted (AC-6)
10. test_review_reject_moves_entry_to_rejected (AC-6)
11. test_review_formally_committed_requires_all_model_summaries_decided (AC-6/AC-7)
12. test_check_classification_denies_insufficient_clearance (AC-5)
13. test_construct_bundle_with_formally_committed_true_without_approval_rejected (AC-7)
14. test_to_audit_record_excludes_sensitive_bodies (audit projection)
15. test_pure_function_determinism (质量)

## 7. 风险与缓解

- R1 (AC-7 防止模型总结直接入库): KnowledgeBundle.requires_user_confirmation=True 强制 + formally_committed 默认 False + review() 必须所有 requires_owner_approval=True entries 都有 decision 才设 formally_committed=True. 三层防御。
- R2 (AC-5 密级检查可被绕过): check_classification 是 facade 方法, 必须显式调用; 默认 bundle 不带 actor_clearances; raise ClassificationDenied 而非 silent skip (fail-closed)。
- R3 (AC-3 模板提取启发式): 当前切片用最简单启发式 (baseline 节点 -> process_template, baseline 工作包 -> task_template, risk_reports -> risk_rule), 后续 AC 可升级为 LLM-assisted 但本切片纯函数。

## 8. 完成定义 (本切片)

- 所有 ≥ 15 项 unit 测试通过
- `python scripts/quality_gate.py --target quality` exit=0, audit chain fully-sealed
- 不修改既有模块 / 既有 wire / 既有密码 / 既有审计配置
- BACKLOG US-14-AC-1 status: ready → done
- STATE bump iteration + status done
- DECISIONS append 一段 finalize 段 (append-only)
- 追踪矩阵 US-14 行追加

## 9. 后续 AC 候选 (本切片不做)

- US-14-AC-2: 持久化入库 (KnowledgeStore 写 disk / DB)
- US-14-AC-3: 跨项目模板搜索 (similar_projects_by_scope)
- US-14-AC-4: LLM-assisted 模板提取 (model summary → reusable templates)
- US-14-AC-5: 入库审计追踪 (每个 bundle 对应一条 audit chain record)
