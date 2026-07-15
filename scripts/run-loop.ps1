<#
  run-loop.ps1 — 受限自动循环脚本

  退出码契约（与 scripts/check_loop_stop.py 一致）：
    0  — mvp-complete，停循环
    10 — 继续下一轮
    20 — 阻断，需要人工决策
    30 — opencode CLI 调用失败
    40 — 检查脚本返回了未知状态
    50 — 达到 MaxIterations 上限
#>

[CmdletBinding()]
param(
    [int]$MaxIterations = 12,
    [string]$Agent       = "loop-engineer",
    [string]$TitlePrefix = "MVP Loop"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSCommandPath) | Out-Null
Set-Location .. | Out-Null   # 切到仓库根

Write-Host "Coevo / Loop running from: $PWD"

for ($i = 1; $i -le $MaxIterations; $i++) {
    Write-Host "=== Loop iteration $i / $MaxIterations ==="

    & opencode run `
        --agent $Agent `
        --title  "$TitlePrefix $i" `
        "执行一个且仅一个受控工程循环。完成、阻塞或失败后立即停止本轮。"

    if ($LASTEXITCODE -ne 0) {
        Write-Error "opencode run failed in iteration $i (exit=$LASTEXITCODE)"
        exit 30
    }

    & python scripts/check_loop_stop.py | Out-Null
    switch ($LASTEXITCODE) {
        0  { Write-Host "MVP stop condition reached."; exit 0  }
        10 { Write-Host "Continue to next iteration." }
        20 { Write-Error "Loop is blocked and requires human decision."; exit 20 }
        default { Write-Error "Unknown loop state (exit=$LASTEXITCODE)"; exit 40 }
    }
}

Write-Error "Maximum iteration count reached ($MaxIterations)"
exit 50
