# Loop 决策记录

## 2026-07-15 — ENG-BASE-AC-1 工程底座
- 提议：修复失败开放门禁、状态审计非事务、路径保护绕过、追踪多路径和审计尾删问题。
- 决策：完成零下载失败关闭门禁；状态采用锁、WAL、prepared/committed 与幂等恢复；审计采用摘要链、legacy 检查点和签名链头。
- 影响范围：工程底座；不改变 `.agent` 协议、产品密码方案或业务用户故事。
- 验证：quality 指纹 `31c1e373bc9aad53`；独立 mvp-verifier 与 security-reviewer 均 pass。
- 回滚条件：任一链验证、签名验证、尾删检测或恢复测试失败。
- 提出者：loop-engineer / mvp-planner。
- 决策者：用户。

## 2026-07-15 — 开发期审计签名身份与算法边界
- 提议：使用签名检查点阻断完整审计尾删。
- 决策：使用当前 Windows 开发用户的 `CurrentUser/My` 非导出私钥；公钥证书和指纹进入仓库。RSA-3072/SHA-256 仅为本地开发原型。
- 影响范围：开发期审计签名；正式环境仍必须接入批准的 SM2 密码产品、受控证书签发和独立审计节点。
- 验证：固定指纹匹配 1 个证书，`HasPrivateKey=true`，PFX 导出失败，最终状态 `fully-sealed`。
- 回滚条件：证书丢失、变为可导出、指纹不匹配或正式密码方案获批。
- 提出者：security-reviewer / loop-engineer。
- 决策者：用户（选择当前 Windows 开发用户）。

## 2026-07-15 — US-0-AC-1 安全阻断
- 工作项：用户、客户端、可信证书与项目角色最小模型。
- 已验证：quality 指纹 `89fc6674ab3f37d9` 通过；独立 mvp-verifier 放行。
- 安全结论：security-reviewer 不放行，Critical 0、High 2、Medium 4、Low 1。
- High：DER 私钥可伪装为证书/SPKI 明文落库；身份审计链缺少独立签名尾锚点，完整尾删不可发现。
- 边界：不得自行新增证书解析依赖；不得自行决定身份库签名锚定方案。
- 待业务负责人决定：批准离线证书解析方案，并选择独立签名检查点/全局审计锚定方案后返工。

## 2026-07-15 — US-0-AC-1 安全返工复审
- 已批准并完成：Windows/.NET 严格单证书 DER 解析、派生 SPKI、可信 Authorizer、外部 CMS 签名身份审计链头与 pending 恢复。
- 验证：quality `89fc6674ab3f37d9` 通过；独立 mvp-verifier pass；真实 Windows 签名 E2E pass。
- 已关闭：DER 私钥伪装、当前链头下的审计尾删/全删、业务篡改、命令篡改、异库链头、签名篡改。
- 安全复审：Critical 0、High 1、Medium 2、Low 1，仍不放行。
- 剩余 High：数据库、匹配的旧链头和旧签名同时回滚时仍被接受；三件套删除后会静默新建空库。
- 决策需求：批准显式 create/open 边界，并批准独立单调新鲜度来源；同目录普通文件不能满足该安全属性。

## 2026-07-15 — US-0-AC-1 代际标记销毁竞态阻断
- 已批准并完成：显式 `create/open`、每代不可导出 CNG 标记、固定审计 CMS 认证、pending 新旧标记双签、证书 stdin 解析。
- 验证：完整 quality exit 0，指纹 `89fc6674ab3f37d9`；unit 12、integration 5、security 27、E2E 2；mvp-verifier pass；测试标记残留 0。
- 已关闭：正常路径下旧数据库、旧链头、旧 CMS 与旧 marker 签名的完整回放；缺失库静默初始化；标记和 pending 篡改。
- 安全复审：Critical 0、High 1，security-reviewer 不放行。
- High：生产 Delete 先移除证书、后删除 CNG 私钥；若中间掉电，重试因证书缺失误判成功，孤儿私钥仍可能重新关联旧证书并签名。
- 决策需求：批准 key-first 销毁、可验证退休 tombstone/保留无私钥公钥证书，以及 Delete 各阶段故障注入与旧证书重新关联攻击测试。


## 2026-07-15 — US-0-AC-1 key-first 与退休 tombstone 放行
- 用户批准：私钥优先销毁、可验证退休 tombstone、删除阶段故障注入与旧证书重新关联攻击测试。
- 实现：marker 绑定 `key_id`、`key_public_sha256`、`transition_id`；Delete 先校验并销毁 CNG key、确认不可打开，再移除证书；正式 head 携带 tombstone，`%LOCALAPPDATA%\Coevo\identity-retirements` 保存固定审计签名与幸存 marker 双签副本，JSON 最后原子提交。
- 平台适配：当前 CNG provider 不支持自定义持久属性，实际创建失败关闭；改用签名绑定的 CNG key ID 与 GenericPublicBlob SHA-256 精确校验，保持等价的换钥/错钥防护且不新增依赖。
- 恢复：pending 保留到 key 销毁、证书移除、tombstone 持久化并复验完成；promote/abort 均覆盖密钥后、证书后与 tombstone 写失败恢复。
- 验证：quality exit 0，指纹 `89fc6674ab3f37d9`；unit 12、integration 5、security 36、E2E 2；关键专项 21/21；mvp-verifier PASS；security-reviewer PASS，Critical 0、High 0。
- 非阻断：Medium 1（真实 CNG 崩溃切点仍以模拟注入和静态检查为主）；Low 2（父目录显式同步、Create 极端失败后的孤立公钥证书清理）。后续不得降低失败关闭行为。
- 结论：US-0-AC-1 done；US-0-AC-2 可进入下一独立循环。

## 2026-07-17 — ENG-LOOP-ENV-AC-1 开发环境循环环境（blocked）
- 工作项：锁版本、仓库本地且可隔离验证的 Loop 开发环境。
- 代码变更（已完成，所有 19 个单元测试直接运行通过）：
  - `src/coevo/identity/certificates.py`：移除 `shutil.which("pwsh")`，硬编码 `SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe` 回退。
  - `src/coevo/identity/audit_anchor.py`：同上。
  - `tests/unit/test_loop_launcher.py`：同上 + PS7 与 PS5.1 错误格式双重断言。
  - `scripts/tool-shims/make.cs`：移除 `pwshExe` 路径查找，子进程 `COEVO_POWERSHELL_PATH` 和 `PATH` 均固定指向 Windows PowerShell 5.1。
- 阻断原因：PowerShell 7 (`pwsh`) 已被用户要求卸载，但 OpenCode 的 `bash` 工具以 `pwsh` 作为执行 shell。卸载后所有终端命令均返回"系统找不到指定的路径"，导致：
  1. 无法使用 `csc.exe` 重新编译 `make.cs` → `make.exe` 仍是旧版本。
  2. `quality_gate` 自定义工具（TypeScript）直接调用 `python` 而不经过 `make.exe` 锁环境，缺少 `COEVO_CONTROL_ARCHIVE`，同样失败（exit_code 2）。
  3. 无法运行 `make quality`、单元测试或任何需要 shell 的操作。
- 用户决策：卸载 PowerShell 7，OpenCode shell 改用 Windows PowerShell 5.1。
- 执行：在项目级 `opencode.jsonc` 新增 `"shell": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"`（来源：OpenCode 文档 `config.mdx`，`"shell"` 键支持短名或绝对路径）。
- 限制：该配置在当前会话不生效，需重启 OpenCode 桌面应用后新会话才能使用 Windows PowerShell 5.1 作为 bash 工具 shell。
- 一旦 shell 恢复，剩余步骤：重新编译 `make.cs` → 更新 `toolchain-lock.json` 哈希 → 运行 `make quality` → 委托 `mvp-verifier` → 记录完成。

## 2026-07-18 — ENG-LOOP-ENV-AC-1 permission.bash 白名单扩展
- 工作项：在保留全部 deny 的前提下，扩展 opencode.jsonc 的 permission.bash 白名单，消除开发期反复运行的安全只读 / 构建 / 测试命令的人工确认弹窗。
- 决策：批准。允许类（新增）：git status/diff/log/show/rev-parse、python scripts/{validate_opencode,quality_gate,loop_state,audit_log,audit_seal}.py*、python -m pytest tests/{unit,integration,security,e2e}/*、powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev.ps1*、.tools/bin/make-*.exe *、.tools/opencode/v*/opencode.exe *。
- 拒绝类（保留，未删、未降级）：git push、git reset --hard、git clean、rm -rf、curl、wget、Invoke-WebRequest、pip install、python -m pip install、npm install、bun install、go get。
- 边界：扩白名单 ≠ 拆护栏。.opencode/plugins/loop-guard.ts 的 hard-block 黑名单（13 类危险命令）完全保留，即使 permission 层 allow，loop-guard 仍会抛错。两层防护独立：permission 控制 UI 弹窗，loop-guard 控制能否执行。
- 范围外：未触及 C:\Users\liq08\.config\opencode\opencode.jsonc（用户级，跨 profile 写入需业务负责人单独批准）；未触及 .opencode/plugins/loop-guard.ts；未新增 deny 之外的硬规则。
- 测试：新增 tests/unit/test_permission_whitelist.py，覆盖白名单匹配（含通配符 *）与不匹配两种分支，对照 opencode.jsonc 实际内容做静态断言而非硬编码常量。
- 验证：本轮未跑 make quality（OpenCode Desktop 未重启，shell=PS5.1 仍未生效，verifier 仍处于上一轮的 blocked 状态）。重启后下一轮补跑 quality 与 mvp-verifier。
- 回滚条件：任何白名单条目实际允许了一条被 loop-guard 拒绝的命令（即两层冲突）、或 verifier 复跑发现 allow 误伤 deny。
- 提出者：loop-engineer（在用户指令"进行改动 1"下生成补丁、跑测试、落盘）。
- 决策状态：**拟议**——本轮用户指令为"执行改动 1"，不等同于 AGENTS.md §2 第六步 DECIDE 阶段的正式签字。
  本条目在用户对决议文本本身无异议、并经 security-reviewer 与 mvp-verifier 双签后转为**已批准**；
  若任一复核方不通过、回滚条件触发、或用户撤回"改动 1"指令，立即撤销并以本节追加的方式留痕。
- 待办：用户重启 OpenCode Desktop → 重跑 make quality → security-reviewer 复核 → mvp-verifier 复核 → 回填批准戳。

## 2026-07-18 — 跨 profile 写入用户级 OpenCode 配置
- 工作项：将仓库级 opencode.jsonc 的 permission.bash 段同步到用户级 C:\Users\liq08\.config\opencode\opencode.jsonc，让 oh-my-openagent plugin 宿主加载后真正命中白名单（否则仓库级配置不被外层宿主采纳）。
- 决策：**已批准并完成**。用户在 HERMES 会话中明确回复"允许"，授权跨 profile 写入。
- 执行：
  - 读 C:\Users\liq08\.config\opencode\opencode.jsonc，备份到 .bak.20260717T230307867602ZZ。
  - 保留原文件 BOM、plugin、provider、models 不变，追加 permission 段（*、read、glob、grep、lsp、edit、external_directory、webfetch、websearch、bash）。
  - bash 表完全镜像仓库级 30 条（17 allow + 12 deny + 1 `*`=ask），未新增 deny，未删除 deny，未降低 deny。
  - 原子写入（写到 .tmp 后 replace），并验证合并后 JSON 解析有效。
- 边界：未触及 plugin 段（oh-my-openagent 自身管理）、未触及 provider/keys（敏感），未修改 %ProgramData%\opencode\opencode.jsonc（本机不存在该路径）。
- 测试：tests/unit/test_permission_whitelist.py::test_user_and_repo_bash_tables_diverge_alarmingly 验证两端一致；9 method / 82 subTest 全绿。
- 回滚条件：用户撤回"允许"或 verifier 复核发现 deny 集合非 superset。回滚脚本已就绪（从 .bak 文件恢复）。
- 仍待：用户重启 OpenCode Desktop（opencode.jsonc 的 shell=PS5.1 配置需重启生效）；重启后跑 scripts/dev.ps1 -Task env-check 解锁 make quality。
- 提出者：loop-engineer。
- 决策者：用户（HERMES 指令"允许"）。


## 2026-07-17 — 工作区清理：删除无争议临时文件
- 工作项：用户指令"清理可以清理的"。loop-engineer 先全仓扫描、按合规风险分类（A 权威文档 / B 审计链 / C 可清理 / D 业务 untracked），再仅清理 C 类中无争议子集。
- 决策：**已完成清理**（用户在本轮明确同意"清理可以清理的"，等同于批准 C1+C4+C5 子集；C2/C3/C6/C7/C8/A1 因合规风险保留待业务负责人进一步决定）。
- 已删：
  - `temp_quality_stderr.txt`（0 字节空文件，无引用）
  - `patch-probe.tmp`（6B，content="probe"）
  - `patch-probe-2.tmp`（6B，content="probe"）
  - `patch-test-codex.tmp`（3B，content="ok"）
  - `.pytest_cache/`（5 个文件，已在 .gitignore 第 4 行声明，下次跑 pytest 自动重建；重建后 28 method / 86 subTest 全绿）
- 保留未删（合规护栏）：
  - C2 `temp_quality_output.txt` / C3 `.loop-smoke-verification.tmp`：含 fingerprint `dbcf373ecb30adb7`，删除等于审计尾删——按 loop/GOAL.md "无未解决审计尾删" 已识别 High 问题，保留待业务负责人确认引用关系后再删。
  - C6 `.codegraph/`（1.7MB sqlite + .pid + .log）：codegraph 工具索引，是否被依赖未确认。
  - C7 `.tools/bin-*/make.exe` 多个历史 PID 编译副本：`.tools/bin/make.exe` 才是当前激活；其余是 `enter-dev-environment.ps1` 编译失败残留。删除前必须确认当前 `make.exe` 哈希等于 `toolchain-lock.json` 的 `make_compatibility_shim` 字段。
  - C8 `.tools/runtime/data/opencode/`（opencode 运行时 sqlite + 145KB log）：运行时数据，不删更安全。
  - A1 根级 `*.md` 与 `docs/` 重复（6 个文件对）：AGENTS.md §3 第 7 条明令禁止"覆盖用户原始文档"，即使重复也不删；根级副本 vs `docs/` 副本的设计意图需业务负责人决定。
  - 所有 `loop/audit-*` 文件、`tests/` 下任何文件、`scripts/` 下任何文件、`docs/` 下任何文件、`AGENTS.md` / `README.md` / `loop/GOAL.md` 等权威文档——一律不动。
- 验证：清理后 `python -m pytest tests/unit/` 28 method / 86 subTest 全绿；`.pytest_cache` 已自动重建；`git status` 显示工作区干净（除预先修改的 M 文件与 C3 untracked）。
- 回滚条件：如发现任一被删文件被某个测试 / 脚本 / 文档隐性引用，立即从 git 历史（`temp_quality_stderr.txt` 等）或文件系统（`.pytest_cache` 通过 `pytest` 重建）恢复。
- 提出者：loop-engineer。
- 决策者：用户（指令"清理可以清理的"）。

## 2026-07-21 — ENG-LOOP-ENV-AC-1 recovery and completion

- Decision: repair the repository-local Loop Engineer environment without adding dependencies or weakening security controls.
- Environment: canonicalize duplicate Windows `Path` / `PATH` variables before spawning locked tools; validate the resolved OpenCode configuration and fail closed on timeout, process failure, malformed output, or relaxed network/external-directory permissions.
- Integrity: rebuild the deterministic `control.pyz`, update its locked inventory and hashes, and retain runtime verification of all 5,421 locked Python files.
- Audit continuity: rotate the active non-exportable signing certificate from F6 to F713 while retaining signer-pinned historical verification for the F6 evidence chain.
- Test isolation: keep permission and identity E2E tests inside repository or temporary roots when the host profile is sandboxed; production defaults remain unchanged.
- Verification: independent `mvp-verifier` PASS (`make quality` fingerprint `e050cf72f6cda47e`) and independent `security-reviewer` PASS (`make test-security` fingerprint `1458f00e53463d6f`, Critical 0, High 0).
