# 独立验收执行包（Independent Verification Pack）

> 状态：生效（2026-08-10；ARCH-REVIEW-3 记录"实现完成、待独立验收"后，供独立
> mvp-verifier 与 security-reviewer 使用的验收执行包）。

## 1. 角色与独立性

- **mvp-verifier**：在只读沙箱复核 AC 映射、追溯矩阵、审计链与质量证据；
- **security-reviewer**：对身份/密钥/文件解析/权限/审计边界独立 STRIDE 审查；
- 两者独立于实现方（本包为交接证据，不替代审查者自主执行）。

## 2. 复验命令（权威证据）

```powershell
python scripts\test.py --suite unit
python scripts\test.py --suite integration
python scripts\test.py --suite security
python scripts\test.py --suite e2e
python scripts\test.py --suite win7
cd go; $env:GOPROXY='off'; go test ./...
python scripts\quality_gate.py --target fast
python scripts\release_check.py
python scripts\traceability_check.py
python scripts\audit_seal.py verify
```

发布级复验：`python scripts\quality_gate.py --target quality`（业务负责人解除"不做
全量门禁"限制后执行）。

## 3. 逐项证据位置

| 验证项 | 证据 |
|---|---|
| AC 映射 | docs/traceability/requirements-test-matrix.md |
| 能力状态 | docs/architecture/capability-status.md |
| 门禁产物 | loop/runtime/gate-results/*.json（每阶段计数+totals） |
| 审计链 | loop/audit-head.json/.p7s + audit_seal verify |
| 决策记录 | loop/DECISIONS.md（ADR 式，含外部门） |
| 外部门 | docs/architecture/external-gates.md |

## 4. 双签放行条件

1. 全套件 exit=0（含本包命令）；2. 追溯矩阵无悬空；3. audit fully-sealed；
4. 无未解决 Critical/High；5. 独立安全审查覆盖 external-gates 中
REVIEW-REQUIRED 门；6. 审查报告落 DECISIONS 留痕。

## 5. 变更纪律

本执行包由审查者按实际情况调整；任何"以历史记录代替现场复验"的豁免必须
在 DECISIONS 显式留痕。
