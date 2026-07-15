# 开发环境

当前离线基线使用：

- Python 3.14+（业务代码与零下载质量门禁）；
- Windows PowerShell 5.1+ / .NET X.509、CMS 与 CNG API（严格证书解析、签名审计链头和代际新鲜度标记）；
- Git 2.53+；
- 当前 Windows 开发用户 `CurrentUser/My` 中固定指纹、不可导出的审计签名私钥。

执行完整门禁：

```powershell
.\scripts\dev.ps1 -Task quality
```

或直接执行：

```powershell
python scripts/validate_opencode.py
python scripts/quality_gate.py --target quality
```

门禁会验证 Python 源码、OpenCode 配置、追踪矩阵、单元/集成/安全/E2E 测试、全局审计签名，以及身份库的真实 DER X.509 解析、独立签名审计锚点和回滚检测。证书解析失败、签名证书缺失、私钥可导出、链头不匹配、当前代际标记缺失或存在无法验证的 pending/退休状态时均失败关闭。

## 身份库创建与打开

- 新库必须显式调用 `IdentityRepository.create(...)`；已存在的路径、未完成初始化或缺失的锚点都会被拒绝。
- 已有库必须显式调用 `IdentityRepository.open(...)`；数据库、正式链头、签名或当前代际标记任一缺失/不匹配时不会静默重建。
- 每次业务提交都会生成新的不可导出 CNG 标记私钥和 `CurrentUser/My` 标记证书。marker 同时绑定 `store_id`、代际号、检查点摘要、随机 `transition_id`、CNG `key_id` 与公钥 blob SHA-256；固定审计签名者再以 CMS 签名认证该链头。
- pending 检查点同时由旧、新标记签名。新链头激活后，旧标记严格先按签名绑定的 key ID 与公钥摘要销毁私钥并验证无法重新打开，再移除证书。
- 正式 head 内含退休 tombstone；其固定审计签名和幸存 marker 签名副本持久化到 `%LOCALAPPDATA%\Coevo\identity-retirements\<store_id>`。密钥销毁、证书移除、tombstone 原子提交并复验之前不会清理 pending。
- 崩溃恢复覆盖密钥已删但证书仍在、证书已删但 tombstone 未提交以及 tombstone 已提交但 pending 未清理。旧证书重新导入后因对应 CNG 私钥已销毁，不能重新关联签名或恢复旧快照。

证书候选数据通过标准输入传给严格解析脚本，不会把待验证 DER 写入临时文件。安全测试覆盖完整旧快照回放、标记与 tombstone 缺失/篡改、pending 双签篡改、key-first 删除各阶段崩溃和真实 Windows 证书库路径。

## 依赖与部署边界

本轮没有引入或下载第三方 Python 包。`opencode`、GNU Make、Go、pytest、ruff 仍未纳入已批准依赖；导入前必须登记离线来源、精确版本、SHA-256 与许可证，禁止 bootstrap 脚本联网安装。`python scripts/validate_opencode.py --require-tools` 会明确报告可选工具缺失。

项目级安全配置禁止联网工具、外部目录和依赖安装。组织级 `%ProgramData%\opencode\opencode.jsonc` 需要管理员单独部署，本仓库不会修改它。

开发期使用 RSA-3072/SHA-256、本机自签代际标记和固定审计签名者，仅用于本机篡改与回滚发现；正式环境仍必须替换为批准的 SM2 产品、组织证书链、受保护的硬件密钥和独立审计节点。
