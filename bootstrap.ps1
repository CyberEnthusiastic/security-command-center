# Bootstrap script: clones all 14 sibling AI Security Projects repos
# Usage: .\bootstrap.ps1

$ErrorActionPreference = "Stop"

function Log  { param($m) Write-Host "[*] $m" -ForegroundColor Blue }
function Ok   { param($m) Write-Host "[+] $m" -ForegroundColor Green }
function Warn { param($m) Write-Host "[!] $m" -ForegroundColor Yellow }

$parentDir = (Resolve-Path "$PSScriptRoot\..").Path
$repos = @(
    # Original 9
    "ai-sast-scanner",
    "cloud-misconfig-hunter",
    "prompt-injection-proxy",
    "compliance-gap-analyzer",
    "waf-bypass-lab",
    "ai-governance-framework",
    "saas-security-posture",
    "itdr-engine",
    "personal-firewall",
    # Second wave (added 2026-04-18)
    "iam-least-privilege-analyzer",
    "k8s-admission-controller",
    "cicd-security-scanner",
    "mitre-attack-detection-rules",
    "soc2-compliance-automation",
    "secrets-detection-rotation-engine"
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

Ok "All 14 sibling repos are in place. Start the Command Center with:"
Write-Host "   python server.py"
Write-Host "Then open:  http://127.0.0.1:5500"
