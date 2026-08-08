# FRAMEWORK-OPTIMIZE-6 切片计划：demo 组合根阶段化收敛（pipeline 薄编排）

> 状态：已批准（2026-08-08 用户指令"基于框架，优化原来系统应用的代码实现，
> 包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-6`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-5]）。
- 目的：`app/pipeline.py` 的 `run_demo_pipeline` 仍是一个 ~250 行的大函数，
  内联了包导出、驾驶舱快照、知识库入库、审计流 4 段装配。本轮把**无状态阶段
  提取为模块级函数**（薄编排 + 可独立测试），组合根只做调度与结果组装
  （模块架构优化，行为不变，demo e2e 守护）。

## 2. 交付

- `src/coevo/app/pipeline.py` 新增模块级阶段函数（demo 组合根私有助手）：
  * `_export_demo_package(...) -> tuple[Path, str]`：加密包构建 + 三方回环校验
    + outbox 落盘 + SHA-256（原 #4 段，含 json/hashlib 局部 import）；
  * `_build_demo_cockpit_views() -> tuple[WorkspaceView, RoleView]`（原 #5 快照段）；
  * `_store_demo_knowledge(run_dir, now) -> str`（原 #6 段，返回 bundle_id）；
  * `_publish_demo_audit(hub, now) -> None`（原 #7 段）。
- `run_demo_pipeline` 主体改为调用上述阶段函数；顶部 `hashlib`/`json` import
  移入 `_export_demo_package`（`uuid` 保留给主函数 run_dir）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize6.py`：
  * `_build_demo_cockpit_views` 返回字段正确的快照（纯数据）；
  * `_publish_demo_audit` 发布 3 条事件且订阅者收到；
  * `_store_demo_knowledge` 在临时目录生成 knowledge.db 并返回 bundle_id；
  * 模块架构守卫：`run_demo_pipeline` 不再内联 `build_encrypted_package` /
    `KnowledgeBaseFacade.aggregate` / `AuditStreamHub()` 字面（已收敛到阶段函数）。
- 回归：demo e2e（test_demo_runner）+ test_pipeline_framework_gate + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-6 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（组合根装配路径与 demo 密钥/包导出相关，须确认
  fail-closed 与 demo-only 边界不因提取而改变）；protocol-reviewer：**否**。
