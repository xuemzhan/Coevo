# 审计签名密钥生命周期仪式（Audit Key Ceremony）

> 状态：生效（2026-08-10，ARCH-REVIEW-5；security_review=true——生产执行前需独立安全审查）
> 适用范围：`loop/audit-signing.json`、`scripts/audit_signature.ps1` 的签名密钥治理。

## 1. 当前状态

- 单签名者：thumbprint `F6DE13A4ADF56B9D66902B8E3055DCCA8B702D86`；
- 私钥经 Windows CNG（`CurrentUser/My`）不可导出，Python 进程不接触密钥字节；
- 签名算法 RSA-PKCS1-v1_5 / SHA-256（`prototype=true`）；
- 正式替换方向：国家密码产品 + 受保护密钥句柄（long-term，已记录于配置）。

## 2. 轮换仪式（Rotate）

1. 生成新签名者密钥对（受控 CNG/HSM 容器，非导出）；
2. 签发新证书并写入 `loop/audit-signing-public.cer`（新指纹）；
3. 过渡期：新签者先对**历史 head** 补签一次（保留旧 p7s 归档）；
4. 更新 `audit-signing.json`（thumbprint/证书哈希/算法），人工审批 + 独立验证；
5. 旧签名者密钥归档/销毁（受控流程，销毁前导出收据）。

## 3. 离线备份（Backup）

- 公钥/证书：`loop/audit-signing-public.cer` 随仓库版本化；
- 私钥：CNG 非导出密钥按组织备份策略在受控备份容器保存（禁止明文/仓库内）；
- 备份操作必须形成审计记录。

## 4. 丢失恢复（Recovery）

1. 确认原签名者不可用（受控诊断）；
2. 生成新签名者并更新 `audit-signing.json`（人工审批）；
3. 对现有 audit-head 用新签者重新签名，历史 p7s 保留归档；
4. 全链复验：`audit_log verify` + `audit_seal verify` + 追溯矩阵 + 独立验证；
5. 恢复过程全程留痕（DECISIONS + tool-audit）。

## 5. 备份签名者评估（Backup Signer）

- 风险：单签名者丢失/泄露 = 信任基座重建；
- 评估方向：HSM 多签 / 备份签名者 + 轮换窗口，作为后续工作项；
- **当前方案不变**（不新增第二签名者），评估结论另行决策。

## 6. 守卫测试

`tests/security/test_arch_review_5_audit_key_ceremony.py`：契约存在且含
轮换/备份/恢复/备份签名者章节；`audit-signing.json` 为单签名者且
`prototype=true`；运行手册 `docs/operations/audit-key-runbook.md` 存在。
