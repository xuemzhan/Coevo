[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidateSet('Initialize','Sign','Verify','Inspect')][string]$Action,[string]$HeadPath='loop/audit-head.json',[string]$SignaturePath='loop/audit-head.p7s',[string]$ConfigPath='loop/audit-signing.json')
$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.Security; $Root=Split-Path -Parent $PSScriptRoot
Import-Module PKI -ErrorAction Stop
function Full([string]$Value){ if([IO.Path]::IsPathRooted($Value)){return $Value}; return Join-Path $Root $Value }
function FileSha256([string]$Value){ $sha=[Security.Cryptography.SHA256]::Create(); try { $stream=[IO.File]::OpenRead($Value); try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-','').ToLowerInvariant() } finally { $stream.Dispose() } } finally { $sha.Dispose() } }
$HeadPath=Full $HeadPath; $SignaturePath=Full $SignaturePath; $ConfigPath=Full $ConfigPath
if($Action -eq 'Initialize'){
  if(Test-Path -LiteralPath $ConfigPath){ throw 'Signing configuration already exists; refusing replacement.' }
  $cert=New-SelfSignedCertificate -Subject 'CN=Coevo Development Audit Signer' -CertStoreLocation 'Cert:\CurrentUser\My' -Type CodeSigningCert -KeyAlgorithm RSA -KeyLength 3072 -HashAlgorithm SHA256 -KeyExportPolicy NonExportable -NotAfter (Get-Date).AddYears(2)
  $publicPath=Join-Path (Split-Path -Parent $ConfigPath) 'audit-signing-public.cer'; Export-Certificate -Cert $cert -FilePath $publicPath -Type CERT | Out-Null
  $config=[ordered]@{schema_version='1.0';prototype=$true;store='CurrentUser/My';thumbprint=$cert.Thumbprint;public_certificate='loop/audit-signing-public.cer';public_certificate_sha256=(FileSha256 $publicPath);signature_algorithm='RSA-PKCS1-v1_5';digest_algorithm='SHA-256';formal_replacement='approved SM2 product required'}
  [IO.File]::WriteAllText($ConfigPath,($config|ConvertTo-Json -Depth 4)+"`n",[Text.UTF8Encoding]::new($false)); Write-Output $cert.Thumbprint; exit 0
}
$config=Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
if($Action -eq 'Verify'){
  $head=Get-Content -Raw -LiteralPath $HeadPath | ConvertFrom-Json
  $signerThumb=[string]$head.signer_thumbprint
  if($signerThumb){
    if($signerThumb -notmatch '^[0-9A-Fa-f]{40}$'){ throw 'Audit head signer thumbprint is invalid.' }
    if($signerThumb -ne $config.thumbprint){
      $archive=Join-Path (Split-Path -Parent $ConfigPath) ("audit-signing-"+$signerThumb.ToUpperInvariant()+".json")
      if(-not (Test-Path -LiteralPath $archive -PathType Leaf)){ throw 'Pinned historical signing configuration is unavailable.' }
      $config=Get-Content -Raw -LiteralPath $archive | ConvertFrom-Json
    }
    if($config.thumbprint -ne $signerThumb){ throw 'Audit head signer does not match pinned signing configuration.' }
  }
}
$publicPath=Full $config.public_certificate
if((FileSha256 $publicPath) -ne $config.public_certificate_sha256){ throw 'Pinned public certificate hash mismatch.' }
$public=[Security.Cryptography.X509Certificates.X509Certificate2]::new($publicPath)
if($public.Thumbprint -ne $config.thumbprint){ throw 'Pinned certificate thumbprint mismatch.' }
if($public.NotBefore -gt (Get-Date) -or $public.NotAfter -lt (Get-Date)){ throw 'Signing certificate is outside its validity period.' }
if($Action -eq 'Inspect'){
  $store=[Security.Cryptography.X509Certificates.X509Store]::new('My',[Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser); $store.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
  try { $matches=$store.Certificates.Find([Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,$config.thumbprint,$false); if($matches.Count -ne 1){ throw 'Pinned signing certificate count must equal one.' }; $stored=$matches[0] } finally { $store.Close() }
  $exportable=$false; try { $null=$stored.Export([Security.Cryptography.X509Certificates.X509ContentType]::Pfx,'probe'); $exportable=$true } catch [Security.Cryptography.CryptographicException] { }
  if(-not $stored.HasPrivateKey -or $exportable){ throw 'Signing key is missing or exportable.' }
  [ordered]@{thumbprint=$stored.Thumbprint;match_count=$matches.Count;has_private_key=$stored.HasPrivateKey;pfx_exportable=$exportable;store='CurrentUser/My'} | ConvertTo-Json -Compress
  exit 0
}
if($Action -eq 'Sign'){
  $store=[Security.Cryptography.X509Certificates.X509Store]::new('My',[Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser); $store.Open([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
  try { $matches=$store.Certificates.Find([Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,$config.thumbprint,$false); if($matches.Count -ne 1){ throw 'Pinned signing certificate is missing from CurrentUser/My.' }; $stored=$matches[0] } finally { $store.Close() }
  if(-not $stored.HasPrivateKey){ throw 'Signing certificate private key is unavailable.' }
  $exported=$false; try { $null=$stored.Export([Security.Cryptography.X509Certificates.X509ContentType]::Pfx,'probe'); $exported=$true } catch [Security.Cryptography.CryptographicException] { }
  if($exported){ throw 'Signing private key is exportable; refusing to sign.' }
  $content=[Security.Cryptography.Pkcs.ContentInfo]::new([IO.File]::ReadAllBytes($HeadPath)); $cms=[Security.Cryptography.Pkcs.SignedCms]::new($content,$true)
  $signer=[Security.Cryptography.Pkcs.CmsSigner]::new($stored); $signer.IncludeOption=[Security.Cryptography.X509Certificates.X509IncludeOption]::EndCertOnly; $cms.ComputeSignature($signer)
  [IO.File]::WriteAllBytes($SignaturePath,$cms.Encode()); exit 0
}
$content=[Security.Cryptography.Pkcs.ContentInfo]::new([IO.File]::ReadAllBytes($HeadPath)); $cms=[Security.Cryptography.Pkcs.SignedCms]::new($content,$true)
$cms.Decode([IO.File]::ReadAllBytes($SignaturePath)); $cms.CheckSignature($true)
if($cms.SignerInfos.Count -ne 1 -or $cms.SignerInfos[0].Certificate.Thumbprint -ne $config.thumbprint){ throw 'CMS signer does not match the pinned certificate.' }
Write-Output 'verified'
