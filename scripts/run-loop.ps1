<#
  run-loop.ps1 — 受限 Loop 启动器。每次 opencode run 只执行一个工作项，
  不使用 --auto；完成、阻断或达到上限后立即停止。

  退出码：0=mvp-complete；10=尚可继续；20=需人工决策；
  30=OpenCode 调用失败；40=未知状态。达到上限时返回 10，由新 session 继续。
#>
[CmdletBinding()]
param(
    [ValidateRange(1,40)][int]$MaxIterations = 12,
    [ValidatePattern('^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$')][string]$Item,
    [ValidatePattern('^[a-z0-9][a-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._:/-]*$')][string]$Model,
    [ValidatePattern('^[^-][A-Za-z0-9 _.-]{0,79}$')][string]$TitlePrefix = 'MVP Loop'
)

$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
. (Join-Path $PSScriptRoot 'enter-dev-environment.ps1') -Quiet
$OpenCode=$env:COEVO_OPENCODE_PATH

Write-Host "Coevo / Loop running from: $Root"
for($i=1;$i -le $MaxIterations;$i++){
    Write-Host "=== Loop iteration $i / $MaxIterations ==="
    $Arguments=@('run','--command','loop','--title',"$TitlePrefix $i")
    if($Model){ $Arguments+=@('--model',$Model) }
    if($Item){ $Arguments+=@('--',$Item) }
    if($Arguments -contains '--auto'){ throw 'Automatic permission approval is forbidden.' }
    & $OpenCode @Arguments
    if($LASTEXITCODE -ne 0){ Write-Error "opencode run failed in iteration $i (exit=$LASTEXITCODE)"; exit 30 }

    & $env:COEVO_MAKE_PATH verify-loop-state | Out-Null
    switch($LASTEXITCODE){
      0 { Write-Host 'MVP stop condition reached.'; exit 0 }
      10 { Write-Host 'Current item finished; another fresh session may continue.' }
      20 { Write-Error 'Loop is blocked and requires human decision.'; exit 20 }
      default { Write-Error "Unknown loop state (exit=$LASTEXITCODE)"; exit 40 }
    }
    $Item=$null
}
Write-Host "Maximum iteration count reached ($MaxIterations); a fresh session may continue."
exit 10
