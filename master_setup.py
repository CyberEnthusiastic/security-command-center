"""
Security Command Center — Master Setup
One command installs the ENTIRE AI Security Projects suite.

What it does:
  1. Checks Python version (3.8+ required)
  2. Creates install directory
  3. Clones all 10 tool repos from GitHub
  4. Installs dependencies (pip install)
  5. Runs self-test on each tool
  6. Sets up persistent startup (Windows Task Scheduler / cron)
  7. Launches the dashboard
  8. Prints a full guide with storage locations

Run:
  python master_setup.py install     # full install
  python master_setup.py uninstall   # complete removal
  python master_setup.py status      # check what's installed
  python master_setup.py start       # start dashboard
  python master_setup.py stop        # stop dashboard

Author: Mohith Vasamsetti (CyberEnthusiastic)
License: Proprietary — see LICENSE
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


SUITE_NAME = "AI Security Projects Suite"
VERSION = "1.0.0"
AUTHOR = "Mohith Vasamsetti"
GITHUB = "https://github.com/CyberEnthusiastic"

# Default install location
if platform.system() == "Windows":
    DEFAULT_INSTALL = Path(os.environ.get("LOCALAPPDATA", "C:/Users")) / "SecuritySuite"
else:
    DEFAULT_INSTALL = Path.home() / ".security-suite"

REPOS = [
    {"name": "security-command-center", "desc": "Unified Dashboard", "has_server": True, "port": 5500},
    {"name": "ai-sast-scanner", "desc": "Code Vulnerability Scanner", "test_cmd": "python scanner.py samples/"},
    {"name": "cloud-misconfig-hunter", "desc": "AWS IaC Security", "test_cmd": "python hunter.py samples/"},
    {"name": "prompt-injection-proxy", "desc": "LLM Firewall", "test_cmd": "python benchmark.py", "has_server": True, "port": 5001},
    {"name": "compliance-gap-analyzer", "desc": "SOC2/ISO27001 Analyzer", "test_cmd": "python analyzer.py samples/acme_security_policy.md"},
    {"name": "waf-bypass-lab", "desc": "WAF Coverage Tester", "test_cmd": "python waf_lab.py --list-categories"},
    {"name": "ai-governance-framework", "desc": "AI Tool DLP + RBAC", "test_cmd": "python governance.py --demo"},
    {"name": "saas-security-posture", "desc": "SaaS Security Dashboard", "test_cmd": "python analyzer.py"},
    {"name": "itdr-engine", "desc": "Identity Threat Detection", "test_cmd": "python itdr.py"},
    {"name": "personal-firewall", "desc": "Network Monitor + Firewall", "test_cmd": "python firewall.py scan --no-intel"},
]

DASHBOARD_PORT = 5500


def log(msg): print(f"  \033[94m[*]\033[0m {msg}")
def ok(msg):  print(f"  \033[92m[+]\033[0m {msg}")
def warn(msg): print(f"  \033[93m[!]\033[0m {msg}")
def err(msg): print(f"  \033[91m[x]\033[0m {msg}")


def banner():
    print("""
    ============================================================
       AI SECURITY PROJECTS SUITE — Master Setup v1.0
       10 production-grade security tools, one installer
       github.com/CyberEnthusiastic
    ============================================================
    """)


def check_python():
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        err(f"Python {v.major}.{v.minor} found — need 3.8+")
        sys.exit(1)
    ok(f"Python {v.major}.{v.minor}.{v.micro}")


def check_git():
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        ok(f"Git: {r.stdout.strip()}")
    except Exception:
        err("Git not found. Install from https://git-scm.com")
        sys.exit(1)


def install(install_dir: Path, skip_tests=False, no_persist=False):
    banner()
    print(f"  Install directory: {install_dir}\n")

    log("Checking prerequisites...")
    check_python()
    check_git()

    install_dir.mkdir(parents=True, exist_ok=True)

    # Clone all repos
    print(f"\n  Cloning {len(REPOS)} repositories...\n")
    for repo in REPOS:
        repo_dir = install_dir / repo["name"]
        if repo_dir.exists():
            warn(f"{repo['name']}: already exists, pulling latest...")
            subprocess.run(["git", "pull"], cwd=repo_dir, capture_output=True, timeout=30)
        else:
            log(f"Cloning {repo['name']} ({repo['desc']})...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", f"{GITHUB}/{repo['name']}.git", str(repo_dir)],
                    check=True, capture_output=True, timeout=60
                )
                ok(f"{repo['name']}")
            except Exception as e:
                err(f"{repo['name']}: clone failed — {e}")

    # Install dependencies
    print("\n  Installing dependencies...\n")
    for repo in REPOS:
        repo_dir = install_dir / repo["name"]
        req_file = repo_dir / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text(encoding="utf-8").strip()
            if content and not content.startswith("#"):
                log(f"Installing deps for {repo['name']}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)],
                    capture_output=True, timeout=120
                )
                ok(f"{repo['name']}: deps installed")
            else:
                ok(f"{repo['name']}: zero dependencies (pure stdlib)")

    # Run self-tests
    if not skip_tests:
        print("\n  Running self-tests...\n")
        passed = 0
        for repo in REPOS:
            cmd = repo.get("test_cmd")
            if not cmd:
                continue
            repo_dir = install_dir / repo["name"]
            try:
                r = subprocess.run(
                    cmd.split(), cwd=repo_dir, capture_output=True, text=True,
                    timeout=60, encoding="utf-8", errors="replace"
                )
                if r.returncode == 0:
                    ok(f"{repo['name']}: PASS")
                    passed += 1
                else:
                    warn(f"{repo['name']}: exit {r.returncode}")
            except Exception as e:
                warn(f"{repo['name']}: {e}")
        print(f"\n  Self-tests: {passed}/{sum(1 for r in REPOS if r.get('test_cmd'))} passed\n")

    # Setup persistence
    if not no_persist:
        setup_persistence(install_dir)

    # Save install metadata
    meta = {
        "version": VERSION,
        "install_dir": str(install_dir),
        "installed_at": __import__("datetime").datetime.now().isoformat(),
        "repos": [r["name"] for r in REPOS],
        "dashboard_port": DASHBOARD_PORT,
        "python": sys.executable,
    }
    (install_dir / "install_meta.json").write_text(json.dumps(meta, indent=2))

    # Print final guide
    print_guide(install_dir)


def setup_persistence(install_dir: Path):
    """Set up auto-start on boot."""
    log("Setting up auto-start on boot...")
    scc_dir = install_dir / "security-command-center"

    if platform.system() == "Windows":
        # Create a startup batch file
        startup_bat = install_dir / "start_dashboard.bat"
        startup_bat.write_text(
            f'@echo off\n'
            f'cd /d "{scc_dir}"\n'
            f'start /min python server.py --port {DASHBOARD_PORT}\n'
        )

        # Create a stop batch file
        stop_bat = install_dir / "stop_dashboard.bat"
        stop_bat.write_text(
            '@echo off\n'
            'taskkill /F /FI "WINDOWTITLE eq Security Command Center*" 2>nul\n'
            f'for /f "tokens=5" %%a in (\'netstat -ano ^| findstr :{DASHBOARD_PORT}\') do taskkill /F /PID %%a 2>nul\n'
            'echo Dashboard stopped.\n'
        )

        # Add to Windows startup folder
        startup_folder = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if startup_folder.exists():
            shortcut_bat = startup_folder / "SecuritySuite_Dashboard.bat"
            shortcut_bat.write_text(
                f'@echo off\n'
                f'cd /d "{scc_dir}"\n'
                f'start /min python server.py --port {DASHBOARD_PORT}\n'
            )
            ok(f"Auto-start added to Windows Startup folder")
        else:
            warn("Could not find Windows Startup folder. Start manually with start_dashboard.bat")

        ok(f"Start: {startup_bat}")
        ok(f"Stop:  {stop_bat}")
    else:
        # Linux/Mac: create systemd user service or launchd plist
        service_content = f"""[Unit]
Description=Security Command Center Dashboard
After=network.target

[Service]
Type=simple
WorkingDirectory={scc_dir}
ExecStart={sys.executable} server.py --port {DASHBOARD_PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""
        service_dir = Path.home() / ".config" / "systemd" / "user"
        service_dir.mkdir(parents=True, exist_ok=True)
        service_file = service_dir / "security-dashboard.service"
        service_file.write_text(service_content)
        subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
        subprocess.run(["systemctl", "--user", "enable", "security-dashboard"], capture_output=True)
        ok("Systemd user service created and enabled")


def uninstall(install_dir: Path):
    banner()
    print(f"  Uninstalling from: {install_dir}\n")

    # Remove persistence
    if platform.system() == "Windows":
        startup_folder = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        shortcut = startup_folder / "SecuritySuite_Dashboard.bat"
        if shortcut.exists():
            shortcut.unlink()
            ok("Removed auto-start from Windows Startup")

        # Kill dashboard process
        subprocess.run(
            f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{DASHBOARD_PORT}\') do taskkill /F /PID %a',
            shell=True, capture_output=True
        )
    else:
        subprocess.run(["systemctl", "--user", "stop", "security-dashboard"], capture_output=True)
        subprocess.run(["systemctl", "--user", "disable", "security-dashboard"], capture_output=True)
        service_file = Path.home() / ".config" / "systemd" / "user" / "security-dashboard.service"
        if service_file.exists():
            service_file.unlink()
            ok("Removed systemd service")

    # Remove install directory
    if install_dir.exists():
        log(f"Removing {install_dir}...")
        shutil.rmtree(install_dir, ignore_errors=True)
        ok("All files removed")

    ok("Uninstall complete. No files, services, or startup entries remain.")


def status(install_dir: Path):
    banner()
    meta_file = install_dir / "install_meta.json"
    if not meta_file.exists():
        warn(f"Suite not installed at {install_dir}")
        print(f"  Run: python master_setup.py install")
        return

    meta = json.loads(meta_file.read_text())
    print(f"  Version     : {meta['version']}")
    print(f"  Installed at: {meta['installed_at']}")
    print(f"  Location    : {meta['install_dir']}")
    print(f"  Dashboard   : http://127.0.0.1:{meta['dashboard_port']}")
    print(f"  Python      : {meta['python']}")
    print()

    for name in meta["repos"]:
        repo_dir = install_dir / name
        exists = repo_dir.exists()
        status_icon = "\033[92m[OK]\033[0m" if exists else "\033[91m[--]\033[0m"
        desc = next((r["desc"] for r in REPOS if r["name"] == name), "")
        print(f"  {status_icon} {name:<30} {desc}")

    print()
    print_storage_guide(install_dir)


def start_dashboard(install_dir: Path):
    scc_dir = install_dir / "security-command-center"
    if not scc_dir.exists():
        err("Security Command Center not found. Run install first.")
        return
    log(f"Starting dashboard on http://127.0.0.1:{DASHBOARD_PORT}")
    if platform.system() == "Windows":
        subprocess.Popen(
            [sys.executable, "server.py", "--port", str(DASHBOARD_PORT)],
            cwd=scc_dir, creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        subprocess.Popen(
            [sys.executable, "server.py", "--port", str(DASHBOARD_PORT)],
            cwd=scc_dir, start_new_session=True
        )
    time.sleep(2)
    ok(f"Dashboard running at http://127.0.0.1:{DASHBOARD_PORT}")
    print(f"  Open in browser: http://127.0.0.1:{DASHBOARD_PORT}")


def print_storage_guide(install_dir: Path):
    print("  WHERE IS EVERYTHING STORED:")
    print(f"  {'='*55}")
    print(f"  Install root     : {install_dir}")
    print(f"  Scan reports     : <tool>/reports/*.json, *.html")
    print(f"  Audit logs       : ai-governance-framework/data/audit_log.jsonl")
    print(f"  Firewall logs    : personal-firewall/logs/firewall_alerts.jsonl")
    print(f"  Dashboard DB     : security-command-center/data/scc.db")
    print(f"  Threat intel     : <tool>/threat_intel.json (auto-updated daily)")
    print(f"  Firewall IPs     : personal-firewall/rules/threat_intel_ips.json")
    print(f"  WAF payloads     : waf-bypass-lab/payloads/*.json")
    print(f"  Compliance rules : compliance-gap-analyzer/frameworks/*.json")
    print(f"  Governance policy: ai-governance-framework/policies/*.json")
    print(f"  SaaS inventory   : saas-security-posture/data/saas_inventory.json")
    print(f"  ITDR events      : itdr-engine/data/identity_events.json")


def print_guide(install_dir: Path):
    print(f"""
    ============================================================
       INSTALLATION COMPLETE
    ============================================================

    Dashboard URL : http://127.0.0.1:{DASHBOARD_PORT}

    QUICK COMMANDS:
      Start dashboard  : python master_setup.py start
      Stop dashboard   : python master_setup.py stop
      Check status     : python master_setup.py status
      Full uninstall   : python master_setup.py uninstall

    INDIVIDUAL TOOLS (run from their directory):
      cd {install_dir}/ai-sast-scanner
        python scanner.py <your-code-directory>

      cd {install_dir}/cloud-misconfig-hunter
        python hunter.py <your-terraform-directory>

      cd {install_dir}/prompt-injection-proxy
        python proxy.py  (starts on http://127.0.0.1:5001)

      cd {install_dir}/compliance-gap-analyzer
        python analyzer.py <your-policy.md>

      cd {install_dir}/waf-bypass-lab
        python waf_lab.py <target-url> --i-am-authorized-to-test

      cd {install_dir}/ai-governance-framework
        python governance.py --demo

      cd {install_dir}/saas-security-posture
        python analyzer.py

      cd {install_dir}/itdr-engine
        python itdr.py

      cd {install_dir}/personal-firewall
        python firewall.py monitor

    AUTO-START:
      The dashboard starts automatically on boot.
      To disable: delete the shortcut from Windows Startup folder.
    """)
    print_storage_guide(install_dir)
    print(f"""
    UNINSTALL:
      python master_setup.py uninstall
      This removes ALL files, startup entries, and services.
      Nothing is left behind.

    ============================================================
       Built by {AUTHOR} | {GITHUB}
    ============================================================
    """)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description=f"{SUITE_NAME} — Master Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=["install", "uninstall", "status", "start", "stop"],
                        help="install | uninstall | status | start | stop")
    parser.add_argument("--dir", type=Path, default=DEFAULT_INSTALL,
                        help=f"Install directory (default: {DEFAULT_INSTALL})")
    parser.add_argument("--skip-tests", action="store_true",
                        help="Skip self-tests during install")
    parser.add_argument("--no-persist", action="store_true",
                        help="Don't set up auto-start on boot")
    args = parser.parse_args()

    if args.command == "install":
        install(args.dir, args.skip_tests, args.no_persist)
    elif args.command == "uninstall":
        uninstall(args.dir)
    elif args.command == "status":
        status(args.dir)
    elif args.command == "start":
        start_dashboard(args.dir)
    elif args.command == "stop":
        if platform.system() == "Windows":
            subprocess.run(
                f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{DASHBOARD_PORT}\') do taskkill /F /PID %a',
                shell=True, capture_output=True
            )
        else:
            subprocess.run(["pkill", "-f", f"server.py.*{DASHBOARD_PORT}"], capture_output=True)
        ok("Dashboard stopped.")


if __name__ == "__main__":
    main()
