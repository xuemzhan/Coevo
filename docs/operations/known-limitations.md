# 已知限制与外部依赖清单（RELEASE-1）

> 状态：生效（2026-08-04）。发布/交接前必读。本清单记录当前 MVP 已知限制、
> 外部依赖与尚未落地的事项，避免把"已实现"误认为"可无条件生产"。

## 1. 外部条件（未落地，需业务/环境决策）

| 事项 | 状态 | 影响 | 前置 |
|---|---|---|---|
| 国密认证模块（SKF/PKCS#11/硬件令牌） | 未落地 | 受保护密钥句柄为软件 KSP 实现（CNG KEK 封装），非认证模块 | 外部采购；适配契约与受保护层已就绪 |
| Win7 存量环境实机验证 | 未落地 | `win7-compat` 分支仅静态专项，未实机验证 | 存量 Win7 环境 |
| CI 激活 | 未落地 | `.github/workflows/quality.yml` 已入库但未激活 | 所有者发布工具链制品、回填 `ci-artifact.json` 哈希、推送工作流 |
| 审计签名密钥托管 / 独立审计节点 | 未落地 | 审计封存仍依赖维护机 `CurrentUser/My` 非导出证书 | 批准密码产品/受控密钥介质（见 audit-key-runbook） |
| Windows 服务形态 | 未落地 | 自启为计划任务（登录触发），非服务（服务需管理员与 SCM 集成） | 若需常驻服务另行决策 |

## 2. 已知实现边界

- **解释器路径已固化（OPS-2）**：安装/注册会把绝对解释器路径写入
  `<install_root>\python-path.txt`（`install_cockpit.py` 与
  `register-autostart.ps1` 的 `Register`/`PinPython`），看门狗按
  显式 `-PythonPath` → sidecar → PATH 解析；sidecar 缺失、非绝对路径或指向
  不存在的解释器时失败关闭。OPS-5 起 `install_cockpit.py --action check` 强制
  校验 pin（缺失/空/非绝对/目标缺失即 check 失败），`health_check.py` 增加
  `pin` 检查（degraded）；旧安装（升级前未写过 sidecar）需先执行一次
  `register-autostart.ps1 -Action PinPython`（或重跑 `Register`）才能通过
  install check。
- **备份默认位于安装根内**（`backups/`，与数据同卷）：BACKUP-2 起支持
  `--backup-root` 指向外部磁盘/共享并用 `--require-external` 强制异卷（同卷或
  在安装根内时失败关闭）；manifest 记录 `same_volume` 供自动化核查。异地拷贝
  仍是部署责任；密钥句柄/私钥不随备份（按身份库/密钥手册处置）。
- **`secret_scan` 为高置信启发式**：覆盖主流私钥/令牌格式，不替代人工代码审查；
  新增密钥格式需扩展模式清单。
- **`request_count` 仅统计认证请求**：未认证探测不计入（已文档化）。METRICS-2
  起 `/api/health` 增加 `probe_count` 单独统计 `/healthz` 存活探测，运维可区分
  看门狗/健康检查流量与真实使用。
- **访问日志轮转备份为明文**：与源同密级，轮转文件注意归档权限。
- **模型外发审批以配置文件为准**：`COEVO_LLM_EXTERNAL_DATA_OK` 仅为直接构造
  provider 时的兼容开关（见 configuration-reference）。
- **原型密码路径（GmSSL 3.2.0 + 纯 Python SM3）**：真实算法、开源引擎、受保护
  句柄层已落地，但非国密认证模块（见 §1）。

## 3. 维护注意

- 门禁指纹随 lint 命令集变化（如新增 secret_scan 后 `34fc0b6`→`e3a61c2`）；发布
  记录必须引用**实际运行**的指纹。
- 锁定文件（python-script-lock.tsv、toolchain-lock.json、make.cs）任何编辑都必须
  全链同步哈希，否则环境入口/门禁失败关闭。
- 新增 `COEVO_*` 环境变量必须登记 `configuration-reference.md`（有测试校验）。
