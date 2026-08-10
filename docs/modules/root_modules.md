# 根级模块

`src/coevo/` 根目录下的独立模块，供全仓共享：

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `config.py` | `AppConfig`、`ConfigError`、`from_env()` | 生产运行配置：环境变量驱动、失败关闭（环回强制、端口/级别/路径校验） |
| `version.py` | `VERSION`、`APP_NAME`、`APP_DISPLAY_NAME` | 版本元数据（语义化版本，禁用时间戳；当前 0.2.0） |
| `timefmt.py` | `is_iso_utc_z` / `now_utc_iso_z` / `parse_iso_utc` | 共享 ISO-8601 UTC 时间戳校验、生成与解析（`\Z` 锚定、小数秒、日历校验、非字符串 fail-closed；parse_iso_utc 以 error_factory + 消息参数保留各模块异常语义；依赖无关叶模块，框架层与产品模块统一引用，decision_brief/merge/risk/supervision 的 _parse_utc 统一收敛） |
| `canon.py` | `canonical_json_bytes` / `canonical_digest` | 共享 canonical JSON 序列化与 SHA-256 摘要（sort_keys、紧凑分隔符、可选 ASCII 转义、allow_nan 默认 False 拒绝 NaN/Infinity；依赖无关叶模块，框架层与产品审计哈希链统一引用，禁止内联副本） |
| `ids.py` | `SAFE_ID` / `is_safe_id` / `HEX_64` / `is_hex_64` | 共享 safe-id 与 64-hex 正则/校验（safe-id `[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,63}`、hex `[0-9a-f]{64}`，非字符串/空/超长 fail-closed；依赖无关叶模块，产品与 framework 统一引用；task_flow/talent 语义差异保留独立） |
| `jsonutil.py` | `reject_duplicate_pairs` | 共享 JSON 重复键拒绝守卫（object_pairs_hook，error_factory 可注入保持各模块异常语义，重复键 fail-closed；依赖无关叶模块，协议/清单/存储/清单解析统一引用） |
| `relpath.py` | `is_safe_relative_path` | 共享安全相对路径谓词（非空、无前导 `/`、无 `\`、无 NUL、无空/`.`/`..` 段，fail-closed；依赖无关叶模块，progress_capture.watcher / cockpit.static / cockpit.wps 统一引用；workspace._has_parent_traversal 与 model.config prompts_file 语义差异保留独立） |
| `powershell.py` | `powershell_executable` / `locked_powershell_executable` | 共享 Windows PowerShell 可执行文件解析（简单变体 + 锁哈希校验变体，error_factory 保留各模块异常语义，fail-closed；依赖无关叶模块，identity/certificates、identity/audit_anchor、identity/private_keys、crypto/cng_handle 统一引用） |
| `validate.py` | `non_empty_string` | 共享模型输入校验助手（非空字符串，error_factory 保留各模块异常类与消息，fail-closed；依赖无关叶模块，risk/supervision 的 _non_empty 统一引用） |
| `decision_brief/_util.py` | `_safe_string` / `_digest` / `_encode_json` / `_stat_is_reparse` / `_is_link_or_reparse` / `_parse_utc` / `_ZERO_DIGEST` | decision_brief/models 纯工具助手（error_factory 保留异常类与消息；无域导入依赖；models.py 薄包装再导出，导入面不变） |
| `logging_setup.py` | `setup_logging()` | 日志引导（stdlib logging，轮转 5MB×5，绝不吞审计链） |
| `records_archive.py` | `archive_plan()` / `over_policy_size()` / `POLICY` | 记录归档策略唯一事实源（纯函数：VERIFICATION/DECISIONS/tool-audit 分节、按容量+期限裁剪、容量判定与策略常量） |
| `events/` | `DomainEvent` / `validate_event_chain` / `event_order_key` | 显式领域事件模型（REVIEW2-8）：聚合内按 client_sequence 严格递增排序，created_at 仅元数据不参与排序，causation_id 只允许指向前序事件（无自指/环），fail-closed |

## 关键入口

- `AppConfig.from_env()` — 非法值一律抛 `ConfigError`，绝不静默回退；
- `archive_plan(text, kind, now, keep_recent, min_age_days, size_threshold_bytes)`
  — 供 `scripts/archive_records.py` 驱动归档（含 size-trim 语义）；
- `over_policy_size(kind, text)` — 容量阈值判定（fail-closed：未知 kind / 非字符串拒绝）；
  `POLICY` — 归档策略常量（keep_recent / min_age_days / size）唯一来源；
- `setup_logging()` — 应用日志与安全审计（`loop/tool-audit.jsonl`）严格分离。

## 约束

- 全部 stdlib-only，零第三方运行时依赖；
- 版本号不使用时间戳；归档策略变更须在 `loop/DECISIONS.md` 留痕。

## 测试覆盖

- `tests/unit/test_records_archive.py`（分节/裁剪/策略常量/`over_policy_size`）；
- `tests/unit/test_production_docs.py`（配置⇄文档一致性）；
- `tests/security/test_loop_state_transaction.py` 等（配置/状态安全）。

## 依赖与下游

- **下游消费者**：全仓（config/version/logging 被所有模块引用）；
  `scripts/archive_records.py` 消费 `records_archive`。

## 配置项（环境变量）

| 变量 | 默认 | 说明 |
|---|---|---|
| `COEVO_COCKPIT_HOST` | `127.0.0.1` | 仅允许环回（强制约束 §5.1） |
| `COEVO_COCKPIT_PORT` | `12701` | 1..65535 |
| `COEVO_DATA_DIR` / `COEVO_LOG_DIR` | `%LOCALAPPDATA%\KaiwuAgent` | 状态与日志根 |
| `COEVO_SESSION_TIMEOUT_SEC` | `28800` | 会话不活动超时 |
| `COEVO_COCKPIT_CHECKPOINT_SEC` | `300` | 状态周期快照间隔 |
| `COEVO_LOG_LEVEL` | `INFO` | CRITICAL..DEBUG |
| `COEVO_STATE_PATH` / `COEVO_LOG_PATH` / `COEVO_LOCK_PATH` | 派生 | 显式覆盖路径 |

非法值一律抛 `ConfigError`，绝不静默回退。
