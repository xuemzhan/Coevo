[CmdletBinding()]
<#
.SYNOPSIS
  Controlled offline helper for non-exportable private-key handles.

.DESCRIPTION
  Round-2 (US-0-AC-2 slice E) implementation. Reads JSON from STDIN
  containing { "action": "Store|Use|Verify|Revoke|Destroy|VerifyHandle", "arguments": {...} }
  and writes a single JSON line to STDOUT describing the result.

  Reads context from ``loop/audit-signing.json`` (the pinned attestation
  thumbprint in ``CurrentUser/My``). When the pinned cert is missing
  the helper exits with code 14 and a JSON envelope; callers MUST
  surface that to the user — production cannot run without a pinned
  parent.

  Real CNG / Smart Card storage:

    * ``Store`` opens the pinned attestation cert, generates a non-exportable
      RSA-2048 signing key (Microsoft CNG ``CngKey.Create`` with
      ``ExportPolicy=None`` and ``KeyUsage=Signing``), records the
      public digest, and writes a durable JSON receipt next to
      ``loop/audit-signing.json``.

    * ``Use`` calls ``RSA.SignData`` over the supplied payload through
      the CNG key and emits a base64 RSA-PKCS1-v1_5 SHA-256 signature.

    * ``Verify`` opens the same non-exportable CNG handle, re-checks its
      receipt/public-digest/algorithm binding, and calls ``RSA.VerifyData``.

    * ``Destroy`` opens the CNG key by ``key_id`` (CNG KeyName), verifies
      the binding, then ``CngKey.Delete`` and tombstones the receipt.

    * ``VerifyHandle`` checks the CNG key still exists and matches the
      public digest.

  Private-key bytes NEVER leave Windows CNG; only the cryptographic
  result flows back to Python.

  Prototype status: the pinned cert uses ``1.2.840.113549.1.1.11``
  (RSA-PKCS1-v1_5 SHA-256), so algorithm OID is ``1.2.840.113549.1.1.1``
  (RSA). Approved-SM2 swap is a future protocol change.
#>
param()
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Security
$Root = Split-Path -Parent $PSScriptRoot

$ConfigPath = Join-Path $Root 'loop/audit-signing.json'
if (-not (Test-Path -LiteralPath $ConfigPath)) { throw 'pinned attestation config is missing' }
$Config = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
$PinnedThumb = [string]$Config.thumbprint
if (-not $PinnedThumb) { throw 'pinned attestation thumbprint is missing in audit-signing.json' }

$ReceiptPath = Join-Path $Root ('loop/private-key-handles-{0}.json' -f $PinnedThumb)

function Emit([hashtable]$Body) {
  $envelope = [ordered]@{ schema_version = '1.0' }
  foreach ($key in $Body.Keys) { $envelope[$key] = $Body[$key] }
  $envelope | ConvertTo-Json -Compress
}

function Open-Store {
  $store = [Security.Cryptography.X509Certificates.X509Store]::new('My', [Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser)
  $store.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
  return $store
}

function Get-PinnedCertificate {
  $store = Open-Store
  try {
    $matches = $store.Certificates.Find([Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint, $PinnedThumb, $false)
    if ($matches.Count -ne 1) { throw ('pinned attestation certificate count must equal one (got {0})' -f $matches.Count) }
    $cert = $matches[0]
    if (-not $cert.HasPrivateKey) { throw 'pinned attestation certificate has no private key' }
    return $cert
  } finally { $store.Close() }
}

function Key-PublicDigest([Security.Cryptography.CngKey]$Key) {
  $sha = [Security.Cryptography.SHA256]::Create()
  try {
    return ([BitConverter]::ToString($sha.ComputeHash($Key.Export([Security.Cryptography.CngKeyBlobFormat]::GenericPublicBlob))).Replace('-','').ToLowerInvariant())
  } finally { $sha.Dispose() }
}

function Read-Receipt {
  if (-not (Test-Path -LiteralPath $ReceiptPath)) { return @{ handles = @{} } }
  $raw = Get-Content -Raw -LiteralPath $ReceiptPath
  if ([string]::IsNullOrWhiteSpace($raw)) { return @{ handles = @{} } }
  $parsed = $raw | ConvertFrom-Json
  if ($null -eq $parsed.handles) { return @{ handles = @{} } }
  $allowed = @('algorithm_oid','public_digest','parent_thumbprint','parent_subject','certificate_id','valid_from','valid_to','creation_audit_id','created_at','destroyed_at','revoked_at','revocation_reason')
  $normalized = @{}
  foreach ($handleProp in $parsed.handles.PSObject.Properties) {
    $entry = @{}
    foreach ($name in $allowed) {
      if ($handleProp.Value.PSObject.Properties.Name -contains $name) {
        $entry[$name] = $handleProp.Value.$name
      }
    }
    $normalized[$handleProp.Name] = $entry
  }
  $parsed.handles = $normalized
  return $parsed
}

function Write-Receipt($Data) {
  $tmp = "$ReceiptPath.tmp"
  [System.IO.File]::WriteAllText($tmp, ($Data | ConvertTo-Json -Depth 16), [System.Text.Encoding]::UTF8)
  Move-Item -LiteralPath $tmp -Destination $ReceiptPath -Force
}

function Set-HandleEntry($Receipt, $Handle, $Entry) {
  $dict = $Receipt.handles
  # Re-hydrate hashtable if PSCustomObject: dot-path fails for keys with dashes
  $temp = @{}
  if ($dict -is [System.Collections.IDictionary]) {
    foreach ($key in $dict.Keys) { $temp[[string]$key] = $dict[$key] }
  } else {
    foreach ($prop in $dict.PSObject.Properties) { $temp[$prop.Name] = $prop.Value }
  }
  $temp[$Handle] = $Entry
  $Receipt.handles = $temp
}

function Get-HandleEntry($Receipt, $Handle) {
  $dict = $Receipt.handles
  if ($dict -is [System.Collections.IDictionary]) { return $dict[$Handle] }
  foreach ($prop in $dict.PSObject.Properties) {
    if ($prop.Name -eq $Handle) { return $prop.Value }
  }
  return $null
}

function Add-EntryField($Entry, $Name, $Value) {
  $temp = @{}
  if ($Entry -is [System.Collections.IDictionary]) {
    foreach ($key in $Entry.Keys) { $temp[[string]$key] = $Entry[$key] }
  } else {
    foreach ($prop in $Entry.PSObject.Properties) { $temp[$prop.Name] = $prop.Value }
  }
  $temp[$Name] = $Value
  return $temp
}

function Assert-ActiveKeyBinding(
  [Security.Cryptography.CngKey]$Key,
  $Record,
  [string]$Handle,
  [string]$PublicDigest
) {
  if ($null -eq $Record) { throw ('receipt for handle {0} is missing' -f $Handle) }
  if (($Record -is [System.Collections.IDictionary] -and $Record.Contains('destroyed_at')) -or
      ($Record -isnot [System.Collections.IDictionary] -and $Record.PSObject.Properties.Name -contains 'destroyed_at')) {
    throw ('receipt for handle {0} is tombstoned; treat as destroyed' -f $Handle)
  }
  if (($Record -is [System.Collections.IDictionary] -and $Record.Contains('revoked_at')) -or
      ($Record -isnot [System.Collections.IDictionary] -and $Record.PSObject.Properties.Name -contains 'revoked_at')) {
    throw ('receipt for handle {0} is revoked' -f $Handle)
  }
  if ([string]$Record.parent_thumbprint -ne $PinnedThumb) {
    throw 'stored handle is not bound to the pinned parent certificate'
  }
  if ([string]$Record.public_digest -ne $PublicDigest) {
    throw 'public digest does not match stored handle'
  }
  if ($Key.KeyName -ne $Handle) {
    throw 'opened CNG key name does not match requested handle'
  }
  if ((Key-PublicDigest $Key) -ne $PublicDigest) {
    throw 'actual CNG key public digest does not match stored handle'
  }
}

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { throw 'store_private_key helper: STDIN is empty' }
try {
  $request = $raw | ConvertFrom-Json -ErrorAction Stop
} catch {
  throw "store_private_key helper: STDIN is not valid JSON ($($_.Exception.Message))"
}
if (-not $request.action) { throw 'action is required' }
if (-not $request.arguments) { throw 'arguments are required' }

switch ($request.action) {
  'Store' {
    $payload = $request.arguments.payload
    if (-not $payload) { throw 'Store requires arguments.payload' }
    $expectedAlgorithmOid = [string]$payload.algorithm_oid
    $expectedPublicDigest = [string]$payload.key_public_sha256
    $expectedCertId = [string]$payload.certificate_id
    $handle = 'CoevoPrivateKey-' + ([Guid]::NewGuid().ToString('N'))
    $key = $null; $rsa = $null
    try {
      $parent = Get-PinnedCertificate
      $parameters = [Security.Cryptography.CngKeyCreationParameters]::new()
      $parameters.ExportPolicy = [Security.Cryptography.CngExportPolicies]::None
      $parameters.KeyUsage = [Security.Cryptography.CngKeyUsages]::Signing
      $lengthBytes = [BitConverter]::GetBytes(2048)
      $lengthProperty = [Security.Cryptography.CngProperty]::new('Length', $lengthBytes, [Security.Cryptography.CngPropertyOptions]::None)
      $parameters.Parameters.Add($lengthProperty)
      $key = [Security.Cryptography.CngKey]::Create([Security.Cryptography.CngAlgorithm]::Rsa, $handle, $parameters)
      $publicDigest = Key-PublicDigest $key
      if ($expectedPublicDigest -and $expectedPublicDigest -ne $publicDigest) {
        $key.Delete(); throw ('public digest mismatch: caller pre-claim {0} vs actual {1}' -f $expectedPublicDigest, $publicDigest)
      }
      $rsa = [Security.Cryptography.RSACng]::new($key)
      try { $null = $rsa.ToXmlString($false) } catch { }
      $stored = Read-Receipt
      if (Get-HandleEntry $stored $handle) { $key.Delete(); throw ('handle {0} already exists' -f $handle) }
      $handleEntry = [ordered]@{
        algorithm_oid = $expectedAlgorithmOid
        public_digest = $publicDigest
        parent_thumbprint = $PinnedThumb
        parent_subject = $parent.Subject
        certificate_id = $expectedCertId
        valid_from = [string]$payload.valid_from
        valid_to = [string]$payload.valid_to
        creation_audit_id = [string]$payload.creation_audit_id
        created_at = (Get-Date).ToUniversalTime().ToString('o')
      }
      Set-HandleEntry $stored $handle $handleEntry
      Write-Receipt $stored
      Emit @{
        reference = [ordered]@{
          key_id = $handle
          algorithm_oid = $expectedAlgorithmOid
          key_public_sha256 = $publicDigest
          valid_from = [string]$payload.valid_from
          valid_to = [string]$payload.valid_to
          revoked = $false
          handle_token_hint = $handle.Substring($handle.Length - 16, 16)
        }
      }
    } catch {
      if ($null -ne $key) { try { $key.Delete() } catch { } }
      throw
    } finally {
      if ($null -ne $rsa) { $rsa.Dispose() }
      if ($null -ne $key) { $key.Dispose() }
    }
  }
  'Use' {
    $handle = [string]$request.arguments.handle
    $publicDigest = [string]$request.arguments.public_digest
    $payloadPath = [string]$request.arguments.payload_path
    if (-not (Test-Path -LiteralPath $payloadPath)) { throw 'payload file is missing' }
    if (-not [Security.Cryptography.CngKey]::Exists($handle)) { throw ('private-key handle {0} is missing from local store' -f $handle) }
    $stored = Read-Receipt
    $record = Get-HandleEntry $stored $handle
    if (-not $record) { throw ('receipt for handle {0} is missing; treat as destroyed' -f $handle) }
    $key = [Security.Cryptography.CngKey]::Open($handle)
    $rsa = $null
    try {
      Assert-ActiveKeyBinding $key $record $handle $publicDigest
      if ([string]$record.algorithm_oid -ne [string]$request.arguments.algorithm_oid) {
        throw 'algorithm OID does not match stored handle'
      }
      $rsa = [Security.Cryptography.RSACng]::new($key)
      $bytes = [IO.File]::ReadAllBytes($payloadPath)
      $signature = $rsa.SignData($bytes, [Security.Cryptography.HashAlgorithmName]::SHA256, [Security.Cryptography.RSASignaturePadding]::Pkcs1)
      Emit @{ result = @{ signature_base64 = [Convert]::ToBase64String($signature); algorithm = 'RSA-PKCS1-v1_5-SHA256' } }
    } finally {
      if ($null -ne $rsa) { $rsa.Dispose() }
      $key.Dispose()
    }
  }
  'Verify' {
    $handle = [string]$request.arguments.handle
    $publicDigest = [string]$request.arguments.public_digest
    $payloadPath = [string]$request.arguments.payload_path
    $signatureBase64 = [string]$request.arguments.signature_base64
    $expectedParentThumbprint = [string]$request.arguments.parent_pinned_thumbprint
    if (-not (Test-Path -LiteralPath $payloadPath)) { throw 'payload file is missing' }
    if (-not $signatureBase64) { throw 'signature_base64 is required' }
    if (-not $expectedParentThumbprint -or $expectedParentThumbprint -ne $PinnedThumb) {
      throw 'parent thumbprint does not match the configured trust pin'
    }
    if (-not [Security.Cryptography.CngKey]::Exists($handle)) { throw ('private-key handle {0} is missing from local store' -f $handle) }
    $stored = Read-Receipt
    $record = Get-HandleEntry $stored $handle
    if (-not $record) { throw ('receipt for handle {0} is missing; treat as destroyed' -f $handle) }
    $key = [Security.Cryptography.CngKey]::Open($handle)
    $rsa = $null
    try {
      Assert-ActiveKeyBinding $key $record $handle $publicDigest
      if ([string]$record.algorithm_oid -ne [string]$request.arguments.algorithm_oid) {
        throw 'algorithm OID does not match stored handle'
      }
      try { $signature = [Convert]::FromBase64String($signatureBase64) }
      catch { throw 'signature_base64 is malformed' }
      $rsa = [Security.Cryptography.RSACng]::new($key)
      $bytes = [IO.File]::ReadAllBytes($payloadPath)
      $verified = $rsa.VerifyData($bytes, $signature, [Security.Cryptography.HashAlgorithmName]::SHA256, [Security.Cryptography.RSASignaturePadding]::Pkcs1)
      Emit @{ result = @{ verified = [bool]$verified; algorithm = 'RSA-PKCS1-v1_5-SHA256'; certificate_id = $record.certificate_id; parent_thumbprint = $record.parent_thumbprint } }
    } finally {
      if ($null -ne $rsa) { $rsa.Dispose() }
      $key.Dispose()
    }
  }
  'Revoke' {
    $handle = [string]$request.arguments.handle
    $publicDigest = [string]$request.arguments.public_digest
    $reason = [string]$request.arguments.reason
    if ([string]::IsNullOrWhiteSpace($reason)) { throw 'revocation reason is required' }
    if (-not [Security.Cryptography.CngKey]::Exists($handle)) { throw ('private-key handle {0} is missing from local store' -f $handle) }
    $stored = Read-Receipt
    $record = Get-HandleEntry $stored $handle
    if (-not $record) { throw ('receipt for handle {0} is missing' -f $handle) }
    $key = [Security.Cryptography.CngKey]::Open($handle)
    try {
      Assert-ActiveKeyBinding $key $record $handle $publicDigest
      $updated = Add-EntryField $record 'revoked_at' ((Get-Date).ToUniversalTime().ToString('o'))
      $updated = Add-EntryField $updated 'revocation_reason' ([BitConverter]::ToString(([Security.Cryptography.SHA256]::Create()).ComputeHash([Text.Encoding]::UTF8.GetBytes($reason))).Replace('-','').ToLowerInvariant())
      Set-HandleEntry $stored $handle $updated
      Write-Receipt $stored
      Emit @{ result = @{ revoked = $true } }
    } finally {
      $key.Dispose()
    }
  }
  'Destroy' {
    $handle = [string]$request.arguments.handle
    $publicDigest = [string]$request.arguments.public_digest
    if (-not [Security.Cryptography.CngKey]::Exists($handle)) { throw ('private-key handle {0} is missing from local store' -f $handle) }
    $key = [Security.Cryptography.CngKey]::Open($handle)
    try {
      if ((Key-PublicDigest $key) -ne $publicDigest) { throw 'public digest does not match stored handle' }
      $key.Delete()
    } finally {
      $key.Dispose()
    }
    if ([Security.Cryptography.CngKey]::Exists($handle)) { throw ('private-key destruction could not be verified for {0}' -f $handle) }
    $stored = Read-Receipt
    $record = Get-HandleEntry $stored $handle
    if ($record) {
      $updated = Add-EntryField $record 'destroyed_at' ((Get-Date).ToUniversalTime().ToString('o'))
      Set-HandleEntry $stored $handle $updated
    }
    Write-Receipt $stored
    Emit @{ result = @{ destroyed = $true } }
  }
  'VerifyHandle' {
    $handle = [string]$request.arguments.handle
    $publicDigest = [string]$request.arguments.public_digest
    if (-not [Security.Cryptography.CngKey]::Exists($handle)) { throw ('private-key handle {0} is missing from local store' -f $handle) }
    $stored = Read-Receipt
    $record = Get-HandleEntry $stored $handle
    if (-not $record) { throw ('receipt for handle {0} is missing' -f $handle) }
    $key = [Security.Cryptography.CngKey]::Open($handle)
    try {
      Assert-ActiveKeyBinding $key $record $handle $publicDigest
      Emit @{ result = @{ verified = $true; certificate_id = $record.certificate_id; parent_thumbprint = $record.parent_thumbprint } }
    } finally {
      $key.Dispose()
    }
  }
  default { throw ("unknown action '{0}'" -f $request.action) }
}
