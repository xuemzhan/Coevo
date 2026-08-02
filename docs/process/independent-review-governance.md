# 独立双签治理：只读审查沙箱

> 状态：生效（2026-08-02）。历史教训：2026-08-02 首次恢复独立双签时，子代理曾在主工作树内直接修改并提交源码/记录，security-reviewer 还擅自派生子代理——审查独立性被破坏。本策略即针对该事件固化治理。

## 1. 目的

满足 AGENTS.md 完成定义中的“独立 mvp-verifier 与（必要时）security-reviewer 双方均放行”，且保证：

- 审查者在**不可变快照**上工作，主工作树全程只读；
- 任何试图修改被审对象（源码/测试/脚本/文档）的行为都会被守卫捕获并使该轮审查作废；
- 审查有明确时限，超时即中断并按“未放行”处理；
- 只有通过守卫校验的报告才能写入正式记录。

## 2. 角色

| 角色 | 职责 | 放行标准 |
|---|---|---|
| independent verifier | 在被审提交的隔离沙箱内执行完整质量门禁（`make quality`），复核追溯矩阵与审计链 | exit=0、指纹与仓库既有锁定基线一致、审计链 fully-sealed |
| security-reviewer | 对密码/协议/鉴权/路径/审计链/私钥处理做安全审查，可只读运行安全测试子集 | 无未解决的 Critical/High；输出四档计数与证据 |

审查报告只能以**最终回复文本**交付，禁止以文件形式落盘（防注入正式记录）。

## 3. 沙箱生命周期（由编排者执行）

所有命令均只读写 `loop/runtime/review-sandboxes/`（gitignored），不触碰主工作树：

```text
python scripts/review_sandbox.py prepare --name <name> --role verifier|security-reviewer [--ref <commit>]
python scripts/review_sandbox.py check   --name <name>      # 0=通过, 2=违规, 3=缺失
python scripts/review_sandbox.py discard --name <name>
```

`prepare` 用 `git clone --no-hardlinks --no-local` 建立隔离副本并 `checkout --detach` 钉扎提交，同时生成 pin 清单（HEAD + 保护路径清单的 SHA-256）。保护范围：**除 `loop/` 外的全部已跟踪路径**；`loop/` 是质量门禁合法副产物区（VERIFICATION.md、tool-audit.jsonl、audit-head.*）。

`check` 校验三件事：

1. 沙箱 HEAD 仍等于钉扎提交（禁止新增提交）；
2. 保护路径清单与 pin 一致（禁止任何编辑/新增/删除/重命名）；
3. porcelain 状态中非 `loop/` 变更列表为空（忽略 gitignored 的 `.tools/`、`loop/runtime/`、`__pycache__/` 等）。

`loop/` 内的变动作为证据输出（`loop_delta`），不作为放行依据；审计链与 VERIFICATION 证据以主仓库最终门禁为准。

## 4. 只读契约（审查者必须遵守）

审查者收到的任务包必须包含以下约束：

- 只允许在指定沙箱路径内活动；**禁止**读写主工作树（`E:\Workspace\Coevo` 下除沙箱外的任何路径）；
- 禁止 `git add / commit / reset / checkout / stash / rebase / filter-branch / push`；
- 禁止编辑 `src/ tests/ scripts/ docs/ Makefile` 及任何非 `loop/` 文件（verifier 执行门禁导致的 `loop/` 追加除外）；
- 禁止运行网络、安装、下载类命令；禁止生成文件型报告；禁止派生子代理；
- 发现缺陷只报告、不修复（修复是 loop-engineer 的下一个循环的职责）；
- 超时上限：25 分钟，超时由编排者中断，报告按 UNKNOWN/FAIL 处理。

## 5. 违规处理

- `check` 返回违规（exit 2/3）或超时未完成：报告作废，不写入正式记录；沙箱立即 `discard`；
- 违规事件写入 `loop/DECISIONS.md` 与 `loop/tool-audit.jsonl`；
- 同一提交连续 3 次未通过独立双签 → 触发 AGENTS.md 停止条件（同一错误连续出现 3 次），停轮请业务负责人决策。

## 6. 放行与记录

双签放行后的记录步骤（仍由 loop-engineer/编排者执行）：

- 两份报告原文（含审查者身份、时间、结论）追加至 `loop/VERIFICATION.md`；
- 追溯矩阵新增/更新行并标注双签状态；
- `loop/STATE.json` 更新（iteration、current_item、phase=decide、status=done）；
- 主仓库最终 `make quality` exit=0 后提交记录。

## 7. 环境说明

沙箱内无 `.tools/`（gitignored）：编排者在 prepare 后以目录联接（junction）挂载主仓库 `.tools/` 与 `loop/runtime/`，二者均为只读工具链/运行时材料，不属于被审对象；守卫因 gitignore 规则不会将其列为变更。实机审查命令使用固定环境变量：

```text
COEVO_REPO_ROOT=<sandbox>
COEVO_NODE_PATH=E:\Workspace\Coevo\.tools\node\24.14.0\node.exe
COEVO_CONTROL_ARCHIVE=E:\Workspace\Coevo\.tools\control\control.pyz
PYTHON=E:\Workspace\Coevo\.tools\python\3.14.3\python.exe
```

