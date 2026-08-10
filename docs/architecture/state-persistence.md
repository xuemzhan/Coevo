# 状态持久化矩阵（State Persistence Matrix）

> 状态：生效（2026-08-10，ARCH-REVIEW-11；落实架构审查 P2-2）
> 用途：显式区分"内存态"与"持久态"，回答每个有状态组件**重启后是否保留、
> 如何恢复**，防止演示路径与生产路径混淆。

## 1. 总原则

- **内存态**：纯模型/注册表/计数器，重启即丢失；必须在组合根重建或由持久层回放；
- **持久态**：SQLite / JSONL / 受控文件系统 / CNG 密钥存储，重启保留；
- 正式任务状态（项目主版本、合并收据、编排实例、审计链）**必须**持久化；
- 内存态组件在文档中显式标注，任何把内存态当作持久态的接线都属于架构违规。

## 2. 状态持久化矩阵

| 模块 | 有状态组件 | 存储介质 | 重启行为 | 恢复/同步 | 审计关联 |
|---|---|---|---|---|---|
| `src/coevo/identity/repository.py` | IdentityRepository | SQLite 身份库 + 签名单调新鲜度锚 | 重启保留 | 锚校验失败即回滚/拒绝 | 身份与密钥配置审计 |
| `src/coevo/identity/private_keys.py` | PrivateKeyStore / WindowsPrivateKeyStore | Windows CNG KSP（非导出句柄）+ 受保护密钥引用 | 重启保留 | 句柄重新获取 + 公钥摘要绑定校验 | 密钥生命周期审计 |
| `src/coevo/crypto/cng_handle.py` | CngKekStore / CngWrappedKeyRegistry | CNG KEK（OS 保护）+ 包装密钥注册 | 重启保留（KEK）；注册表随配置重建 | 密钥不落明文，失败关闭 | 密码操作审计 |
| `src/coevo/crypto/contract.py` | ProviderRegistry | 内存（Provider 作用域注册） | 重启重建 | `require_approved` 拒绝原型/未声明作用域 | 密码提供方审计 |
| `src/coevo/protocol/processed_package_store.py` | ProcessedPackageStore | 内存（纯函数，无 IO） | 重启丢失 | 持久化登记由 `package_store_db.py` 提供 | 重放/重复包审计 |
| `src/coevo/protocol/package_store_db.py` | PackageStoreDb | SQLite 已处理包登记 | 重启保留 | 原子提交/回滚 | 导入/重放审计 |
| `src/coevo/workspace/models.py` | WorkspaceRegistry | 内存（纯模型） | 重启丢失 | 工作区目录落盘；视图状态由 cockpit state_store 恢复 | 工作区初始化审计 |
| `src/coevo/orchestrator/models.py` | AgentRegistry | 内存 | 重启丢失 | 组合根按能力目录重建注册 | 智能体注册审计 |
| `src/coevo/orchestrator/real_chain_store.py` | RealChainStore | SQLite + 哈希链 + 签名锚 | 重启保留 | 锚点恢复（RecoveryRequired 语义） | 编排实例审计 |
| `src/coevo/merge/receipt.py` | MergeCommitReceiptStore | 内存密封 store（纯函数） | 重启丢失 | 持久化由 `merge/repository.py` 提供 | 合并收据审计 |
| `src/coevo/merge/repository.py` | MergeReceiptRepository | SQLite 密封收据链（全量重校验） | 重启保留 | 行级门禁 + 锚恢复 | 合并审计 |
| `src/coevo/decision_brief/repositories.py` | ApprovedTemplateRegistry / RiskConfirmationRepository / DecisionBriefRepository | 模板=受控文件系统；审批/风险确认/简报=内存 CAS | 重启丢失（模板文件保留） | 权威收据经 merge 收据链；简报版本链为内存 CAS | 简报/模板审计 |
| `src/coevo/knowledge_base/store.py` | KnowledgeStore | SQLite + 哈希链审计 | 重启保留 | schema 校验 + 追加独占 | 知识入库审计 |
| `src/coevo/audit_governance/stream.py` | AuditStreamHub | 内存 pub/sub + 有界缓冲 | 重启丢失 | 持久化委托 `stream_store.py` | 审计流投递 |
| `src/coevo/audit_governance/stream_store.py` | AuditStreamStore | JSONL 哈希链 store | 重启保留 | 回放 + 追加独占 | 审计链本体 |
| `src/coevo/cockpit/state_store.py` | CockpitStateStore | JSON 原子写（临时文件 + 换名） | 重启保留 | 损坏 fail-closed | 驾驶舱操作/访问日志 |
| `src/coevo/talent/store.py` | TalentStore | SQLite 脱敏人才库 | 重启保留 | 完整性/哈希链校验 | 推荐审计投影 |
| `src/coevo/progress_capture/watcher.py` | WorkspaceWatcher | 文件系统 + 内存缓存（mtime/哈希） | 重启重建扫描 | 未变化文件免重哈希 | 进展采集审计 |
| `src/coevo/report/builder.py` | ReportSubmissionSequence | 内存单调计数 | 重启重置 | 包唯一编号仍全局唯一，序号重新累计 | 成果包导出审计 |
| `src/coevo/framework/manifest_checker.py` | ManifestRegistry / PolicyRegistry | 内存 / 协议注入 | 重启重建 | 部署点校验为纯函数 | 框架审计投影 |
| `src/coevo/framework/memory.py` | EpisodicMemoryStore / SemanticMemoryStore | 注入存储（协议） | 视注入实现 | 脱敏（REDACTED:sha256）+ 审批投影 | 记忆审计投影 |
| `src/coevo/framework/tools.py` | ToolRegistry | 内存 | 重启重建 | 校验与注册分离 | 工具调用审计 |
| `src/coevo/model/prompts.py` | PromptRegistry | 内存（静态配置模板） | 重启重建 | 模板校验 | 模型调用留痕 |
| `src/coevo/app/demo_support.py` | DemoPolicyRegistry | 内存（演示替身） | 重启重建 | 演示路径专用，生产组合根禁用 | 演示审计 |

## 3. 接线纪律

1. 新增大文件或存储组件时，本矩阵必须同步更新（守卫测试强制覆盖全部
   `*Store/*Repository/*Registry/*Hub/*Watcher` 组件所在模块）；
2. 内存态组件不得被当作正式任务状态的权威来源；
3. 把内存态升级为持久态必须先声明存储介质、恢复流程与审计关联，再实现。

## 4. 守卫测试

`tests/unit/test_arch_review_11_persistence_matrix.py`：扫描 `src/coevo` 全部
有状态组件模块，断言矩阵覆盖每个模块，并断言矩阵包含"重启保留/重启丢失"语义。
