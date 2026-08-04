# 示例：统一服务框架与一致性 API（service-api）

本示例演示如何用**一个服务框架统筹所有 MVP 模块**，并通过**一致性 API** 对外
开放：16 个领域服务（身份、流程理解、任务分解、人才推荐、运行中枢、任务包、
工作区、驾驶舱、进展采集、成果回传、状态合并、风险预警、督办会议、决策简报、
知识沉淀、安全审计）统一注册、统一信封、统一错误码、统一审计。

## 一致性 API 契约

```text
POST /api/v1/{service}/{method}     服务调用（JSON 请求体 → 统一信封）
GET  /api/v1/services              能力目录（16 个服务及其方法）
GET  /api/v1/openapi.json          OpenAPI 3.0 契约（18 个路径 + Schema）
GET  /api/v1/health                健康检查（含请求数/审计事件数）
GET  /healthz                      探活（免鉴权）
```

请求体：

```json
{
  "params": { "...": "..." },
  "actor": "u.pm",
  "request_id": "svc.1.identity.describe",
  "ts": "2026-08-01T00:00:00Z"
}
```

统一响应信封（成功与失败同一结构，错误永不泄漏内部堆栈）：

```json
{
  "ok": true,
  "service": "identity",
  "method": "describe",
  "request_id": "svc.1.identity.describe",
  "code": "ok",
  "message": "",
  "data": { "...": "..." },
  "ts": "2026-08-01T00:00:00Z"
}
```

闭集错误码：`ok / bad_request / validation_error / unauthorized / not_found /
conflict / internal_error / busy`（对应 HTTP 200/400/400/401/404/409/500/503）。

调用权限治理（fail-closed）：框架可配置 `actor → 允许动作` 策略（动作格式
`service.method`，`*` 表示全部）；未列出的主体一律返回 `unauthorized`
信封并留审计。

## 运行

```powershell
python examples\service-api\run_demo.py
```

演示以统一信封逐个调用 16 个服务，走通：身份 → 流程理解 → 任务分解 →
人才推荐 → 运行中枢编排（下发链，含人工确认）→ 加密任务包 → 工作区初始化 →
进展采集 → 成果回传 → 状态合并（签名回执 + 风险预检）→ 督办会议 → 阶段简报 →
知识沉淀（审批入库）→ 安全审计查询；并演示三条一致性错误路径（未知服务 →
`not_found`；证书指纹复用 → `conflict`；越权调用 → `unauthorized`）。
同时输出 OpenAPI 3.0 契约（`/api/v1/openapi.json`）供调用方/文档工具消费。

完整业务闭环版（只通过一致性 API 客户端完成多角色项目）：

```powershell
python examples\service-api\run_demo_full.py
```

走通：双单位合并流程 → 编排下发 → 研发/测试/文档/评审四角色连续成果回传
与签名合并（R0001 → R0005）→ 风险预警 → 督办会议 → 阶段/风险专题/周期
三类简报 → 督办包（SUPERVISION_NOTICE）→ 知识沉淀（审批入库）→
审计查询/导出/检查点包（AUDIT_CHECKPOINT），全程只调用一致性 API；
`package.build` 可构建任意协议包类型。

Python 客户端（消费方视角）：

```python
from service_api import ServiceClient, ServiceApiError

client = ServiceClient("http://127.0.0.1:<port>/", "<token>")
data = client.call("flow", "understand", {"raw": {...}})   # 直接拿 data
print(client.list_services())                               # 能力目录
```

框架自测（秒级，不依赖加密/生产上下文）：

```powershell
python examples\service-api\run_tests.py
```

覆盖：信封契约、错误码、注册表、统一分派（成功/失败/审计钩子）、权限治理、
OpenAPI 契约、Python 客户端与环回 HTTP 服务鉴权（30 项框架层）。

完整测试（含真实加密端到端冒烟，约 40 秒）：

```powershell
python examples\service-api\run_tests.py            # 全部 32 项
python examples\service-api\run_tests.py --fast     # 只跑框架层 30 项
```

## 代码结构

```text
examples/service-api/
├─ README.md                       本说明
├─ run_demo.py                     一致性 API 演示运行器
└─ service_api/
   ├─ contract.py                  请求/响应信封 + 错误码（公共契约）
   ├─ registry.py                  服务注册表（能力目录）
   ├─ framework.py                 ServiceFramework 统一分派 + 审计 + 权限治理
   ├─ adapters/                    16 个领域模块 → 服务处理方法（按领域分组）
   │  ├─ _core.py                  上下文装配与共享助手
   │  ├─ identity_flow.py          身份/流程理解/分解/人才推荐
   │  ├─ orchestration.py          运行中枢编排（含失败升级演示）
   │  ├─ package_workspace.py      任务包/工作区/驾驶舱/进展/回传
   │  ├─ chain.py                  合并/风险/督办/简报/知识
   │  ├─ audit_services.py         审计查询/拦截/导出/检查点
   │  └─ __init__.py               注册表装配（能力目录）
   ├─ openapi.py                   OpenAPI 3.0 契约生成
   ├─ client.py                    Python 客户端（消费方视角）
   └─ server.py                    环回 HTTP 服务（令牌鉴权 + 统一信封）
```

## 安全基线

* HTTP 仅绑定 `127.0.0.1`，Host 头只接受环回主机名；
* 除 `/healthz` 外全部请求需 `X-Service-Token` 会话令牌；
* 请求体大小上限 64 KiB；错误响应不泄漏堆栈；
* 每次调用产生一条审计事件（复用生产 `AuditEvent` 模型），可经
  `audit.query` 查询；
* 服务端顺序处理请求，共享 SQLite 存储在同一线程内使用，避免跨线程连接问题。

## 与 tool-dev-project 的关系

`tool-dev-project` 是“业务化端到端演示”（直接调用生产门面）；本示例是
“统一入口演示”（经一致性 API 封装同一批生产门面）。两者互补：前者展示
业务闭环，后者展示“服务框架统筹 + 一致性 API 开放”的应用架构。
