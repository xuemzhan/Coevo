# 源码文件规模预算（File Size Budget）

> 状态：生效（2026-08-10，ENG-OPTIMIZE-7；落实架构审查 P2-1）
> 适用范围：`src/coevo` 全部跟踪 `.py` 文件

## 1. 预算规则

- **单文件上限 `MAX_FILE_LINES = 1133`**：任何 `src/coevo` 跟踪 `.py` 文件不得
  超过该行数（当前最大文件 `merge/engine.py`）；
- **大文件登记 `KNOWN_LARGE_FILES`**：超过 600 行的文件必须登记（当前 11 个），
  且登记行数只降不增——新增大文件必须先拆分，禁止静默膨胀；
- 守卫测试扫描 `git ls-files src/coevo -- '*.py'` 的**跟踪树**，不依赖工作区
  未跟踪文件。

## 2. 例外流程

确需新增超阈值文件时，必须先拆分或经架构评审在 `loop/DECISIONS.md` 留痕并
同步更新本契约与守卫测试中的登记表；不允许通过删除守卫测试"修复"失败。

> 2026-08-12（MATURITY-O-06）：驾驶舱新增 `SUPERVISION_VIEW` 路由与
> `SupervisionSummary` 快照，经契约例外流程登记
> `src/coevo/cockpit/facade.py: 676`、`src/coevo/cockpit/server.py: 1108`
> （见 `loop/DECISIONS.md` 对应条目；计数维持 11 个）。

## 3. 守卫测试

`tests/unit/test_eng_optimize_7_file_size_budget.py`：预算上限 / 大文件集合钉死 /
登记行数不增长 / 契约文档存在并登记文档索引。
