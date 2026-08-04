<#
AVAIL-1: watchdog that polls the installed cockpit /healthz and restarts
it when it stays unreachable.

* polls http://127.0.0.1:<Port>/healthz every <PollSeconds>;
* after <MissThreshold> consecutive misses it restarts the cockpit with
  the same controlled command as the autostart task (hidden window);
* the interpreter is resolved in this order (OPS-2): explicit -PythonPath,
  then the pin sidecar <InstallRoot>\python-path.txt written by
  register-autostart.ps1 / install_cockpit.py, then python on PATH;
  a stale or malformed pin fails closed instead of silently falling back;
* a restart cooldown (<RestartCooldownSeconds>) prevents crash loops;
* -DryRun performs ONE probe, prints the would-be action, and exits
  without touching the system;
* fail-closed: missing install root / current pointer / runner / python
  (explicit, pinned, or on PATH) aborts before any probe or restart.

Exit codes: 0 = healthy (or dry-run completed), 1 = degraded at exit
(Ctrl+C), 2 = validation failure.
#>
[CmdletBinding()]
param(
    [string]$InstallRoot,
    [string]$PythonPath,
    [int]$Port = 12701,
    [int]$PollSeconds = 10,
    [int]$MissThreshold = 3,
    [int]$RestartCooldownSeconds = 60,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

if (-not $InstallRoot) { $InstallRoot = Join-Path $env:LOCALAPPDATA 'KaiwuAgent' }
$InstallRoot = [IO.Path]::GetFullPath($InstallRoot)
if ($PollSeconds -lt 1 -or $MissThreshold -lt 1 -or $RestartCooldownSeconds -lt 1) {
    throw 'PollSeconds/MissThreshold/RestartCooldownSeconds must be positive'
}

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

function Resolve-PythonPath {
    param([string]$Root, [string]$Explicit)
    $sidecar = Join-Path $Root 'python-path.txt'
    if ($Explicit) {
        $candidate = [IO.Path]::GetFullPath($Explicit)
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "python executable missing: $candidate"
        }
        return $candidate
    }
    if (Test-Path -LiteralPath $sidecar -PathType Leaf) {
        $candidate = (Get-Content -Raw -LiteralPath $sidecar).Trim()
        if (-not $candidate) {
            throw "python pin sidecar is empty: $sidecar"
        }
        if (-not [IO.Path]::IsPathRooted($candidate)) {
            throw "python pin sidecar must contain an absolute path: $candidate"
        }
        $candidate = [IO.Path]::GetFullPath($candidate)
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "python pin sidecar points to a missing executable: $candidate (re-run register-autostart.ps1 -Action PinPython or pass -PythonPath)"
        }
        return $candidate
    }
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw 'python is not on PATH and no pin sidecar exists; pass -PythonPath explicitly'
    }
    return $command.Source
}

$python = Resolve-PythonPath $InstallRoot $PythonPath

$url = "http://127.0.0.1:$Port/healthz"
$startCommand = @($python, $runner)

function Test-CockpitHealth {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        return ($response.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Start-Cockpit {
    Start-Process -FilePath $python -ArgumentList $runner -WindowStyle Hidden
}

if ($DryRun) {
    $healthy = Test-CockpitHealth
    if ($healthy) {
        Write-Output "DRY-RUN: cockpit healthy at $url"
    } else {
        Write-Output ("DRY-RUN: cockpit DOWN at {0}; would restart: {1}" -f $url, ($startCommand -join ' '))
    }
    exit 0
}

Write-Output "watchdog monitoring $url (poll=${PollSeconds}s, misses=${MissThreshold})"
$misses = 0
$lastRestart = 0
try {
    while ($true) {
        if (Test-CockpitHealth) {
            if ($misses -gt 0) { Write-Output "cockpit recovered (was down ${misses}x)" }
            $misses = 0
        } else {
            $misses++
            Write-Output "cockpit unreachable (miss ${misses}/${MissThreshold})"
            if ($misses -ge $MissThreshold) {
                $now = [int][DateTime]::UtcNow.Subtract([DateTime]::new(1970,1,1)).TotalSeconds
                if ($now - $lastRestart -ge $RestartCooldownSeconds) {
                    Write-Output "restarting cockpit (cooldown ${RestartCooldownSeconds}s)"
                    Start-Cockpit
                    $lastRestart = $now
                    $misses = 0
                } else {
                    Write-Output "restart cooldown active; skipping"
                }
            }
        }
        Start-Sleep -Seconds $PollSeconds
    }
} finally {
    Write-Output "watchdog stopped"
}
