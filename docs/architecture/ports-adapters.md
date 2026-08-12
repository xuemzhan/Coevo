# 应用/协议/存储分层契约（Ports & Adapters）

> 状态：生效（2026-08-10，ENG-OPTIMIZE-4；落实第二位架构师 P2 分层建议）
> 适用范围：`src/coevo` 全包的分层归属与边界纪律。

## 1. 四层定义

- **Domain Core**：不可变模型、确定性规则、校验与状态机；**不允许 IO**（无网络、
  无文件、无 SQL、无模型调用）；
- **Application**：用例编排、授权与人工确认、组合根（pipeline / 编排）；
- **Ports**：协议接口（Protocol / 注入接口 / 抽象仓储），业务不直接绑定厂商；
- **Adapters**：端口实现——SQLite / 文件系统 / CNG / GmSSL / 受控子进程 /
  HTTP / WPS / 模型厂商。

## 2. 模块 → 层映射

| 包 | 主层 | 注记 |
|---|---|---|
| task_flow / task_decomposition / talent | Domain | 解析/映射/推荐纯模型 |
| merge / risk / supervision / decision_brief | Domain | 合并/风险/督办/简报规则 |
| progress_capture / report / knowledge_base | Domain | 证据/报告/知识模型（store 为 Adapter） |
| events / slo | Domain | 事件模型 / 指标聚合 |
| model | Ports | ModelProvider 协议（厂商为 Adapter） |
| crypto | Ports | CryptoProvider 协议 + scope 治理（gmssl/cng 为 Adapter） |
| identity | Ports | 证书/私钥引用协议（repository/CNG 为 Adapter） |
| framework | Application/Ports | 校验/策略/Plan/Lifecycle（Ports）；Hybrid 编排/集成（Application） |
| orchestrator | Application | 运行中枢（唯一执行器，见 orchestrator-seam） |
| app | Application | 组合根（pipeline/demo_support） |
| cockpit | Application/Adapters | facade=Application；server/static/wps=Adapters |
| audit_governance | Application/Adapters | facade/stream=Application；stream_store=Adapter |
| workspace | Ports/Adapters | 路径策略=Ports；init_service=Adapter |
| protocol | Ports | `.agent` 编解码/导入/重放 |
| sync | Ports | 跨节点同步信封契约/出站队列/对账（离线文件包；在线传输为 Adapter） |
| benchmarks | Adapters | 探针 |

## 3. 不变量

1. Domain Core 不得执行 IO（stdlib 断言由各模块文档与测试守卫）；
2. 业务逻辑不得直接绑定厂商/存储实现——必须经 Ports；
3. 外部能力（CNG/GmSSL/WPS/模型/文件/SQLite/审计存储/消息通道）一律经 Adapters；
4. 模型输出只能以 `DraftSuggestion` 进入业务层（REVIEW2-7）；
5. 新增实现必须先声明所属层并同步本契约。

## 4. 守卫测试

`tests/unit/test_eng_optimize_4_ports_adapters.py`：四层定义存在；`src/coevo`
全部包均出现在映射表；不变量关键字（无 IO / 注入 / 厂商）存在。

## 5. 变更纪律

调整层归属或新增跨层依赖必须同步本契约并在 `loop/DECISIONS.md` 留痕。
