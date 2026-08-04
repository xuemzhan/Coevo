# Coevo 示例一键演示脚本（现场讲解用）
#
# 用法示例：
#   .\scripts\run-demo.ps1                     # 自动跑完全流程
#   .\scripts\run-demo.ps1 -Open               # 跑完自动打开 HTML 演示报告
#   .\scripts\run-demo.ps1 -Interactive        # 逐段暂停讲解
#   .\scripts\run-demo.ps1 -Serve -Port 12751  # 跑完保持驾驶舱服务运行
param(
    [switch]$Interactive,
    [switch]$Serve,
    [switch]$Open,
    [int]$Port = 12751
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$scriptPath = Join-Path $root "examples\tool-dev-project\scripts\run_example.py"

$python = "python"
if (Test-Path (Join-Path $root ".venv\Scripts\python.exe")) {
    $python = Join-Path $root ".venv\Scripts\python.exe"
}

$runArgs = [System.Collections.Generic.List[string]]::new()
if ($Interactive) { $runArgs.Add("--interactive") }
if ($Serve) {
    $runArgs.Add("--serve")
    $runArgs.Add("--port")
    $runArgs.Add([string]$Port)
}
if ($Open) { $runArgs.Add("--open") }

Write-Host "Coevo 示例演示启动：$python $scriptPath $($runArgs -join ' ')"
& $python $scriptPath @runArgs
exit $LASTEXITCODE
