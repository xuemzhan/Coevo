# FRAMEWORK-OPTIMIZE-23 切片计划：manifest_checker._validate 阶段化拆分

> 状态：已批准（2026-08-09 用户指令"继续"；增量门禁口径，全量 quality 按用户指示豁免）。

## 1. 目标工作项

- 工作项：`FRAMEWORK-OPTIMIZE-23`（ENG-BASE，dependencies=[FRAMEWORK-OPTIMIZE-22]）。
- 目的：`framework/manifest_checker.py:_validate`（150 行，复杂度约 33）按既有
  校验顺序做**纯迁移式阶段拆分**为 7 个模块级私有助手，`_validate` 收敛为线性编排；
  校验顺序、错误消息字符串、失败关闭语义逐字节不变；导入面不变。

## 2. 交付

- `src/coevo/framework/manifest_checker.py` 新增 7 个模块级私有函数（代码原样搬移）：
  1. `_validate_metadata(parsed)`——metadata 对象/agent_id/display_name/semantic_version
     （原 311-324 行，返回 `(agent_id, display_name, semantic_version)`）；
  2. `_validate_spec(parsed)`——spec 对象/capability 解析与 MVP 白名单/rhc
     （原 326-342 行，返回 `(capability, rhc, capability_entry)`）；
  3. `_validate_security(parsed, capability_entry)`——security 对象/crypto_scope/
     CRYPTO_PROXY 限定（原 344-360 行）；
  4. `_validate_audit(parsed)`——audit 对象/redact_in_audit 白名单（原 362-378 行）；
  5. `_require_policy(parsed, policy_registry)`——policy_profile/version 注册表存在
     （原 380-390 行，返回 `(profile, version)`）；
  6. `_compute_spec_hash(parsed)`——declared vs computed 一致性（原 392-400 行）；
  7. `_verify_policy_binding(parsed, declared, cert_resolver, signature_verifier)`
     ——policy_ref 三要素绑定 + 证书指纹 + SM2 验签（原 402-436 行）。
- `_validate()` 收敛为 7 步编排 + trusted_anchor 检查 + AgentManifest 构造
  （约 40 行）。
- 守卫测试 `tests/unit/test_framework_optimize24.py`。

## 3. 测试要点

- 守卫：`_validate` 方法体不超过 80 行（原 150）；7 个阶段助手存在且被 `_validate`
  调用；关键错误消息标记存活（连续字面量）；
- 回归：`tests/unit/test_framework_manifest_checker.py` 全量（32 项）+
  `tests/unit/test_framework_optimize14.py`（manifest 相关）。

## 4. 完成条件

- 定向测试全绿；`fmt` + `lint` exit=0；`archive_records.py --check` exit=0；
- 追溯矩阵新增 `ENG-BASE | FRAMEWORK-OPTIMIZE-23` 行（无悬空）；
- 全量 quality 按用户指示豁免并留痕。

## 5. 审查

- security-reviewer：**是**（manifest 校验为部署点安全关键路径：capability 白名单、
  证书指纹绑定、SM2 验签、policy 注册表；纯迁移不改判定顺序与错误语义）。
- protocol-reviewer：**否**。
