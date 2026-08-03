# Custom Tools（领域化 Tool，非万能 Shell 包装）

> 配置建议第八节明确警告：**不要把任意 Shell 执行封装成 Custom Tool**，否则会绕开已建立的权限边界。本目录下的 3 个 Tool 是状态/证据的领域化读写器，调用前必须先经过 `bash.*` 权限白名单。

| Tool | 作用 | 实现位置 | 调用方式 |
|---|---|---|---|
| `loop_state` | 原子更新 `loop/STATE.json`（带文件锁 + 备份） | `tools/loop_state.ts` → `scripts/loop_state.py` | `python scripts/loop_state.py <args...>` |
| `quality_gate` | 实际执行受控门禁并生成 `VERIFICATION.md` 行 | `tools/quality_gate.ts` → `scripts/quality_gate.py` | `python scripts/quality_gate.py` |
| `traceability_check` | 检查 AC ↔ 测试 ↔ 代码映射完整性 | `tools/traceability_check.ts` → `scripts/traceability_check.py` | `python scripts/traceability_check.py` |

每个 Tool 都遵循同样的边界：

- 单一职责，只读写一个文件或一类证据，不接受任意 shell 命令。
- 写入失败必须回滚（已写一半也要撤销）。
- 输出 JSON 格式，且必含 `timestamp`、`actor`、`command_fingerprint`。
- 调用记录追加到 `loop/tool-audit.jsonl`。
- 不读 / 不写 `secure/`、`keys/`、`*.env`、`%ProgramData%\opencode\` 路径。

调用方：

- `loop-engineer` 在每个阶段结束时调用 `loop_state`。
- `mvp-verifier` 在每个 AC 验证结束时调用 `quality_gate`。
- `mvp-verifier` 与 `security-reviewer` 在交付前调用 `traceability_check`。

> ⚠ 这三个 Tool 是**第二道防线**，仍须保留 OS 沙箱、文件权限、代码审查和制品审计。
