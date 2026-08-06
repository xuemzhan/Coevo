# `benchmarks/` — 可扩展性探针

## 定位

离线性能基准：把参考架构 SLA 与可扩展性探针清单代码化，由 `scripts/benchmark.py`
驱动实测。计时类探针**不进入 `make quality`**（环境相关，不可作门禁），由人工/CI
按需执行并留档。

## 文件清单

| 文件 | 关键类型/函数 | 职责 |
|---|---|---|
| `harness.py` | `BenchmarkResult`、`measure()`、`report()` | 测量框架：计时、上限比较、JSON 结果 |
| `models.py` | `SLA_TARGETS`、`SCALABILITY_PROBES`、`SlaTarget` | SLA 参考表 + 探针清单（le 比较、上限为正） |

## 关键入口

- `measure(name, fn, limit_seconds)` — 计时并与上限比较，返回 `BenchmarkResult`；
- `report(results)` — 输出结构化 JSON；
- `python scripts/benchmark.py --check` — 一键核对全部探针（含 DAG 拓扑排序、
  图查询、人才推荐、注册表查询、watcher 重扫、驾驶舱 HTTP p95 等）。

## 约束

- 全部离线、无网络；探针为确定性可复现测量；
- 计时类结果不写审计链、不参与质量门禁。

## 测试覆盖

- `tests/unit/test_benchmark_suite.py`（探针清单/上限合法性）；
- `tests/unit/test_benchmark_http.py`（驾驶舱 HTTP 探针：零错误 + 延迟边界绑定）。

## 依赖与下游

- **上游依赖**：`cockpit`（HTTP 探针）、`task_decomposition`、`talent`、
  `progress_capture` 等被测模块；
- **下游消费者**：`scripts/benchmark.py`、运维手动性能核对。
