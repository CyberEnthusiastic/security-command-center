#!/usr/bin/env bash
# ============================================================================
# Security Command Center - uninstaller (macOS / Linux).
# Removes all 15 sibling tool folders, SQLite DB, cached bytecode, and venvs.
# Nothing was ever installed system-wide, so this is literally delete the folders.
# ============================================================================
set -e
cd "$(dirname "$0")"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo
echo "==============================================================="
echo "  Security Command Center - Uninstaller (macOS / Linux)"
echo "==============================================================="
echo "This will DELETE the following from $(cd .. && pwd)/:"
echo "  - All 15 sibling security-tool folders"
echo "  - Local databases (scc.db)"
echo "  - Cached Python bytecode and virtual environments"
echo
echo "Your own files are NOT touched."
echo

read -p "Type YES to continue: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
  echo "Aborted."
  exit 0
fi

PARENT="$(cd .. && pwd)"
REPOS=(
  ai-sast-scanner
  cloud-misconfig-hunter
  prompt-injection-proxy
  compliance-gap-analyzer
  waf-bypass-lab
  ai-governance-framework
  saas-security-posture
  itdr-engine
  personal-firewall
  iam-least-privilege-analyzer
  k8s-admission-controller
  cicd-security-scanner
  mitre-attack-detection-rules
  soc2-compliance-automation
  secrets-detection-rotation-engine
)

for repo in "${REPOS[@]}"; do
  target="$PARENT/$repo"
  if [ -d "$target" ]; then
    printf "${BLUE}[*]${NC} Removing %s\n" "$repo"
    rm -rf "$target"
  fi
done

# Clean Command Center local state
rm -rf data .venv __pycache__ reports/*.json reports/*.html logs/*.jsonl 2>/dev/null || true

printf "\n${GREEN}[+]${NC} Uninstall complete.\n"
echo "    The Security Command Center folder itself was kept in case you want"
echo "    to run ./start-here.command again. Delete it manually if you're done."
echo
