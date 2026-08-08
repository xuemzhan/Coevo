# FRAMEWORK-GAPS-7 切片计划：生产验签入口守卫（demo/production 边界收口）

> 状态：已批准（2026-08-08 用户指令"继续下一步"，延续"基于框架，优化原来系统
> 应用的代码实现，包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。
> 收口 INTEGRATION-4 安全审查 Low 1（demo 验签器对任意非空签名返回 True；
> 生产路径必须注入真实 SM2 验签）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-GAPS-7`（ENG-BASE，dependencies=[FRAMEWORK-INTEGRATION-4]）。
- 目的：`guard_registration` 目前接受任意 `signature_verifier`，demo 适配器
  （`DemoRegistrationVerifier`，对任意非空签名返回 True）理论上可被误用于生产
  注册路径。本轮增加**生产验签入口守卫**：`guard_registration` 新增
  `require_production_verifier` 参数（默认 False），为 True 时强制验签器显式声明
  `is_production is True`（真实 SM2、绑定证书链），否则 fail-closed 拒绝；
  demo 适配器补显式 `is_production = False`。不实现真实验签器（非本轮范围）。

## 2. 交付

- `src/coevo/framework/integration.py`：`guard_registration` 新增
  `require_production_verifier: bool = False` 参数（默认行为不变；True 时
  非生产验签器 fail-closed 拒绝，reason 明确）。
- `src/coevo/app/demo_support.py`：`DemoRegistrationVerifier` 补显式
  `is_production = False` 类属性（与"显式非生产"标注一致）。

## 3. 测试要点

- 新增 `tests/unit/test_framework_gaps7.py`：
  * require_production_verifier=True + DemoRegistrationVerifier → rejected
    （fail-closed，零注册）；
  * require_production_verifier=True + 生产协议验签器（is_production=True）→
    accepted（结构校验通过、inner_register 单次）；
  * 默认 False + DemoRegistrationVerifier → accepted（demo 行为不变）；
  * demo 适配器显式 is_production=False（源码守卫）。
- 回归：test_framework_integration4（demo 注册门）/ test_framework_integration /
  全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-7 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（生产注册边界为身份/权限关键，须确认 fail-closed
  与 demo 隔离语义正确）；protocol-reviewer：**否**。
