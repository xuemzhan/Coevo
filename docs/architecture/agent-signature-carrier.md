# `.agent` 签名承载契约（Signature Carrier Contract）

> 状态：生效（2026-08-10，REVIEW2-3）
> 适用范围：`src/coevo/protocol/package_builder.py` / `sm2_sign.py` 的签名承载边界。

## 1. 承载定位

- **交付路径（唯一可宣称"完整可独立验证"的路径）**：`build_encrypted_package` 把
  `sender.sig`（协议 §12）**嵌入认证加密内层载荷**（协议 §8 布局：
  `manifest.json` + `sender.sig`），与内容同生命周期、同加密信封；
  Envelope 作为 AEAD associated data 绑定。因此 `.agent` 字节文件自包含，
  接收方解密后即可对 `manifest.json` 独立验签。
- **P1 未签名表面（fail-closed 载体）**：`build_unsigned_package` /
  `parse_package_bytes` 产出的 `BuiltPackage.signature` 是占位记录
  （`signature == ""`），任何验签尝试一律抛出
  `AgentPackageCryptoVerifyError`。该表面不得被宣称/包装为已完成签名的
  正式安全制品；正式签名等待 US-5-AC-2 批准的 SM2 产品接入。

## 2. 签名覆盖范围

- 签名对象：规范化的 `manifest.json` 字节（协议 §10 canonical 规则 + §12 SM3 摘要）；
- 签名算法：`SM2-SM3`（`cipher_suite = CS-SM2-SM4-AEAD-SM3-01`）；
- Envelope 不参与被签 manifest，但通过 AEAD associated data 与载荷绑定，
  任何 Envelope 篡改都会导致解密/验签失败（fail-closed）；
- 验签失败错误码：`AGT-CRY-003` / `AGT-CRY-004`（协议 §22）。

## 3. 守卫测试

`tests/unit/test_review2_3_signature_carrier.py`（假 provider，纯单元）强制：

- 交付路径 wire 自包含：`build_encrypted_package → to_bytes →
  parse_package_bytes → open_encrypted_package` 无需任何外部签名对象即可
  取回并验签 `sender.sig`；
- 载荷篡改（ciphertext/tag/envelope AAD）→ 打开/验签 fail-closed；
- manifest 与签名失配 → `AGT-CRY-004`；
- 截断 / 尾随字节 / 重复键 / 跨主版本拒绝；
- 未签名表面占位签名 → 验签 fail-closed。

## 4. 变更纪律

任何改变签名承载位置、覆盖范围或 fail-closed 语义的改动，必须先同步本契约与
协议文档，并在 `loop/DECISIONS.md` 留痕；`.agent` 主版本调整须走停止条件审批。
