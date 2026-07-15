[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidateSet('Create','VerifyMarker','Delete','VerifyRetired','Sign','VerifySignature')][string]$Action,
  [Parameter(Mandatory=$true)][ValidatePattern('^[A-Fa-f0-9-]{36}$')][string]$StoreId,
  [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$Generation,
  [Parameter(Mandatory=$true)][ValidatePattern('^[a-f0-9]{64}$')][string]$Binding,
  [Parameter(Mandatory=$true)][ValidatePattern('^[A-Fa-f0-9-]{36}$')][string]$TransitionId,
  [ValidatePattern('^[A-Fa-f0-9]{40}$')][string]$Token,
  [ValidatePattern('^CoevoIdentityMarker-[a-f0-9]{32}$')][string]$KeyId,
  [ValidatePattern('^[a-f0-9]{64}$')][string]$KeyPublicSha256,
  [string]$ContentPath,[string]$SignaturePath,[string]$ConfigPath='loop/audit-signing.json'
)
$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.Security; $Root=Split-Path -Parent $PSScriptRoot
function Full([string]$Value){if([IO.Path]::IsPathRooted($Value)){return $Value};return Join-Path $Root $Value}
$ConfigPath=Full $ConfigPath; $subject="CN=Coevo Identity Freshness $StoreId"; $extensionOid='1.3.6.1.4.1.57264.1.1'
function Binding-Text([string]$Id){return "$StoreId|$Generation|$Binding|$TransitionId|$Id|$KeyPublicSha256"}
function Equal-Bytes([byte[]]$Left,[byte[]]$Right){if($Left.Length-ne$Right.Length){return $false};for($i=0;$i-lt$Left.Length;$i++){if($Left[$i]-ne$Right[$i]){return $false}};return $true}
function Open-Store([Security.Cryptography.X509Certificates.OpenFlags]$Flags){$store=[Security.Cryptography.X509Certificates.X509Store]::new('My',[Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser);$store.Open($Flags);return $store}
function Find-Marker([string]$Thumbprint,[bool]$AllowMissing=$false){if(-not$Thumbprint){throw'Freshness token is required.'};$store=Open-Store ([Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly);try{$matches=$store.Certificates.Find([Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,$Thumbprint,$false);if($AllowMissing-and$matches.Count-eq 0){return $null};if($matches.Count-ne 1){throw'Freshness marker count must equal one.'};return $matches[0]}finally{$store.Close()}}
function Key-Exists([string]$Id){return [Security.Cryptography.CngKey]::Exists($Id)}
function Key-PublicDigest([Security.Cryptography.CngKey]$Key){$sha=[Security.Cryptography.SHA256]::Create();try{return ([BitConverter]::ToString($sha.ComputeHash($Key.Export([Security.Cryptography.CngKeyBlobFormat]::GenericPublicBlob))).Replace('-','').ToLowerInvariant())}finally{$sha.Dispose()}}
function Require-KeyBinding([Security.Cryptography.CngKey]$Key,[string]$Id){if($Key.KeyName-ne$Id-or(Key-PublicDigest $Key)-ne$KeyPublicSha256){throw'Freshness CNG key binding mismatch.'}}
function Require-PublicMarker([Security.Cryptography.X509Certificates.X509Certificate2]$Certificate){if(-not$KeyId){throw'Freshness key identifier is required.'};$friendly="CoevoIdentityFreshness|"+(Binding-Text $KeyId);if($Certificate.Subject-ne$subject-or$Certificate.FriendlyName-ne$friendly){throw'Freshness marker binding mismatch.'};$extension=@($Certificate.Extensions|Where-Object{$_.Oid.Value-eq$extensionOid});$expected=[Text.Encoding]::UTF8.GetBytes((Binding-Text $KeyId));if($extension.Count-ne 1-or-not(Equal-Bytes $extension[0].RawData $expected)){throw'Freshness marker extension mismatch.'};if($Certificate.NotBefore-gt(Get-Date)-or$Certificate.NotAfter-lt(Get-Date)){throw'Freshness marker is outside its validity period.'}}
function Require-Marker([Security.Cryptography.X509Certificates.X509Certificate2]$Certificate){Require-PublicMarker $Certificate;if(-not$Certificate.HasPrivateKey){throw'Freshness marker private key is unavailable.'};$rsa=[Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($Certificate);try{if($rsa.Key.KeyName-ne$KeyId){throw'Freshness certificate key identifier mismatch.'};Require-KeyBinding $rsa.Key $KeyId}finally{$rsa.Dispose()};$exportable=$false;try{$null=$Certificate.Export([Security.Cryptography.X509Certificates.X509ContentType]::Pfx,'probe');$exportable=$true}catch [Security.Cryptography.CryptographicException]{};if($exportable){throw'Freshness marker private key is exportable.'}}
if($Action-eq'Create'){
  if($Token-or$KeyId-or$KeyPublicSha256){throw'Create does not accept existing marker identifiers.'};$Config=Get-Content -Raw -LiteralPath $ConfigPath|ConvertFrom-Json;$store=Open-Store ([Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite);$key=$null;$rsa=$null;$certificate=$null
  try{$issuers=$store.Certificates.Find([Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,$Config.thumbprint,$false);if($issuers.Count-ne 1-or-not$issuers[0].HasPrivateKey){throw'Pinned attestation certificate is unavailable.'};$createdKeyId="CoevoIdentityMarker-"+[Guid]::NewGuid().ToString('N');$parameters=[Security.Cryptography.CngKeyCreationParameters]::new();$parameters.ExportPolicy=[Security.Cryptography.CngExportPolicies]::None;$parameters.KeyUsage=[Security.Cryptography.CngKeyUsages]::Signing;$parameters.Parameters.Add([Security.Cryptography.CngProperty]::new('Length',[BitConverter]::GetBytes(2048),[Security.Cryptography.CngPropertyOptions]::None));$key=[Security.Cryptography.CngKey]::Create([Security.Cryptography.CngAlgorithm]::Rsa,$createdKeyId,$parameters);$KeyPublicSha256=Key-PublicDigest $key;$rsa=[Security.Cryptography.RSACng]::new($key);$request=[Security.Cryptography.X509Certificates.CertificateRequest]::new($subject,$rsa,[Security.Cryptography.HashAlgorithmName]::SHA256,[Security.Cryptography.RSASignaturePadding]::Pkcs1);$request.CertificateExtensions.Add([Security.Cryptography.X509Certificates.X509Extension]::new($extensionOid,[Text.Encoding]::UTF8.GetBytes((Binding-Text $createdKeyId)),$true));$certificate=$request.CreateSelfSigned((Get-Date).AddMinutes(-5),$issuers[0].NotAfter.AddMinutes(-1));$certificate.FriendlyName="CoevoIdentityFreshness|"+(Binding-Text $createdKeyId);$store.Add($certificate);$Token=$certificate.Thumbprint;$KeyId=$createdKeyId;Require-Marker $certificate;[ordered]@{token=$Token;key_id=$KeyId;key_public_sha256=$KeyPublicSha256}|ConvertTo-Json -Compress
  }catch{if($null-ne$key){try{$key.Delete()}catch{}};throw}finally{if($null-ne$certificate){$certificate.Dispose()};if($null-ne$rsa){$rsa.Dispose()};if($null-ne$key){$key.Dispose()};$store.Close()};exit 0
}
if(-not$Token-or-not$KeyId-or-not$KeyPublicSha256){throw'Token, key identifier and public digest are required.'}
if($Action-eq'Delete'){
  $certificate=Find-Marker $Token $true
  try{if($null-ne$certificate){Require-PublicMarker $certificate;if($certificate.HasPrivateKey){Require-Marker $certificate}}
    if(Key-Exists $KeyId){$key=[Security.Cryptography.CngKey]::Open($KeyId);try{Require-KeyBinding $key $KeyId;$key.Delete()}finally{$key.Dispose()}}
    if(Key-Exists $KeyId){throw'Freshness private key destruction could not be verified.'}
    if($null-ne$certificate){$store=Open-Store ([Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite);try{$store.Remove($certificate)}finally{$store.Close()}}
  }finally{if($null-ne$certificate){$certificate.Dispose()}}
  if(Key-Exists $KeyId){throw'Freshness private key still exists after retirement.'};if($null-ne(Find-Marker $Token $true)){throw'Freshness certificate still exists after retirement.'};exit 0
}
if($Action-eq'VerifyRetired'){if(Key-Exists $KeyId){throw'Retired freshness private key still exists.'};$certificate=Find-Marker $Token $true;if($null-ne$certificate){$certificate.Dispose();throw'Retired freshness certificate still exists.'};Write-Output 'verified';exit 0}
if($Action-eq'VerifyMarker'){$certificate=Find-Marker $Token;try{Require-Marker $certificate}finally{$certificate.Dispose()};Write-Output 'verified';exit 0}
$ContentPath=Full $ContentPath;$SignaturePath=Full $SignaturePath
if($Action-eq'Sign'){$certificate=Find-Marker $Token;try{Require-Marker $certificate;$content=[Security.Cryptography.Pkcs.ContentInfo]::new([IO.File]::ReadAllBytes($ContentPath));$cms=[Security.Cryptography.Pkcs.SignedCms]::new($content,$true);$signer=[Security.Cryptography.Pkcs.CmsSigner]::new($certificate);$signer.IncludeOption=[Security.Cryptography.X509Certificates.X509IncludeOption]::EndCertOnly;$cms.ComputeSignature($signer);[IO.File]::WriteAllBytes($SignaturePath,$cms.Encode())}finally{$certificate.Dispose()};exit 0}
$content=[Security.Cryptography.Pkcs.ContentInfo]::new([IO.File]::ReadAllBytes($ContentPath));$cms=[Security.Cryptography.Pkcs.SignedCms]::new($content,$true);$cms.Decode([IO.File]::ReadAllBytes($SignaturePath));$cms.CheckSignature($true);if($cms.SignerInfos.Count-ne 1-or$cms.SignerInfos[0].Certificate.Thumbprint-ne$Token){throw'Freshness signature token mismatch.'};Write-Output 'verified'
