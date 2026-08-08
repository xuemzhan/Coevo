# 根级模块

`src/coevo/` 根目录下的独立模块，供全仓共享：

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `config.py` | `AppConfig`、`ConfigError`、`from_env()` | 生产运行配置：环境变量驱动、失败关闭（环回强制、端口/级别/路径校验） |
| `version.py` | `VERSION`、`APP_NAME`、`APP_DISPLAY_NAME` | 版本元数据（语义化版本，禁用时间戳；当前 0.2.0） |
| `timefmt.py` | `is_iso_utc_z` / `now_utc_iso_z` | 共享 ISO-8601 UTC 时间戳校验与生成（`\Z` 锚定、小数秒、日历校验、非字符串 fail-closed；依赖无关叶模块，框架层与产品模块统一引用） |
| `canon.py` | `canonical_json_bytes` / `canonical_digest` | 共享 canonical JSON 序列化与 SHA-256 摘要（sort_keys、紧凑分隔符、可选 ASCII 转义；依赖无关叶模块，框架层与产品审计哈希链统一引用，禁止内联副本） |
| `logging_setup.py` | `setup_logging()` | 日志引导（stdlib logging，轮转 5MB×5，绝不吞审计链） |
| `records_archive.py` | `archive_plan()` | 记录归档策略助手（纯函数：VERIFICATION/DECISIONS/tool-audit 分节、按容量+期限裁剪） |

## 关键入口

- `AppConfig.from_env()` — 非法值一律抛 `ConfigError`，绝不静默回退；
- `archive_plan(text, kind, now, keep_recent, min_age_days, size_threshold_bytes)`
  — 供 `scripts/archive_records.py` 驱动归档（含 size-trim 语义）；
- `setup_logging()` — 应用日志与安全审计（`loop/tool-audit.jsonl`）严格分离。

## 约束

- 全部 stdlib-only，零第三方运行时依赖；
- 版本号不使用时间戳；归档策略变更须在 `loop/DECISIONS.md` 留痕。

## 测试覆盖

- `tests/unit/test_records_archive.py`（分节/裁剪/策略常量）；
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
