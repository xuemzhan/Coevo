# 审计签名密钥健康诊断与恢复手册（AUDIT-KEY-1）

> 状态：生效（2026-08-03）。对应 P0-3 决策点“审计签名密钥托管化 + 丢失告警/自动恢复”
> 的本地可落地部分：健康诊断、恢复/轮换操作流程与归档纪律。
> 正式密钥托管与独立审计节点仍需批准密码产品/受控密钥介质（另行决策）。

## 1. 为什么需要这份手册

审计封存（`loop/tool-audit.jsonl` + `loop/audit-head.json` + `.p7s`）由
`loop/audit-signing.json` 中钉扎的一个 **CurrentUser/My 非导出 CodeSigning 证书** 签名。
该证书是质量门禁 preflight 的单点故障：证书丢失/更换机器后任何
`make quality` 都会以 `exit=14` 失败（历史教训：F713 私钥丢失事件）。

诊断入口（任何门禁异常前先跑）：

```powershell
python scripts\audit_key_health.py
```

输出结构化 JSON：逐项检查（配置结构 / 公钥文件哈希 / 链头签名者归档 / 证书 Inspect）、
问题清单与对应处置建议；退出码 0=健康，1=存在需处置的问题。

## 2. 检查项

| 检查 | 含义 | 失败影响 |
|---|---|---|
| config.structure | 配置字段/thumbprint/哈希/算法字段合法 | 门禁 preflight 不可用 |
| config.public_certificate | `loop/audit-signing-public.cer` 存在且哈希匹配 | 不可验签/签名 |
| config.head_signer | 当前链头签名者 = 配置，或存在 `audit-signing-<THUMB>.json` 归档 | 历史链无法复核 |
| certificate.inspect | 证书在 CurrentUser/My、恰好 1 个、有私钥、不可导出、在有效期内 | 不可签名/续封 |

## 3. 恢复流程（按故障类型）

### 3.1 证书丢失/被卸载（CurrentUser/My 中找不到）

1. 确认机器上是否仍有不可导出的旧证书（`certmgr.msc` → 个人 → 证书）；
2. 若确认丢失，**先备份** `loop/audit-signing.json` 与 `loop/audit-signing-public.cer`；
3. 重建新签名者：`scripts\audit_signature.ps1 -Action Initialize`
   （生成新非导出证书与新的公钥文件）；
4. 若历史链头签名者 ≠ 新配置，按 §4 为历史签名者补档归档；
5. 重跑 `python scripts\audit_key_health.py` 确认全绿后，再跑门禁。

### 3.2 配置损坏/字段错误

1. 依据 `audit_key_health.py` 的 `problems` 字段逐项修正
   `loop/audit-signing.json`；
2. 公钥文件哈希必须与配置一致；不一致时以实际文件哈希回写配置（先留备份）。

### 3.3 私钥可导出（pfx_exportable=true）

**立即停用**：可导出的私钥不满足不可抵赖性要求，不允许用于审计签名。
按 §3.1 重建非导出证书并轮换签名者。

### 3.4 链头签名者与配置不一致（历史归档缺失）

`audit_key_health.py` 会给出缺失的归档文件名 `audit-signing-<THUMB>.json`；
恢复该签名者当时的配置内容（thumbprint/公钥路径/哈希/算法字段）补档即可
恢复历史链复核能力。

## 4. 轮换与归档纪律

- 每次轮换签名者，保留旧签名者的 `audit-signing-<THUMB>.json` 归档于 `loop/`；
- `loop/audit-signing.json` 只指向当前签名者；历史归档用于跨签名者复核；
- 公钥证书与配置均为非敏感元数据，可入库；**私钥永不入库、不入日志、不进模型上下文**；
- 备份：`loop/audit-signing.json` + `loop/audit-signing-public.cer` + 全部
  `loop/audit-signing-<THUMB>.json` 归档 + `loop/audit-head.json`/`.p7s`。

## 5. 升级路径与决策点

- 当前原型使用 RSA-3072/SHA-256 开发证书；正式环境必须替换为**批准的 SM2 密码产品
  与受控密钥介质**（`loop/audit-signing.json` 的 `formal_replacement` 字段已声明）；
- 独立审计节点同步（日志检查点异地留档）需业务负责人与安全保密管理员决策；
- 本手册不改变密码方案，仅为原型密钥的可运维性提供诊断与恢复手段。

## 6. 密钥托管方案（PRODUCT-REVIEW T-07，2026-08-12）

目标：把审计签名密钥从"维护机 `CurrentUser/My` 非导出证书"升级为受控托管形态，
消除单机单点故障。托管形态三档：

| 档位 | 形态 | 适用阶段 | 前置 |
|---|---|---|---|
| A（当前） | 维护机非导出证书 + 归档纪律 | 原型/试点 | 已具备 |
| B | 受控密钥介质（USB-Key/HSM/SKF 适配）承载 SM2 审计私钥 | 试点后 | 批准密码产品（US-5-AC-2） |
| C | 独立审计节点异地留档（日志检查点 + 密钥分离） | 生产 | 安全保密管理员决策 |

落地步骤（B 档，密码产品批准后）：

1. `audit_seal.py` 签名路径接入受控句柄（与 `crypto/` 受保护层同契约），私钥字节
   不进入 Python/日志/模型上下文；
2. `loop/audit-signing.json` 增加 `custody` 字段（`machine|token|hsm`）与介质
   指纹，`audit_key_health.py` 按该字段校验介质在位/可签名；
3. 轮换与归档纪律（§4）保持不变，多介质轮换按 §3.4 补档。

健康检查覆盖：`audit_key_health.py` 新增 `custody` 检查项（B/C 档生效），
介质缺失/不可签名按 §3.1 恢复流程处置（先备份公钥与配置，再重建/轮换）。
