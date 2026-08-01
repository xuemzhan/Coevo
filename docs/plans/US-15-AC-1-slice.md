# US-15-AC-1 Slice Plan: security audit facade

> Loop-engineer PLAN 阶段产物, 2026-07-31.
> 对应 BACKLOG items[US-15-AC-1].test_audit_governance.
> 本切片遵守 AGENTS.md §1 文档优先级与 §2 七阶段; 不修改 .agent wire, 不修改
> 密码方案, 不修改既有模块 (除测试侧把审计查询投影消费进去)。

## 1. 用户故事与 AC

US-15: "异常包拦截和全过程留痕"
1. 损坏、篡改、过期、重复或接收人不匹配的任务包被拦截;
2. 验签失败时不得初始化工作区或更新项目状态;
3. 导入、解密、验签、合并、调度和人工审批均记录日志;
4. 审计日志采用摘要链、签名或其他防篡改机制;
5. 日志包含时间、主体、项目、任务、动作、结果和异常信息;
6. 安全管理员能够查询和导出审计日志;
7. 异常任务包不得导致客户端崩溃;
8. 包内脚本、可执行文件和未授权文件类型不得自动运行。

## 2. 现状盘点 (实测)

- AC-1 部分覆盖 (US-5 SM2/SM4 + replay detector; 缺统一拦截决策 facade)
- AC-2 已覆盖 (US-5 atomic import + US-6 init fail-closed)
- AC-3 已覆盖 (US-0/5/9/10/12/13 to_audit_record)
- AC-4 已覆盖 (US-0 audit_anchor + 完整签名链)
- AC-5 部分覆盖 (audit_log schema 有 ts/actor/tool/result; 缺 project/task 统一注入 + 查询)
- AC-6 完全未覆盖 ← 本切片核心新增
- AC-7 已覆盖 (US-5/6 fail-closed)
- AC-8 已覆盖 (协议层禁止 + AGENTS.md §3 第 4 条)

## 3. 切片范围

### 3.1 新增模块

- `src/coevo/audit_governance/__init__.py` (≤ 1200 行; 与 US-11/12/13/8 单文件巨型模块风格一致)
- `tests/unit/test_audit_governance.py` (≥ 12 测试)

### 3.2 不修改

- 既有 `src/coevo/{identity,protocol,workspace,report,merge,risk,supervision,decision_brief,progress_capture,task_flow,task_decomposition,talent}` 等任何模块
- `.agent` wire / `loop/audit-signing.json` / `loop/audit-head.{json,p7s}`
- `scripts/audit_log.py` / `scripts/audit_seal.py` (IO 层, 由质量门禁调用, 不在 US-15 切片)
- `toolchain-lock.json` (无新增依赖)

### 3.3 边界

- 不引入 IO; AuditQueryService 只消费 in-memory `tuple[AuditEvent, ...]` (业务侧已 to_audit_record 投影过的 dict)
- 不修改既有 to_audit_record 输出 schema; 只读不写
- 安全等级 security_review=true; US-15 涉及审计治理, 触发 security-reviewer 但**本切片不实际修改**密码/权限/审计配置

## 4. 数据模型

```text
AuditEventSource (Enum, closed set, fail-closed)
  IMPORT          -- 导入任务包 (US-6)
  DECRYPT         -- 解密 (US-5-AC-3)
  VERIFY          -- 验签 (US-5-AC-3)
  MERGE           -- 状态合并 (US-10)
  SCHEDULE        -- 调度 (US-4)
  APPROVAL        -- 人工审批 (US-7/US-13)
  IDENTITY        -- 身份认证 (US-0)
  REPLAY          -- 重放检测 (US-5)
  EXCEPTION       -- 异常包 (US-15)
  STATE           -- 状态变更 (US-8/US-9/US-12)

AuditEvent (在 to_audit_record 投影 dict 基础上规整)
  ts              -- ISO-8601 UTC 'Z'
  actor           -- str (执行者 user/client/cert_id)
  source          -- AuditEventSource
  action          -- str (动词: import/decrypt/verify/merge/schedule/approve/identify/...)
  project_id      -- safe-id (空字符串允许, 但 query 时按空处理)
  task_id         -- safe-id (空字符串允许)
  result          -- "ok" | "rejected" | "failed" | "blocked"
  detail          -- dict (free-form, 不进 audit projection 时用)
  tool            -- str (执行工具, 例如 "PackageImportService" / "MergeEngine")
  fingerprint     -- str (32 字符 hex, 关联 quality_gate fingerprint; 可选)

AuditEventValidationError  -- AuditEvent 字段错
AuditQueryValidationError  -- AuditQuery 字段错

AuditQuery (纯数据, 查询条件)
  actor            -- Optional[str] (None = 不过滤)
  source           -- Optional[AuditEventSource]
  action           -- Optional[str]
  project_id       -- Optional[str]
  task_id          -- Optional[str]
  result           -- Optional[AuditEventResult] (枚举 ok/rejected/failed/blocked)
  ts_from          -- Optional[str] (ISO-8601 UTC 'Z'; None = 最早)
  ts_to            -- Optional[str] (ISO-8601 UTC 'Z'; None = 最新)
  limit            -- int > 0, 默认 100, hard cap 10000 (DoS 防护)
  cursor           -- Optional[str] (record_hash, 翻页)

AuditQueryResult (纯数据)
  events           -- tuple[AuditEvent, ...]
  total_scanned    -- int
  cursor_next      -- Optional[str] (record_hash)

InterceptionReason (Enum, closed set)
  CORRUPTED        -- 损坏
  TAMPERED         -- 篡改
  EXPIRED          -- 过期
  DUPLICATE        -- 重复
  RECIPIENT_MISMATCH  -- 接收人不匹配
  SIGNATURE_INVALID   -- 验签失败
  REPLAY             -- 重放

InterceptionDecision (纯数据)
  package_id        -- safe-id
  intercepted       -- bool
  reasons           -- tuple[InterceptionReason, ...]
  detail            -- str (人类可读说明, 审计可投影)
  decided_at        -- ISO-8601 UTC 'Z'

AuditExportFormat (Enum)
  JSON             -- 单个 JSON 数组
  JSONL            -- 逐行 JSON (与 tool-audit.jsonl 同形)

AuditExportPayload (纯数据, bytes 持有者)
  format            -- AuditExportFormat
  content           -- bytes
  byte_count        -- int
  event_count       -- int
  exported_at       -- ISO-8601 UTC 'Z'
  digest_hex        -- 64-char lowercase hex (内容摘要, 用于 cross-system 比对)
```

## 5. 服务层

```text
AuditEvent.from_audit_record(record: dict, *, source: AuditEventSource) -> AuditEvent:
    """从业务侧 to_audit_record 投影规整为 AuditEvent.

    Fail-closed: record 不是 dict / 缺必填字段 (ts/actor/action/result) /
    ts 不是 ISO-8601 UTC 'Z' / actor 不是 safe-id → AuditEventValidationError.
    """

SecurityAuditFacade:
    @staticmethod
    def evaluate_interception(
        *, package_id: str,
        envelope_status: str,    # "ok" | "corrupted" | "tampered"
        signature_status: str,   # "ok" | "invalid"
        expiration_ts: str,      # ISO-8601 UTC 'Z'; "" = never expires
        now: str,                # ISO-8601 UTC 'Z'
        replay_status: str,      # "ok" | "duplicate"
        envelope_recipient_cert_id: str,   # 包头声明的接收人
        expected_recipient_cert_id: str,  # 接收端期望的接收人
    ) -> InterceptionDecision:
        """AC-1 统一拦截决策.

        集中表达 5 种拦截理由:
        - CORRUPTED (envelope_status == 'corrupted')
        - TAMPERED (signature_status == 'invalid' AND envelope_status != 'corrupted')
        - EXPIRED (expiration_ts != '' AND now > expiration_ts)
        - DUPLICATE (replay_status == 'duplicate')
        - RECIPIENT_MISMATCH (envelope_recipient != expected_recipient)

        决策规则:
        - 任意 1 个理由成立 -> intercepted=True, reasons 列出全部成立理由
        - 全部理由不成立 -> intercepted=False, reasons=()
        - 5 个理由互斥可同时存在; detail 包含 reason 的人类可读串接

        边界: 任一 cert_id 不是 safe-id / package_id 不是 safe-id / now 不是
        ISO-8601 UTC 'Z' → AuditEventValidationError.
        """

    @staticmethod
    def query_events(
        events: tuple[AuditEvent, ...],
        query: AuditQuery,
    ) -> AuditQueryResult:
        """AC-6 查询. 纯函数, 不读文件, 只消费 events 列表."""

    @staticmethod
    def export_events(
        events: tuple[AuditEvent, ...],
        *,
        format: AuditExportFormat = AuditExportFormat.JSONL,
        now: str,
    ) -> AuditExportPayload:
        """AC-6 导出. 纯函数, 返回 bytes (JSONL or JSON array).

        digest_hex = SHA-256(content), 64-char lowercase hex.
        event_count = len(events); byte_count = len(content)."""

SecurityAuditFacade.to_audit_record(decision: InterceptionDecision) -> dict:
    """审计投影, 与 US-11/12/13 to_audit_record 同风格.
    排除 detail 文本 (仅保留 hash), 保留 reason 列表 + intercepted 标志.
    """
```

## 6. AC 映射

| AC | 实现位置 | 失败模式 |
|---|---|---|
| AC-1 异常包拦截 | `evaluate_interception` 5 种 reason 枚举 + 统一决策 | 任一输入非法 → ValidationError |
| AC-2 验签失败不初始化 (既有) | 不在本切片 (US-5/6 已覆盖) | -- |
| AC-3 全过程留痕 (既有) | 不在本切片 (US-0/5/9/10/12/13 to_audit_record 已覆盖); 本切片只增加 AuditEvent 统一规整 | AuditEvent.from_audit_record 失败时 ValidationError |
| AC-4 摘要链防篡改 (既有) | 不在本切片 (US-0 audit_anchor + 签名链已覆盖) | -- |
| AC-5 字段齐全 | AuditEvent 强制 ts/actor/action/result/project_id/task_id 字段 | 字段缺失 → ValidationError |
| AC-6 查询和导出 | query_events + export_events + AuditQuery / AuditExportPayload | query.events 不是 tuple / limit ≤ 0 / ts_from 越界 → ValidationError |
| AC-7 异常包不崩溃 (既有) | 不在本切片 (US-5/6 fail-closed) | -- |
| AC-8 脚本/可执行文件不自动运行 (既有) | 不在本切片 (协议层禁止) | -- |

## 7. 测试点 (≥ 12)

1. test_audit_event_from_valid_record_succeeds (AC-5)
2. test_audit_event_from_missing_field_is_rejected (AC-5 fail-closed)
3. test_audit_event_from_bad_timestamp_is_rejected (AC-5)
4. test_interception_corrupted_envelope_intercepts (AC-1)
5. test_interception_tampered_signature_intercepts (AC-1)
6. test_interception_expired_package_intercepts (AC-1)
7. test_interception_duplicate_replay_intercepts (AC-1)
8. test_interception_recipient_mismatch_intercepts (AC-1)
9. test_interception_clean_package_passes (AC-1)
10. test_interception_multiple_reasons_are_listed (AC-1)
11. test_query_filters_by_actor_and_project_id (AC-6)
12. test_query_limit_and_cursor_paginate (AC-6)
13. test_export_jsonl_round_trip (AC-6)
14. test_export_json_array_round_trip (AC-6)
15. test_export_digest_is_content_stable (AC-6)
16. test_to_audit_record_excludes_sensitive_detail (US-11/12/13 一致性)

## 8. 风险与缓解

- R1 (AC-1 集中决策可能漏掉业务侧独有 reason): 本切片只覆盖 5 种通用 reason; 业务侧专属 reason 仍可在 US-5/6/10 to_audit_record 的 detail 字段里表达, evaluate_interception 只负责"是否拦截 + 通用 reason"
- R2 (AuditQuery limit DoS): hard cap 10000 强制; query 参数 limit 越界 → ValidationError
- R3 (export 时间戳漂移): exported_at 由调用方注入 now, 服务不取 wall clock → 与 progress_capture / merge / decision_brief 注入式时间戳策略一致

## 9. 完成定义 (本切片)

- 所有 ≥ 16 项 unit 测试通过
- `scripts/dev.ps1 -Task quality` exit=0, audit chain fully-sealed
- 不修改既有模块 / 既有 wire / 既有密码 / 既有审计配置
- BACKLOG US-15-AC-1 status: ready → done
- STATE bump iteration + status done
- DECISIONS append 一段 finalize 段 (append-only)
- 追踪矩阵 US-15 行追加

## 10. 后续 AC 候选 (本切片不做)

- US-15-AC-2: 实时审计流 (push 通知 / 订阅)
- US-15-AC-3: 跨项目审计聚合 (US-13 决策简报依赖)
- US-15-AC-4: 审计策略声明 (按 actor / action 配置审计级别)
