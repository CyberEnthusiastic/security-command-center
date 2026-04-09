# Bootstrap script: clones all 5 sibling AI Security Projects repos
# Usage: .\bootstrap.ps1

$ErrorActionPreference = "Stop"

function Log  { param($m) Write-Host "[*] $m" -ForegroundColor Blue }
function Ok   { param($m) Write-Host "[+] $m" -ForegroundColor Green }
function Warn { param($m) Write-Host "[!] $m" -ForegroundColor Yellow }

$parentDir = (Resolve-Path "$PSScriptRoot\..").Path
$repos = @(
    "ai-sast-scanner",
    "cloud-misconfig-hunter",
    "prompt-injection-proxy",
    "compliance-gap-analyzer",
    "waf-bypass-lab"
)

Log "Cloning sibling AI Security Projects into $parentDir"
foreach ($repo in $repos) {
    $target = Join-Path $parentDir $repo
    if (Test-Path $target) {
        Warn "$repo already exists at $target - skipping"
    } else {
        Log "Cloning $repo..."
        git clone --depth 1 "https://github.com/CyberEnthusiastic/$repo.git" $target
        Ok "Cloned $repo"
    }
}

Ok "All 5 sibling repos are in place. Start the Command Center with:"
Write-Host "   python server.py"
Write-Host "Then open:  http://127.0.0.1:5500"
