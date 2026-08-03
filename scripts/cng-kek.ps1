<#
HANDLE-1: controlled CNG non-exportable KEK helper.

Creates / opens / destroys a *non-exportable* CNG RSA key that acts as a
key-encryption key (KEK) for wrapping the SM2 private-key material of the
protected-handle path. The KEK never leaves the Windows CNG KSP:

* CreateKek      -- create RSA-2048 with ExportPolicy=None, KeyUsage=Decryption
                    in the Microsoft Software Key Storage Provider;
* Status         -- metadata only (exists / exportable / public SHA-256);
* Wrap           -- RSA-OAEP-SHA256 encrypt an input blob (stdin, base64);
* UnwrapDigest   -- RSA-OAEP-SHA256 decrypt and return ONLY the SHA-256 of
                    the plaintext (raw key material never crosses to Python);
* Destroy        -- delete the CNG key.

Protocol: one JSON request on stdin, one JSON response on stdout.
Input buffers are zeroized. Only ciphertext and digests leave the process.
#>
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

function Sha256Hex([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Zero([byte[]]$Bytes) { if ($null -ne $Bytes) { [Array]::Clear($Bytes, 0, $Bytes.Length) } }

function Read-Request {
    $raw = [Console]::In.ReadToEnd()
    try { return $raw | ConvertFrom-Json } finally { $raw = $null }
}

function Write-Response([hashtable]$Result) {
    $payload = @{ schema_version = '1.0'; result = $Result }
    [Console]::Out.Write(($payload | ConvertTo-Json -Compress -Depth 5))
}

function Fail([string]$Message) {
    [Console]::Error.Write($Message)
    exit 22
}

$KEK_RE = '^CoevoSm2Kek-[0-9a-f]{32}$'

$request = Read-Request
if ($null -eq $request -or -not $request.action) { Fail 'GCP-E-INPUT' }
$action = [string]$request.action
$kekName = [string]$request.kek_name
if (-not $kekName -or $kekName -notmatch $KEK_RE) { Fail 'GCP-E-KEK-NAME' }

$params = [Security.Cryptography.CngKeyCreationParameters]::new()
$params.ExportPolicy = [Security.Cryptography.CngExportPolicies]::None
$params.KeyUsage = [Security.Cryptography.CngKeyUsages]::Decryption
$params.Provider = [Security.Cryptography.CngProvider]::MicrosoftSoftwareKeyStorageProvider
$params.Parameters.Add([Security.Cryptography.CngProperty]::new(
    'Length', [BitConverter]::GetBytes([int]2048), [Security.Cryptography.CngPropertyOptions]::None))

switch ($action) {
    'CreateKek' {
        $key = [Security.Cryptography.CngKey]::Create([Security.Cryptography.CngAlgorithm]::Rsa, $kekName, $params)
        try {
            $rsa = [Security.Cryptography.RSACng]::new($key)
            $public = $rsa.ExportParameters([Security.Cryptography.RSAParameters]::Public)
            $publicBytes = New-Object byte[] 0
            $ms = [IO.MemoryStream]::new()
            $w = [IO.BinaryWriter]::new($ms)
            $w.Write($public.Modulus.Length)
            $w.Write($public.Modulus)
            $w.Write($public.Exponent.Length)
            $w.Write($public.Exponent)
            $w.Flush()
            $publicBytes = $ms.ToArray()
            Write-Response @{ kek_name = $kekName; public_sha256 = (Sha256Hex $publicBytes); exportable = $false }
            $w.Dispose(); $ms.Dispose()
        } finally { $rsa.Dispose(); $key.Dispose() }
    }
    'Status' {
        try { $key = [Security.Cryptography.CngKey]::Open($kekName, [Security.Cryptography.CngProvider]::MicrosoftSoftwareKeyStorageProvider, [Security.Cryptography.CngKeyOpenOptions]::None) }
        catch { Fail 'GCP-E-KEK-MISSING' }
        try {
            $rsa = [Security.Cryptography.RSACng]::new($key)
            $exportable = $false
            try { $null = $key.Export([Security.Cryptography.CngKeyBlobFormat]::GenericPrivateBlob); $exportable = $true } catch { }
            Write-Response @{ kek_name = $kekName; exists = $true; exportable = $exportable; key_size = $key.KeySize }
            $rsa.Dispose()
        } finally { $key.Dispose() }
    }
    'Wrap' {
        try { $key = [Security.Cryptography.CngKey]::Open($kekName, [Security.Cryptography.CngProvider]::MicrosoftSoftwareKeyStorageProvider, [Security.Cryptography.CngKeyOpenOptions]::None) }
        catch { Fail 'GCP-E-KEK-MISSING' }
        try {
            $rsa = [Security.Cryptography.RSACng]::new($key)
            $plain = [Convert]::FromBase64String([string]$request.input_base64)
            try {
                $wrapped = $rsa.Encrypt($plain, [Security.Cryptography.RSAEncryptionPadding]::OaepSHA256)
                Write-Response @{ kek_name = $kekName; wrapped_base64 = [Convert]::ToBase64String($wrapped); wrapped_sha256 = (Sha256Hex $wrapped) }
                Zero $wrapped
            } finally { Zero $plain }
            $rsa.Dispose()
        } finally { $key.Dispose() }
    }
    'UnwrapDigest' {
        try { $key = [Security.Cryptography.CngKey]::Open($kekName, [Security.Cryptography.CngProvider]::MicrosoftSoftwareKeyStorageProvider, [Security.Cryptography.CngKeyOpenOptions]::None) }
        catch { Fail 'GCP-E-KEK-MISSING' }
        try {
            $rsa = [Security.Cryptography.RSACng]::new($key)
            $wrapped = [Convert]::FromBase64String([string]$request.input_base64)
            try {
                $plain = $rsa.Decrypt($wrapped, [Security.Cryptography.RSAEncryptionPadding]::OaepSHA256)
                try { Write-Response @{ kek_name = $kekName; plaintext_sha256 = (Sha256Hex $plain); length = $plain.Length } }
                finally { Zero $plain }
            } finally { Zero $wrapped }
            $rsa.Dispose()
        } finally { $key.Dispose() }
    }
    'Destroy' {
        try { $key = [Security.Cryptography.CngKey]::Open($kekName, [Security.Cryptography.CngProvider]::MicrosoftSoftwareKeyStorageProvider, [Security.Cryptography.CngKeyOpenOptions]::None) }
        catch { Fail 'GCP-E-KEK-MISSING' }
        try { $key.Delete() } finally { $key.Dispose() }
        Write-Response @{ kek_name = $kekName; destroyed = $true }
    }
    default { Fail 'GCP-E-ACTION' }
}
