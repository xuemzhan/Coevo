<#
OPS-1: register / unregister / query a Windows logon scheduled task that
starts the installed Coevo cockpit.

* Register  -- create a logon-triggered, limited-privilege scheduled task
              running `python <install>\app\<current>\scripts\run_cockpit.py`
              in a hidden window;
* Unregister -- delete the task (no-op when it does not exist);
* Status    -- report whether the task exists and is enabled;
* -DryRun   -- validate and print the exact action without touching the
              system (used by tests and by operators before applying).

Fail-closed: a missing install root / current pointer / runner / python
aborts before any system change. The task runs at user logon only and
requires no administrator rights.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet('Register','Unregister','Status')][string]$Action,
    [string]$InstallRoot,
    [string]$TaskName = 'CoevoCockpit',
    [string]$PythonPath,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

if (-not $InstallRoot) { $InstallRoot = Join-Path $env:LOCALAPPDATA 'KaiwuAgent' }
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)

$pointer = Join-Path $InstallRoot 'current'
if (-not (Test-Path -LiteralPath $pointer -PathType Leaf)) {
    throw "install root has no current pointer (install first): $InstallRoot"
}
$version = (Get-Content -Raw -LiteralPath $pointer).Trim()
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw "invalid current version: $version" }
$runner = Join-Path $InstallRoot ("app\" + $version + '\scripts\run_cockpit.py')
if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) {
    throw "run_cockpit.py missing: $runner"
}

if (-not $PythonPath) {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $command) { throw 'python is not on PATH; pass -PythonPath explicitly' }
    $PythonPath = $command.Source
}
$PythonPath = [IO.Path]::GetFullPath($PythonPath)
if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw "python executable missing: $PythonPath"
}

$taskArgs = ('"{0}" "{1}"' -f $PythonPath, $runner)

function Invoke-SchTasks([string[]]$Arguments) {
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & schtasks.exe @Arguments 2>&1 | Out-Null } finally { $ErrorActionPreference = $previous }
    return $LASTEXITCODE
}

switch ($Action) {
    'Register' {
        if ($DryRun) {
            Write-Output ("DRY-RUN register task '{0}' -> schtasks /create /tn {0} /tr {1} /sc onlogon /rl LIMITED /f" -f $TaskName, $taskArgs)
            exit 0
        }
        $code = Invoke-SchTasks @('/create', '/tn', $TaskName, '/tr', $taskArgs, '/sc', 'onlogon', '/rl', 'LIMITED', '/f')
        if ($code -ne 0) { throw "schtasks create failed: $code" }
        Write-Output "registered task '$TaskName' (logon, $PythonPath)"
    }
    'Unregister' {
        if ($DryRun) {
            Write-Output ("DRY-RUN unregister task '{0}' -> schtasks /delete /tn {0} /f" -f $TaskName)
            exit 0
        }
        $queryCode = Invoke-SchTasks @('/query', '/tn', $TaskName)
        if ($queryCode -eq 0) {
            $code = Invoke-SchTasks @('/delete', '/tn', $TaskName, '/f')
            if ($code -ne 0) { throw "schtasks delete failed: $code" }
            Write-Output "unregistered task '$TaskName'"
        } else {
            Write-Output "task '$TaskName' is not registered"
        }
    }
    'Status' {
        $queryCode = Invoke-SchTasks @('/query', '/tn', $TaskName)
        if ($queryCode -ne 0) {
            Write-Output "task '$TaskName' is NOT registered"
            exit 0
        }
        $previous = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try { $info = & schtasks.exe /query /tn $TaskName /fo LIST /v 2>&1 } finally { $ErrorActionPreference = $previous }
        $state = ($info | Select-String -Pattern 'Status:\s+(.+)$' | Select-Object -First 1)
        Write-Output ("task '{0}' IS registered ({1})" -f $TaskName, $(if ($state) { $state.Matches[0].Groups[1].Value.Trim() } else { 'unknown' }))
    }
}
