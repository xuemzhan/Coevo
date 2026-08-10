# 门禁分层策略（Gate Tiers）

> 状态：生效（2026-08-10，ARCH-REVIEW-7）
> 适用范围：`scripts/quality_gate.py` 与 `scripts/tool-shims/make.cs` 的门禁入口。

## 1. 分层定义

- **fast（迭代内环）**：`python scripts/quality_gate.py --target fast`（或 `make fast`）
  = compileall + lint（validate_opencode / traceability_check / audit verify /
  audit seal verify / archive_records --check / secret_scan）+ 单元测试
  （`tests/unit`）。用于每个工作项的最小反馈闭环，约 3-5 分钟。
- **quality（发布/收口）**：`--target quality` = fmt + lint + test（单元+集成+Go）+
  test-security + test-e2e + test-win7（Win7 兼容子集）。作为 mvp-complete、
  发布与审计收口的唯一权威门槛。

## 2. 纪律

1. 开发/迭代轮次允许仅过 `fast`；**任何宣称 done / 收口 / 发布的行为必须过 `quality`**，
   除非业务负责人显式豁免（豁免须在 `loop/DECISIONS.md` 留痕）。
2. 新增测试套件时，必须同步决定其归属层（unit/integration/security/e2e），
   不得出现"只在全量 quality 里才被发现的遗漏套件"。
3. 修改 `quality_gate.py` / `make.cs` 后，必须同步
   `docs/dependencies/python-script-lock.tsv`、
   `scripts/tool-shims/make.cs` 的 `ScriptInventorySha256` 与
   `docs/dependencies/toolchain-lock.json` 的
   `make_compatibility_shim.source_sha256 / source_size / script_inventory`。

## 3. 守卫测试

`tests/unit/test_arch_review_7_gate_tiers.py` 强制：

- `TARGETS["fast"]` 存在且等于 fmt + lint + 单元测试命令；
- `quality` 的命令集与 fingerprint 不变（回归钉）；
- `make.cs` 暴露 `fast` 目标；
- 本契约文档存在。
