$ErrorActionPreference = "Stop"
$Wanted = "0.39.1"
$cmd = Get-Command genlayer -ErrorAction SilentlyContinue
if (-not $cmd) {
  Write-Host "genlayer CLI is not installed. Install exact stable version with: npm install -g genlayer@$Wanted"
  exit 2
}
$actual = (& genlayer --version 2>&1 | Out-String).Trim()
Write-Host $actual
if ($actual -notmatch [regex]::Escape($Wanted)) {
  throw "ProxyMesh requires GenLayer CLI $Wanted. Do not use 0.4.0 or v0.40 RC."
}
& genlayer network set studionet
& genlayer network info
