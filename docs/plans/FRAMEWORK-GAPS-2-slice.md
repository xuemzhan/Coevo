# FRAMEWORK-GAPS-2 切片计划：GAPS-1 新观察项收口

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。本轮只跑
> 增量门禁（fmt + lint + 定向测试），豁免留痕。

## 1. 目标工作项

- 工作项：`FRAMEWORK-GAPS-2`（ENG-BASE，dependencies=[FRAMEWORK-GAPS-1]）
- 目的：收敛 FRAMEWORK-GAPS-1 审查提出的 3 项新 Low/Info 观察项。

## 2. 收口清单

| 观察项 | 处理 |
| --- | --- |
| Policy 超时/重试字段接受 bool（True=1）、非 int 抛 TypeError | `type(...) is int` 严格校验，统一 PolicyValidationError |
| semver/ISO 仅形状校验（前导零、不可能日期可过） | semver 严格规则（禁前导零）+ ISO 用 datetime.strptime 校验日历范围 |
| validated_at 未校验即入审计投影 | validate_plan 与 transition 统一 L7 ISO 校验 |

## 3. 需修改/新增文件

- 修改 `src/coevo/framework/policy.py`、`manifest_checker.py`、`a2a.py`、
  `memory.py`、`validation.py`、`orchestrator.py`
- 新增 `tests/unit/test_framework_gaps2.py`；更新
  `tests/unit/test_framework_orchestrator.py`（transition 用例补 validated_at）

## 4. 测试要点（含异常/负例）

- Policy：timeout/retry/consent 各字段 bool、字符串、float 一律 PolicyValidationError；
  合法 int 通过；默认 4 Profile 全通过；
- semver：`1.01.0` / `01.0.0` / `1.0.01` 拒绝；`0.2.0` / `1.0.0` 通过；
- ISO：`2026-99-99T99:99:99Z` / `2026-02-30T00:00:00Z` / 无 Z 拒绝；
  `2026-08-08T08:00:00Z` 通过；
- validated_at：validate_plan 空/非 ISO → REJECTED；transition 空/非 ISO →
  REJECTED；ISO 通过；
- L15 stdlib / L17 文档守卫回归。

## 5. 可验证完成条件

- `python -m unittest tests.unit.test_framework_gaps2` + 既有框架测试全绿；
- fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-GAPS-2 行。

## 6. 审查门

- security-reviewer：**是**（严格化校验 / 审计投影一致性）；
- protocol-reviewer：**否**。
