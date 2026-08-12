# CI 与制品托管方案（CI-1）

> 状态：方案生效（2026-08-03，业务负责人批准 CI/制品托管方案）。
> 状态更新（2026-08-04，CI-2）：制品已在维护机本地构建并回填
> `ci-artifact.json`（version=1.0.0，sha256=e679aec3…，2026-08-12 起构建脚本
> 时间戳归一化、字节级可复现），工作流已随 main
> 推送。剩余激活前置：所有者创建 `toolchain-1.0.0` GitHub Release 并上传
> `coevo-toolchain-win64-1.0.0.zip`（见 §5）。

## 1. 目标

在 GitHub Actions（Windows runner）上自动运行 Coevo 的**验证侧**质量门禁
（fmt / lint / test / test-security / test-e2e），每次提交或 PR 均可复现，
并把门禁证据（VERIFICATION.md、审计链）作为制品归档。

## 2. 制品托管（锁定工具链）

仓库的 `.tools/`（锁定 CPython 3.14.3、Node 24.14.0、GmSSL 3.2.0、
`control.pyz` 等）是门禁运行的必要条件，但不进入 Git。CI 通过
GitHub Releases 托管一个内容寻址制品：

| 项 | 值 |
|---|---|
| 制品名 | `coevo-toolchain-win64-<version>.zip` |
| 发布标签 | `toolchain-<version>`（与 `docs/dependencies/toolchain-lock.json` 的版本对应） |
| 内容 | 仓库 `.tools/` 目录（排除 `.tools/runtime`、`.tools/bin-*`、下载缓存） |
| 哈希锚定 | `docs/dependencies/ci-artifact.json` 的 `sha256` 字段（64-hex） |
| 下载 | 仅 https，GitHub Releases |

制品构建命令（在维护机执行，可复现）：

```powershell
python scripts\ci-build-toolchain.py --version 1.0.0
```

脚本输出路径、文件数与 SHA-256（已回填至 `ci-artifact.json`）。

> **可复现性（MATURITY-O-02，2026-08-12）**：`ci-build-toolchain.py` 对 zip
> 条目时间戳归一化（固定 1980-01-01），同一 `.tools` 内容无论何时何地构建，
> SHA-256 恒定。若 `.tools` 内容有变动（工具链升级），必须重建制品并同步刷新
> `ci-artifact.json` 的 `version/sha256` 后再发布。

```powershell
Get-FileHash .\coevo-toolchain-win64-<version>.zip -Algorithm SHA256
```

## 3. 恢复流程（fail-closed）

`scripts/ci-restore-toolchain.ps1`：

1. 读取 `docs/dependencies/ci-artifact.json`（可用 `-ArtifactUrl/-ArtifactSha256` 覆盖）；
2. `sha256` 为 `pending` 时**拒绝运行**（制品未发布/未锚定则 CI 不启动）；
3. 下载（仅 https）或使用 `-LocalPath`（测试注入）；
4. 计算归档 SHA-256，与锚定值不一致立即失败（不解压）；
5. 先解压到临时目录，校验 `python.exe`/`node.exe`/`control.pyz` 存在且
   仓库 `toolchain-lock.json` 可解析，再整体复制进 `.tools/`；
6. 失败时清理临时目录，不留半成品。

## 4. 门禁边界（审计封存留在维护机）

`make quality` 的**签名封存**需要 `CurrentUser/My` 中不可导出的审计签名私钥，
该密钥不能上传到 runner（违反非导出原则）。因此：

- CI 运行全部验证侧目标：`fmt`、`lint`、`test`、`test-security`、`test-e2e`
  （lint 内含 `audit_log verify` 与 `audit_seal verify`，均只用公钥，可在 runner 复验
  既有审计链）；
- `--target quality`（含签名封存）由维护机本地执行，产生带签名的最终指纹；
- CI 证据与本地封存指纹共同构成双重证据，`loop/VERIFICATION.md` 由本地门禁追加。

## 5. 激活步骤（需要仓库所有者操作）

1. 构建并发布 `coevo-toolchain-win64-<version>.zip` 到 `toolchain-<version>` 标签；
2. 回填 `docs/dependencies/ci-artifact.json` 的 `version/url/sha256`；
3. 推送 `.github/workflows/quality.yml`（当前仓库规则禁 push，需所有者执行）；
4. 首次运行验证：观察 restore 步骤哈希校验与四个门禁目标；
5. 每次工具链升级：重建制品 → 更新版本/哈希 → 推送。

## 6. 安全说明

- 制品只含锁定工具链，无密钥/口令；哈希锚定保证内容不可被替换；
- runner 权限 `contents: read`（只读）；
- 门禁不联网下载运行时（制品由 CI 恢复，本地/生产运行仍零下载）；
- 若制品哈希被篡改，restore 步骤失败关闭，CI 红。
