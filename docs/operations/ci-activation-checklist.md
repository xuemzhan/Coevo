# CI 激活执行单（MATURITY O-02，2026-08-12 就绪）

> 用途：把 CI 激活从"待 owner 操作"变成可逐项打勾的执行单。所有代码侧前置
> （工作流、制品描述符、恢复脚本）已就绪并验证；本文只记录仓库所有者需要执行的
> 动作与验收命令。

## 1. 当前就绪状态（已核实）

| 项 | 状态 | 证据 |
|---|---|---|
| `.github/workflows/quality.yml` | 已入库（验证侧四目标 fmt/lint/test/test-security/test-e2e + 制品证据上传 + 失败即红） | 随 main 推送 |
| `docs/dependencies/ci-artifact.json` | **已锚定**（version=1.0.0，sha256=`e679aec38727eadd07683cd809b3e0bb19ee8c248d35a306261502fde652d6d9`，url 已填，非 pending） | 描述符 |
| `scripts/ci-build-toolchain.py` | **可复现构建**（2026-08-12 修复：zip 时间戳归一化，两次重建哈希一致 `e679aec3…`） | 复现性回归测试 `test_ci_restore.py::test_build_archive_is_byte_reproducible` |
| `scripts/ci-restore-toolchain.ps1` | fail-closed：https-only、哈希不符不解压、staging 校验、失败清理 | 脚本 |
| 审计封存边界 | CI 只跑验证侧；`--target quality` 的签名封存保留在维护机（非导出私钥不上 runner） | `ci-artifact-hosting.md` §4 |

## 2. 需要仓库所有者执行的动作

- [ ] 1. 在维护机构建制品（如尚未生成）：
      `python scripts\ci-build-toolchain.py --version 1.0.0`
      （构建脚本已字节级可复现；若 `.tools` 内容变更，重建后必须先更新
      `ci-artifact.json` 的 `sha256` 再发布）
- [ ] 2. 在 GitHub 创建标签 `toolchain-1.0.0`，上传制品
      `coevo-toolchain-win64-1.0.0.zip`（名称必须与描述符 `url` 一致）；
- [ ] 3. 上传后用维护机核对：
      `Get-FileHash .\coevo-toolchain-win64-1.0.0.zip -Algorithm SHA256`
      结果必须等于描述符 `sha256`；
- [ ] 4. 推送 `.github/workflows/quality.yml` 与 `docs/dependencies/ci-artifact.json`
      （推送按仓库授权流程单独确认）；
- [ ] 5. 触发一次 `workflow_dispatch`，观察：
      - restore 步骤：`toolchain restored: ... (sha256=81dd3e7d…)` 且无哈希报错；
      - fmt / lint / test / test-security / test-e2e 五个作业全绿；
      - `coevo-gate-evidence` 制品包含 VERIFICATION / tool-audit / audit-head。

## 3. 首次运行验收标准

- restore 失败关闭（哈希不一致 → 作业红，且不解压）；
- lint 内含 `audit_log verify` + `audit_seal verify`（公钥复验既有审计链）通过；
- 验证侧测试计数与本地一致：单元 1607 / 集成 273 / 安全 103 / E2E 25 / Win7 4
  （以当时 HEAD 实际计数为准）；
- 本地 `make quality` 指纹（维护机）与 CI 验证侧结果共同构成双重证据，记录进
  `loop/VERIFICATION.md`。

## 4. 完成后的收口动作

1. 在 `loop/DECISIONS.md` 记录 CI 首次全量绿 + 制品哈希；
2. `known-limitations.md` 的 CI 行状态更新为"已激活"；
3. `external-gates.md` / 计划文档 O-02 标记 done；
4. 工具链升级流程：重建制品 → 更新 `ci-artifact.json` 版本/哈希 → 推送。
