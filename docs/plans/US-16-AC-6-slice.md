# US-16-AC-6 切片计划：A2A wire 0.1 与 policy_ref 三段绑定（CTAF §7.3 / M5）

> 状态：已批准（2026-08-08 用户指令"继续开发"）。本轮只跑增量门禁（fmt + lint +
> 定向测试），不跑全量 quality（用户指示，豁免留痕）。M5 触发 protocol-reviewer。

## 1. 目标工作项与用户故事

- 工作项：`US-16-AC-6-a2a-wire-v0.1`
- 用户故事：US-16【框架层】——把 A2A 消息抽象为纯数据模型，正式化 policy_ref
  三段绑定与 §7.3.3 五步验证时序，并钉住 `.agent` v1.0 wire 不变。

## 2. AC 清单与目标测试

| AC | 内容 | 目标测试 |
| --- | --- | --- |
| AC-6.1 | A2A 消息模型全字段校验 | test_a2a_field_validation |
| AC-6.2 | policy_ref 三段绑定五步验证 | test_policy_ref_five_step_verification |
| AC-6.3 | A2A ↔ `.agent` 字段映射往返一致 | test_agent_field_mapping_round_trip |
| AC-6.4 | 大小边界：>64KiB 业务载荷必须拆分 | test_payload_split_boundary |
| AC-6.5 | 纯函数 / 离线 / stdlib / 审计投影 / L17 | test_stdlib_only + test_module_docs |

## 3. 最小可交付切片

新增 `src/coevo/framework/a2a.py`：A2aMessage / PolicyRef（frozen）、
validate_a2a、verify_policy_ref（五步：证书解析→指纹→spec_hash→SM2 验签→接受，
注入 cert_resolver / signature_verifier，复用 manifest_checker 的规范哈希）、
to_agent_fields / from_agent_fields（§7.3.1 映射）、validate_payload_size
（>64KiB 必须 payload_ref 拆分）、A2aVerificationResult 审计投影。
新增 `docs/framework/a2a-protocol.md`；更新 `docs/modules/framework.md`（L17）。

## 4. 需修改/新增文件

- 新增 `src/coevo/framework/a2a.py`；修改 `src/coevo/framework/manifest_checker.py`
  （暴露公开 `manifest_spec_hash` 供复用）；修改 `src/coevo/framework/__init__.py`
- 新增 `tests/unit/test_framework_a2a.py`
- 新增 `docs/framework/a2a-protocol.md`；修改 `docs/modules/framework.md`

## 5. 测试要点（含异常/负例）

- 字段：task_id/trace_id/sender/recipient/payload_ref safe-id 与 hex64、
  sequence_no 非负、purpose 能力闭集、created_at 非空；负例全拒；
- 五步验证：证书缺失/指纹不匹配/spec_hash 不符（含自指字段参与哈希）/签名
  失败/验证器异常——每步失败均拒绝且 failure_reason 明确；
- 映射：合法消息 → .agent 字段 → 消息往返相等；缺字段/多未知字段拒绝；
- 大小：payload_len ≤ 64KiB 内联通过；> 64KiB 无 payload_ref 拒绝、有合法
  payload_ref 通过；payload_ref 非法 safe-id 拒绝；
- 审计投影键集固定；L15 stdlib / L17 文档守卫。

## 6. 安全与兼容性风险

- policy_ref 验签公钥必须来自证书链（防公钥自包）；五步时序任一失败即拒绝；
- `.agent` v1.0 wire 不变（T6 守护），A2A 仅是 payload 层约定；
- 大小边界防信封越界（放宽须主版本升级）；
- 零新增三方依赖；文档守卫。

## 7. 明确不属于本轮

- 跨组织 PKI 联邦（§7.3.4 显式信任列表路线）；A2A gossip / 跨域发现（v0.5）；
- M6（Plan-LSP）、M7（Hybrid）、M8/M9；
- `.agent` wire 改动（保持字节级不变）。

## 8. 可验证完成条件

- `python -m unittest tests.unit.test_framework_a2a` 全绿；
- `python scripts/quality_gate.py --target fmt` 与 `--target lint` exit 0
  （不跑全量 quality，豁免留痕）；
- 追溯矩阵新增 US-16 | AC-6 行；security-reviewer 与 protocol-reviewer
  无 Critical/High 阻断。

## 9. 给实施者的指令包

按第 4/5 节实现；对齐框架层既有风格（frozen dataclass、注入协议、fail-closed、
stdlib-only、审计投影）；只 stage 本轮文件；提交信息
`feat(framework): US-16-AC-6 A2A wire 0.1 + policy_ref (M5)`。

## 10. 审查门

- security-reviewer：**是**（身份/信任/policy_ref/大小边界）；
- protocol-reviewer：**是**（A2A 邻近 `.agent` 协议面，wire 不变仍须审批）。
