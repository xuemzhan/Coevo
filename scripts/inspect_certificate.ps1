[CmdletBinding()]
param()
$ErrorActionPreference='Stop'

function Encode-Length([int]$Length) {
  if($Length -lt 0x80){ return [byte[]]@($Length) }
  $bytes=New-Object System.Collections.Generic.List[byte]
  while($Length -gt 0){ $bytes.Insert(0,[byte]($Length -band 0xff)); $Length=$Length -shr 8 }
  return [byte[]]@([byte](0x80 -bor $bytes.Count)) + $bytes.ToArray()
}
function Wrap-Der([byte]$Tag,[byte[]]$Content) { return [byte[]]@($Tag) + (Encode-Length $Content.Length) + $Content }
function Encode-Base128([uint64]$Value) {
  $bytes=New-Object System.Collections.Generic.List[byte]
  $bytes.Insert(0,[byte]($Value -band 0x7f)); $Value=$Value -shr 7
  while($Value -gt 0){ $bytes.Insert(0,[byte](0x80 -bor ($Value -band 0x7f))); $Value=$Value -shr 7 }
  return $bytes.ToArray()
}
function Encode-Oid([string]$Oid) {
  $parts=@($Oid.Split('.') | ForEach-Object {[uint64]$_})
  if($parts.Count -lt 2 -or $parts[0] -gt 2 -or ($parts[0] -lt 2 -and $parts[1] -gt 39)){ throw 'Invalid public-key OID.' }
  $body=New-Object System.Collections.Generic.List[byte]
  $body.AddRange([byte[]](Encode-Base128 ([uint64](40*$parts[0]+$parts[1]))))
  for($i=2;$i -lt $parts.Count;$i++){ $body.AddRange([byte[]](Encode-Base128 $parts[$i])) }
  return Wrap-Der 0x06 $body.ToArray()
}
function Equal-Bytes([byte[]]$Left,[byte[]]$Right) {
  if($Left.Length -ne $Right.Length){ return $false }
  for($i=0;$i -lt $Left.Length;$i++){ if($Left[$i] -ne $Right[$i]){ return $false } }
  return $true
}

$json=[Console]::In.ReadToEnd()
if([Text.Encoding]::UTF8.GetByteCount($json) -gt 1500000){ throw 'Certificate request is too large.' }
$request=$json | ConvertFrom-Json
$properties=@($request.PSObject.Properties.Name)
if($properties.Count -ne 1 -or $properties[0] -ne 'certificate_der_base64'){ throw 'Certificate request fields are invalid.' }
if($request.certificate_der_base64 -notmatch '^[A-Za-z0-9+/]+={0,2}$'){ throw 'Certificate Base64 is invalid.' }
$raw=[Convert]::FromBase64String($request.certificate_der_base64)
if($raw.Length -eq 0 -or $raw.Length -gt 1048576){ throw 'Certificate size is invalid.' }
$contentType=[Security.Cryptography.X509Certificates.X509Certificate2]::GetCertContentType($raw)
if($contentType -ne [Security.Cryptography.X509Certificates.X509ContentType]::Cert){ throw "Only a single DER X.509 certificate is accepted; detected $contentType." }
$cert=[Security.Cryptography.X509Certificates.X509Certificate2]::new($raw)
try {
  if($cert.HasPrivateKey){ throw 'Certificate input must not contain a private key.' }
  if(-not (Equal-Bytes $raw $cert.RawData)){ throw 'Certificate contains trailing or non-canonical data.' }
  $oid=$cert.PublicKey.Oid.Value
  if($oid -notin @('1.2.840.113549.1.1.1','1.2.840.10045.2.1')){ throw "Unsupported public-key algorithm: $oid" }
  $algorithm=(Wrap-Der 0x30 ((Encode-Oid $oid) + $cert.PublicKey.EncodedParameters.RawData))
  $spki=(Wrap-Der 0x30 ($algorithm + (Wrap-Der 0x03 ([byte[]]@(0) + $cert.PublicKey.EncodedKeyValue.RawData))))
  $sha=[Security.Cryptography.SHA256]::Create()
  try { $fingerprint=([BitConverter]::ToString($sha.ComputeHash($raw))).Replace('-','').ToLowerInvariant() } finally { $sha.Dispose() }
  [ordered]@{
    schema_version='1.0'; content_type='Cert'; has_private_key=$false; certificate_sha256=$fingerprint
    spki_der_base64=[Convert]::ToBase64String($spki); valid_from=$cert.NotBefore.ToUniversalTime().ToString('o')
    valid_to=$cert.NotAfter.ToUniversalTime().ToString('o'); serial_number=$cert.SerialNumber; public_key_algorithm_oid=$oid
  } | ConvertTo-Json -Compress
} finally { $cert.Dispose() }
