<#
CI-1: restore the locked Coevo toolchain from a pinned GitHub Release artifact.

The repository's gates require the locked toolchain (.tools/), which is
gitignored and machine-local. CI restores it from a published artifact
whose SHA-256 is pinned in docs/dependencies/ci-artifact.json. The
restore is fail-closed:

* the artifact source must be https (or an explicit local path for tests);
* the archive SHA-256 must equal the pinned value before any extraction;
* extraction happens into a temp staging directory first, then the
  expected entries are checked before the content is moved into
  <repo>/.tools;
* the descriptor refuses to run while sha256 is 'pending'.

No secrets are involved; the artifact is content-addressed by hash only.
#>
[CmdletBinding()]
param(
    [string]$ArtifactUrl,
    [string]$ArtifactSha256,
    [string]$InstallRoot,
    [string]$LocalPath,
    [string]$DescriptorPath
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (-not $InstallRoot) { $InstallRoot = Join-Path $Root '.tools' }
if (-not $DescriptorPath) { $DescriptorPath = Join-Path $Root 'docs\dependencies\ci-artifact.json' }

function FileSha256([string]$Value) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::OpenRead($Value)
        try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
        finally { $stream.Dispose() }
    } finally { $sha.Dispose() }
}

$ExpectedEntries = @(
    'python\3.14.3\python.exe',
    'node\24.14.0\node.exe',
    'control\control.pyz'
)

# Resolve URL/hash from the descriptor unless explicitly overridden.
if (-not $ArtifactUrl -or -not $ArtifactSha256) {
    if (-not (Test-Path -LiteralPath $DescriptorPath)) { throw "artifact descriptor missing: $DescriptorPath" }
    $desc = Get-Content -Raw -LiteralPath $DescriptorPath | ConvertFrom-Json
    if (-not $ArtifactUrl) { $ArtifactUrl = [string]$desc.url }
    if (-not $ArtifactSha256) { $ArtifactSha256 = [string]$desc.sha256 }
}
if (-not $ArtifactSha256 -or $ArtifactSha256 -notmatch '^[0-9a-f]{64}$') {
    throw 'artifact sha256 must be pinned to a 64-char hex digest (publish the artifact and update docs/dependencies/ci-artifact.json)'
}

$archive = $LocalPath
if (-not $archive) {
    if ($ArtifactUrl -notmatch '^https://') { throw 'artifact URL must be https' }
    $archive = Join-Path $env:TEMP ('coevo-toolchain-' + [guid]::NewGuid().ToString('N') + '.zip')
    Invoke-WebRequest -Uri $ArtifactUrl -OutFile $archive -UseBasicParsing
}
if (-not (Test-Path -LiteralPath $archive)) { throw "artifact archive missing: $archive" }

$actual = FileSha256 $archive
if ($actual -ne $ArtifactSha256) {
    throw "artifact hash mismatch: expected=$ArtifactSha256 actual=$actual"
}

$staging = Join-Path $env:TEMP ('coevo-toolchain-stage-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $staging | Out-Null
try {
    Expand-Archive -LiteralPath $archive -DestinationPath $staging -Force
    $src = Join-Path $staging '.tools'
    if (-not (Test-Path -LiteralPath $src)) { $src = $staging }
    foreach ($entry in $ExpectedEntries) {
        if (-not (Test-Path -LiteralPath (Join-Path $src $entry))) {
            throw "expected toolchain entry missing from artifact: $entry"
        }
    }
    $lock = Join-Path $Root 'docs\dependencies\toolchain-lock.json'
    if (-not (Test-Path -LiteralPath $lock)) { throw 'repository toolchain-lock.json is missing' }
    $null = Get-Content -Raw -LiteralPath $lock | ConvertFrom-Json

    New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
    Copy-Item -Path (Join-Path $src '*') -Destination $InstallRoot -Recurse -Force
    Write-Output "toolchain restored: $InstallRoot (sha256=$ArtifactSha256)"
}
finally {
    Remove-Item -LiteralPath $staging -Recurse -Force -ErrorAction SilentlyContinue
    if ($LocalPath -eq $null -and (Test-Path -LiteralPath $archive)) {
        Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
    }
}
