<#
AVAIL-3: restart budget for crash-loop protection.

Pure, testable helper shared by cockpit-watchdog.ps1 (dot-sourced). The
watchdog may restart the cockpit at most <MaxRestarts> times per
<WindowSeconds>; once the budget is exhausted it keeps polling but stops
restarting until the window rolls, so a persistently crashing cockpit
cannot churn processes indefinitely.

Usage:
    . (Join-Path $PSScriptRoot 'restart-budget.ps1')   # dot-source (defines Test-RestartBudget)
    powershell -File restart-budget.ps1 -TimestampsJson '[1,2,3]' -WindowSeconds 3600 -MaxRestarts 5
#>
[CmdletBinding()]
param(
    [string]$TimestampsJson,
    [int]$WindowSeconds = 3600,
    [int]$MaxRestarts = 5
)
$ErrorActionPreference = 'Stop'

function Test-RestartBudget {
    param(
        [double[]]$RestartTimes,
        [int]$WindowSeconds,
        [int]$MaxRestarts
    )
    if ($WindowSeconds -lt 1 -or $MaxRestarts -lt 1) {
        throw 'WindowSeconds and MaxRestarts must be positive'
    }
    $now = [DateTime]::UtcNow.Subtract([DateTime]::new(1970, 1, 1)).TotalSeconds
    $cutoff = $now - $WindowSeconds
    $recent = @($RestartTimes | Where-Object { $_ -ge $cutoff })
    return @{
        allowed = ($recent.Count -lt $MaxRestarts)
        recent = $recent.Count
    }
}

if ($TimestampsJson) {
    $parsed = $TimestampsJson | ConvertFrom-Json
    $times = if ($null -eq $parsed) { [double[]]@() } else { [double[]]$parsed }
    $result = Test-RestartBudget -RestartTimes $times -WindowSeconds $WindowSeconds -MaxRestarts $MaxRestarts
    Write-Output ("allowed={0} recent={1}" -f $result.allowed, $result.recent)
}
