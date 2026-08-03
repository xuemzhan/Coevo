<#
  Force-removes Coevo loop\runtime.
  Handles very deep paths, large trees, and read-only files.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [switch]$Yes
)

$ErrorActionPreference = 'Stop'
$Root = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\')
$Target = [System.IO.Path]::GetFullPath((Join-Path $Root 'loop\runtime')).TrimEnd('\')
$Expected = [System.IO.Path]::GetFullPath('E:\Workspace\Coevo\loop\runtime').TrimEnd('\')

if (-not [string]::Equals($Target, $Expected, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Safety check failed: target must be $Expected (actual: $Target)."
}

if (-not [System.IO.Directory]::Exists($Target)) {
    Write-Host "Nothing to delete: $Target"
    exit 0
}

$item = Get-Item -LiteralPath $Target -Force
if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "Safety check failed: refusing to delete a reparse point: $Target"
}

if (-not $Yes) {
    $answer = Read-Host "Permanently delete $Target and everything below it? Type DELETE"
    if ($answer -cne 'DELETE') {
        Write-Host 'Cancelled.'
        exit 2
    }

    if (-not $PSCmdlet.ShouldProcess($Target, 'Permanently delete the directory tree')) {
        exit 0
    }
}
elseif ($WhatIfPreference) {
    Write-Host "WhatIf: would permanently delete $Target"
    exit 0
}

Write-Host "Deleting: $Target"

# Mirror an empty directory into the target. Robocopy handles deep Win32 paths
# better than Remove-Item and /XJ prevents traversal through junctions.
$empty = Join-Path $env:TEMP ('.coevo-empty-' + [Guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($empty) | Out-Null
try {
    & robocopy.exe $empty $Target /MIR /PURGE /SL /R:1 /W:1 /NFL /NDL /NJH /NJS /NP /XJ | Out-Null
    $robocopyExit = $LASTEXITCODE
    if ($robocopyExit -ge 8) {
        throw "Robocopy cleanup failed with exit code $robocopyExit."
    }
}
finally {
    if ([System.IO.Directory]::Exists($empty)) {
        [System.IO.Directory]::Delete($empty, $true)
    }
}

$longTarget = '\\?\' + $Target
try {
    [System.IO.Directory]::Delete($longTarget, $false)
}
catch {
    # cmd.exe rd is tolerant of residual read-only directory attributes.
    & cmd.exe /d /c rd /s /q ('"' + $longTarget + '"')
    if ($LASTEXITCODE -ne 0) {
        throw "Final directory removal failed with exit code $LASTEXITCODE."
    }
}

if ([System.IO.Directory]::Exists($longTarget)) {
    throw "Post-delete verification failed; directory still exists: $Target"
}

Write-Host "Verified removed: $Target"
