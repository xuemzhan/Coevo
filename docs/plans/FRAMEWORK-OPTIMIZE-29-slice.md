# FRAMEWORK-OPTIMIZE-29 切片计划：安全关键域注释强化（crypto/identity/protocol）

> 状态：已批准（2026-08-09 用户指令"继续补全注释"；增量门禁口径，全量 quality
> 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-29`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-28]）。
- 目的：继续注释补全，覆盖**安全关键域** crypto / identity / protocol 共 **61 个
  缺少 docstring 的函数**，写明失败关闭语义、哈希链绑定、受控子进程调用契约、
  返回/异常语义；纯注释、零行为变化。

## 2. 交付

- `src/coevo/crypto/{cng_handle,gmssl_provider,sm3}.py`（8+3+3 处）；
- `src/coevo/identity/{audit_anchor,repository,private_keys,validation,certificates}.py`
  （12+7+6+4+1 处，含重名 `_run` 按行号区分）；
- `src/coevo/protocol/{agent_package,package_store_db,package_builder,import_service,
  replay_detector}.py`（7+7+1+1+1 处）；
- 守卫测试 `tests/unit/test_framework_optimize30.py`——按 (文件,行号) 锁定
  61 个函数均有非空 docstring。

## 3. 测试要点

- 守卫：61 个目标函数（按文件+行号）均有非空 docstring；文件可编译；
- 回归：crypto/identity/protocol 相关既有测试（cng_handle、gmssl_provider、
  private_key_handles、identity_validation、agent_package、package_store 等）全绿。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-29` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**否**（纯注释，无逻辑变更；docstring 与既有失败关闭语义一致）。
- protocol-reviewer：**否**。
