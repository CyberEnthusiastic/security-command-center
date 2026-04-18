#!/usr/bin/env bash
# Bootstrap script: clones all 14 sibling AI Security Projects repos
# so the Command Center can orchestrate them immediately after install.
set -euo pipefail

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${BLUE}[*]${NC} $*"; }
ok()   { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }

PARENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPOS=(
  # Original 9
  "ai-sast-scanner"
  "cloud-misconfig-hunter"
  "prompt-injection-proxy"
  "compliance-gap-analyzer"
  "waf-bypass-lab"
  "ai-governance-framework"
  "saas-security-posture"
  "itdr-engine"
  "personal-firewall"
  # Second wave (added 2026-04-18)
  "iam-least-privilege-analyzer"
  "k8s-admission-controller"
  "cicd-security-scanner"
  "mitre-attack-detection-rules"
  "soc2-compliance-automation"
  "secrets-detection-rotation-engine"
)

log "Cloning sibling AI Security Projects into $PARENT_DIR"
for repo in "${REPOS[@]}"; do
  target="$PARENT_DIR/$repo"
  if [ -d "$target" ]; then
    warn "$repo already exists at $target - skipping"
  else
    log "Cloning $repo..."
    git clone --depth 1 "https://github.com/CyberEnthusiastic/$repo.git" "$target"
    ok "Cloned $repo"
  fi
done

ok "All 14 sibling repos are in place. Start the Command Center with:"
echo "   python server.py"
echo "Then open:  http://127.0.0.1:5500"
