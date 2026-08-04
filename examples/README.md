# Coevo 端到端示例（examples）

本目录存放使用 Coevo MVP 已实现能力做的可运行端到端示例。每个示例都是一个
自包含场景：给定一份业务任务输入，按真实项目中的不同角色，用 `src/coevo`
下的生产门面（facade）完整走通“任务下发链”与“成果回传链”，并产出可检查的
中间产物（流程模型、任务基线、加密 `.agent` 任务包、合并回执、风险报告、
决策简报、知识包与审计流）。

## 目录

| 示例 | 场景 | 覆盖故事 |
|---|---|---|
| [tool-dev-project](./tool-dev-project/) | “内部工时统计小工具”跨单位开发任务，负责人/研发/测试/文档/评审/安全管理员多角色协作 | US-0 ~ US-15 全流程 |
| [service-api](./service-api/) | 统一服务框架：16 个领域模块经一致性 API（统一信封/错误码/权限/OpenAPI/客户端/API 浏览器/审计）对外开放，含最小闭环与完整业务闭环两个演示 | 全模块统筹 + API 封装 |

## 运行方式

每个示例提供 `scripts/run_example.py`，从仓库根目录直接运行：

```powershell
python examples\tool-dev-project\scripts\run_example.py
```

运行全程离线、无网络请求；SM2/SM3/SM4 使用仓库锁定的 GmSSL 3.2.0 测试
PKI（`loop/runtime/sm2-test-pki/demo`）。运行产物写入示例的
`output/run-<时间戳>/` 目录（已在 `.gitignore` 中排除）。

每个示例还提供一键演示包装脚本（自动识别仓库虚拟环境）：

```powershell
examples\tool-dev-project\scripts\run-demo.ps1 -Open        # 跑完自动打开演示报告
examples\tool-dev-project\scripts\run-demo.ps1 -Interactive # 逐段暂停讲解
examples\tool-dev-project\scripts\run-demo.ps1 -Serve       # 跑完保持驾驶舱服务
```

演示增强选项（详见各示例 README）：

- `--interactive`：每步暂停、按回车继续，适合现场逐段讲解；
- `--serve`：跑完后保持本地驾驶舱服务运行，浏览器直接查看；
- 产物中的 `demo-report.html`：离线自包含的整场演示图文报告。

每个示例还提供产物独立核验脚本（只读，断言产物存在、包可解析、审计链等）：

```powershell
python examples\tool-dev-project\scripts\verify_output.py
```

一键联合验证整个 examples 体系（tool-dev-project 核验 + service-api 全套
测试，含两个端到端冒烟，约 2 分钟）：

```powershell
python examples\run_all.py
```

两个示例共享的工具（加密包构建/校验、DOCX、编排容错等）收敛在
`examples/shared/coevo_demo_utils.py`，避免重复实现。

CI 接入：`.github/workflows/quality.yml` 在仓库门禁后运行 service-api 快速
测试与 examples 编译检查（推送/PR 时自动执行）。

## 与测试的关系

示例脚本与 `tests/e2e/test_demo_runner.py`、`tests/e2e/test_return_chain.py`
使用同一批生产门面与加密提供方，可视为两条 E2E 链的“业务化演示”变体：

- 任务下发链：`任务输入 → 流程理解 → 任务分解 → 团队推荐 → 负责人确认 → 生成任务包`
- 成果回传链：`成果包导入 → 版本差异审核 → 项目主版本更新 → 风险预警 → 决策简报 → 知识沉淀`

示例脚本会自行断言关键不变量（包可解密回读、合并版本递增、审计链校验通过等），
任一环节失败则以非零退出码结束。
