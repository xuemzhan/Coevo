# 根级模块

`src/coevo/` 根目录下的独立模块，供全仓共享：

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `config.py` | `AppConfig`、`ConfigError`、`from_env()` | 生产运行配置：环境变量驱动、失败关闭（环回强制、端口/级别/路径校验） |
| `version.py` | `VERSION`、`APP_NAME`、`APP_DISPLAY_NAME` | 版本元数据（语义化版本，禁用时间戳；当前 0.2.0） |
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
