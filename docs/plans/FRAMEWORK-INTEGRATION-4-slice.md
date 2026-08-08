# FRAMEWORK-INTEGRATION-4 切片计划：注册门接入与 Manifest 构建器

> 状态：已批准（2026-08-08 用户指令"继续开发，先不要全量门禁"）。增量门禁口径。

## 1. 目标工作项

- 工作项：`FRAMEWORK-INTEGRATION-4`（ENG-BASE，dependencies=[FRAMEWORK-INTEGRATION-3]）
- 目的：完成 US-16"只有声明合规的智能体才能进入编排"——把 `guard_registration`
  接入真实管线注册路径，并新增纯函数 Manifest 构建器供任意产品接线。

## 2. 交付

- `framework/integration.py`：`build_registration_manifest(agent_id, capability, *,
  display_name, semantic_version, policy_profile, policy_version, crypto_scope,
  requires_human_confirmation, signer_cert_fingerprint, signer)` —— 规范 JSON
  Manifest（spec_hash 排除自指字段；`signer` 可选，签名覆盖
  `spec_hash|fingerprint`）。
- `app/demo_support.py`：`DemoRegistrationVerifier` / `DemoRegistrationResolver` /
  `DemoPolicyRegistry`（显式 **非生产**，注释 + 文档强警告：生产必须注入真实
  SM2 验签与证书链）。
- `app/pipeline.py`：注册 4 个智能体前先 `guard_registration`（Manifest 结构 +
  绑定格式 + policy 版本校验通过才注册）。

## 3. 测试要点

- 构建器：合法 Manifest 的 spec_hash 与 manifest_spec_hash 一致；篡改任何字段后
  guard_registration 拒绝；未注入签名器时 signature 为空但仍可结构校验；
- demo 注册门：4 个 Manifest 全部 accepted 且 inner_register 各调用一次；
- 负例：未知能力 / 缺 policy_version / 非法 crypto_scope 拒绝且不注册；
- L15 stdlib / L17。

## 4. 完成条件

- 定向测试全绿；fmt / lint exit 0（不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 ENG-BASE | FRAMEWORK-INTEGRATION-4 行。

## 5. 审查门

- security-reviewer：**是**（demo 验签适配器边界——必须显式非生产并文档化，
  防被误用为生产路径）；protocol-reviewer：**否**。
