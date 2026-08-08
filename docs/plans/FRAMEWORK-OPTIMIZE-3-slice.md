# FRAMEWORK-OPTIMIZE-3 切片计划：共享 JSON 规范化序列化与摘要（canon.py 叶子）

> 状态：已批准（2026-08-08 用户指令"基于框架，优化原来系统应用的代码实现，
> 包括数据结构、算法与模块架构，不做全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-3`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-2]）。
- 目的：与 timefmt 对称，新增根级依赖无关叶子模块 `src/coevo/canon.py`，统一
  "canonical JSON 序列化 + SHA-256 摘要"实现：
  1. 框架内部重复：`framework/integration.py::_canonical` 与
     `framework/manifest_checker.py::_canonical_bytes` 字节语义完全相同 → 收敛；
  2. 产品 digest 内联：`identity/repository.py`（审计事件哈希链 2 处 +
     business digest 1 处）、`identity/validation.py`（bundle digest 1 处）、
     `identity/private_keys.py`（私钥审计链 1 处）的
     `hashlib.sha256(json.dumps(...)).hexdigest()` → `canonical_digest`。
- 不变式：所有收敛点字节/hash 逐位不变（既有审计链、wire、bundle digest 语义
  不受影响）；`ensure_ascii` 语义逐点保留（默认 True；repository business digest
  为 False）。

## 2. 交付

- 新增 `src/coevo/canon.py`（根级叶子，stdlib only）：
  `canonical_json_bytes(value, *, ensure_ascii=True) -> bytes`（sort_keys、
  separators=(",",":")、无换行，与既有实现一致）；
  `canonical_digest(value, *, ensure_ascii=True) -> str`（sha256 hex）。
- `framework/integration.py` / `framework/manifest_checker.py`：删除私有
  `_canonical` / `_canonical_bytes`，改用 `canonical_json_bytes`。
- `identity/repository.py` / `validation.py` / `private_keys.py`：5 处 digest
  内联改用 `canonical_digest`（repository 128/159 与 private_keys/validation
  默认 ensure_ascii=True；repository 143 business digest ensure_ascii=False）。
- `docs/modules/root_modules.md` 登记 `canon.py`。

## 3. 测试要点

- 新增 `tests/unit/test_framework_optimize3.py`：
  * `canonical_json_bytes` 字节回归（固定样例）与 `canonical_digest` 与手工
    sha256 一致（含 ensure_ascii=True/False 两分支）；
  * 全仓守卫：framework 两模块不再含私有 `_canonical*` 定义；
    identity 三模块不再含 `hashlib.sha256(json.dumps(` 内联 digest
    （排除 canon.py 与测试夹具）；
  * 抽样：repository 事件哈希链 digest 可复现、与旧表达式一致。
- 回归：test_framework_integration(2/4)、test_framework_manifest_checker、
  test_identity_validation、test_identity_repository*、test_private_key_storage、
  test_identity_freshness_security、test_identity_store_security + 全量单元。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-OPTIMIZE-3 行（无悬空）。

## 5. 审查门

- security-reviewer：**是**（identity 审计事件哈希链与私钥审计链为安全关键，
  须确认 digest 逐位不变、fail-closed 语义保留）；protocol-reviewer：**否**
  （wire 字节不变，纯重构）。
