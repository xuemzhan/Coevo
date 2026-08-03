# 生产可用性说明（PROD-HARDEN-1）

## 运行模型

本地客户端以“一个环回 HTTP 驾驶舱 + 离线工作区 + 审计链”的方式运行，全部依赖为
Python 标准库（零第三方运行时依赖），不产生任何公网请求。

## 配置（环境变量驱动、失败关闭）

所有运行参数集中由 `src/coevo/config.py::AppConfig.from_env()` 读取，非法值一律
抛 `ConfigError` 而非静默回退：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `COEVO_COCKPIT_HOST` | `127.0.0.1` | 仅允许环回地址（强制约束 § 5.1） |
| `COEVO_COCKPIT_PORT` | `12701` | 1..65535 |
| `COEVO_DATA_DIR` | `%LOCALAPPDATA%\KaiwuAgent` | 状态与数据根目录 |
| `COEVO_LOG_DIR` | `%LOCALAPPDATA%\KaiwuAgent` | 应用日志根目录 |
| `COEVO_SESSION_TIMEOUT_SEC` | `28800` | 驾驶舱会话不活动超时 |
| `COEVO_COCKPIT_CHECKPOINT_SEC` | `300` | 驾驶舱状态周期快照间隔（秒），崩溃不丢视图状态；停机仍做最终落盘 |
| `COEVO_LOG_LEVEL` | `INFO` | CRITICAL/ERROR/WARNING/INFO/DEBUG |
| `COEVO_STATE_PATH` / `COEVO_LOG_PATH` | 由 data/log 目录派生 | 显式覆盖文件路径 |

## 启动与停机

```powershell
python scripts/run_cockpit.py --check     # 只校验配置
python scripts/run_cockpit.py --port 12710
```

`SIGINT`（Ctrl+C）、`SIGTERM` 与 Windows `CTRL+BREAK` 均触发优雅停机：停止接收新连接、
落盘驾驶舱状态快照、关闭访问日志与单实例锁后以退出码 0 结束。单实例锁残留超过 10 分钟
自动接管，进程被硬杀后的残留锁不会阻塞后续启动超过该窗口。运行期间视图状态按
`COEVO_COCKPIT_CHECKPOINT_SEC` 周期落盘，硬杀/断电最多丢失一个周期内的视图变化；
本地 HTTP 服务并发处理有界（默认 16，饱和返回 503），避免无界线程消耗。

## 日志边界

* **应用运行日志**：`coevo-app.log`（轮转 5MB×5），记录启动/停机/错误；
* **驾驶舱访问日志**：`cockpit-access.jsonl`（每请求一条）；
* **安全审计**：`loop/tool-audit.jsonl` + 签名检查点（`audit_seal`），绝不经过标准
  logging 重定向，保持防篡改链独立。

## 版本

`src/coevo/version.py` 提供语义化版本（当前 `0.2.0`，0.1.0→0.2.0 为生产可用化里程碑），`run_cockpit.py --version` /
`run_demo.py --version` 输出；版本号不使用时间戳（强制约束 § 13.1）。

## 性能基线

`python scripts/benchmark.py --check` 对照参考架构 SLA 与可扩展性探针
（见 `src/coevo/benchmarks/__init__.py`）。计时类探针不进 `make quality`，
由人工/CI 按需执行并留档。

## 与正式安全基线的关系

本说明描述的“生产可用”指离线 MVP 的可运维性（配置/日志/停机/版本/性能可复测）。
正式部署仍必须满足：批准的 SM2/SM4 密码产品与受保护密钥句柄、独立审计节点、
组织证书链、受控升级与回滚（见 `docs/dependencies/approved-crypto-provider-path.md`）。
