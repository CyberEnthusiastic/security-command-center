#!/usr/bin/env bash
# =============================================================================
# Security Command Center - one-click launcher for macOS / Linux.
# Double-click in Finder (macOS) or run `./start-here.command` in a terminal.
# =============================================================================

set -e
cd "$(dirname "$0")"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { printf "${BLUE}[*]${NC} %s\n" "$*"; }
ok()   { printf "${GREEN}[+]${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}[!]${NC} %s\n" "$*"; }
err()  { printf "${RED}[X]${NC} %s\n" "$*" >&2; }

echo
echo "==============================================================="
echo "  Security Command Center - One-click launcher (macOS / Linux)"
echo "==============================================================="
echo

# ---- Check Python ----------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  err "Python is not installed."
  echo "    Download from https://www.python.org/downloads/ (5 min)"
  echo "    Or on macOS:  brew install python@3.12"
  echo "    Or on Linux:  sudo apt install python3 python3-pip  (or dnf / pacman)"
  read -p "Press Enter to close..." _
  exit 1
fi
ok "Found: $($PY --version 2>&1)"

# ---- Check Git -------------------------------------------------------------
if ! command -v git >/dev/null 2>&1; then
  err "Git is not installed."
  echo "    Download from https://git-scm.com/downloads (2 min)"
  echo "    Or on macOS:  xcode-select --install"
  echo "    Or on Linux:  sudo apt install git  (or dnf / pacman)"
  read -p "Press Enter to close..." _
  exit 1
fi
ok "Found: $(git --version)"
echo

# ---- Bootstrap sibling repos ----------------------------------------------
log "Cloning / updating all 14 sibling security tools..."
echo
bash "./bootstrap.sh"
echo

# ---- Install Python dependencies ------------------------------------------
log "Installing Python dependencies..."
$PY -m pip install --quiet --upgrade pip
$PY -m pip install --quiet -r requirements.txt
ok "Dependencies ready."
echo

# ---- Launch server + open browser -----------------------------------------
log "Starting dashboard at http://127.0.0.1:5500 ..."
log "Press Ctrl+C in this window to stop the server when done."
echo

# Open the browser after a short delay, in the background
(
  sleep 2
  if command -v open >/dev/null 2>&1; then
    open "http://127.0.0.1:5500"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://127.0.0.1:5500"
  fi
) &

$PY server.py
