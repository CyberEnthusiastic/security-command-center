# Complete Setup Guide — AI Security Projects Suite

## One-Command Install (Windows / Mac / Linux)

```bash
# 1. Clone the Command Center
git clone https://github.com/CyberEnthusiastic/security-command-center.git
cd security-command-center

# 2. Install the ENTIRE suite (all 10 tools)
python master_setup.py install

# 3. Open the dashboard
# Browser opens automatically, or go to:
# http://127.0.0.1:5500
```

That's it. The installer:
- Clones all 10 security tool repos
- Installs all Python dependencies
- Runs self-tests on every tool
- Sets up auto-start on boot (dashboard survives shutdown/restart)
- Prints a complete guide

---

## What Gets Installed

```
C:\Users\<you>\AppData\Local\SecuritySuite\     (Windows)
~/.security-suite/                               (Mac/Linux)
│
├── security-command-center/     ← Dashboard (port 5500)
├── ai-sast-scanner/             ← Code vulnerability scanner
├── cloud-misconfig-hunter/      ← AWS IaC security
├── prompt-injection-proxy/      ← LLM firewall (port 5001)
├── compliance-gap-analyzer/     ← SOC2/ISO27001 analyzer
├── waf-bypass-lab/              ← WAF coverage tester
├── ai-governance-framework/     ← AI tool DLP + RBAC
├── saas-security-posture/       ← SaaS security dashboard
├── itdr-engine/                 ← Identity threat detection
├── personal-firewall/           ← Network monitor + firewall
│
├── start_dashboard.bat          ← Start the dashboard
├── stop_dashboard.bat           ← Stop the dashboard
└── install_meta.json            ← Install metadata
```

---

## Where Results Are Stored

| Data | Location |
|------|----------|
| **SAST scan reports** | `ai-sast-scanner/reports/sast_report.json` + `.html` |
| **Cloud misconfig reports** | `cloud-misconfig-hunter/reports/cloud_report.json` + `.html` |
| **Prompt injection benchmark** | Terminal output (100% F1) |
| **Compliance gap reports** | `compliance-gap-analyzer/reports/gap_report.json` + `.html` |
| **WAF coverage reports** | `waf-bypass-lab/reports/waf_report.json` + `.html` |
| **AI governance reports** | `ai-governance-framework/reports/governance_report.json` + `.html` |
| **SaaS posture reports** | `saas-security-posture/reports/saas_report.json` + `.html` |
| **ITDR alerts** | `itdr-engine/reports/itdr_report.json` + `.html` |
| **Firewall alerts** | `personal-firewall/logs/firewall_alerts.jsonl` |
| **Dashboard scan history** | `security-command-center/data/scc.db` (SQLite) |
| **Audit trail (AI governance)** | `ai-governance-framework/data/audit_log.jsonl` |
| **Threat intel (auto-updated)** | `<each-tool>/threat_intel.json` |
| **Firewall blocked IPs** | `personal-firewall/rules/threat_intel_ips.json` |

All reports are **HTML (open in any browser)** + **JSON (machine-readable for CI/CD)**.

---

## Daily Operations

### View the Dashboard
```
http://127.0.0.1:5500
```
The dashboard shows all 10 tools, their last scan results, and full history.
Click "Run" on any tool to execute it. Click "History" to see all past runs.

### Run Individual Tools

```bash
# Scan your code for vulnerabilities
cd ai-sast-scanner
python scanner.py /path/to/your/code

# Scan your Terraform for misconfigs
cd cloud-misconfig-hunter
python hunter.py /path/to/your/terraform

# Test your WAF coverage
cd waf-bypass-lab
python waf_lab.py https://your-staging-url --i-am-authorized-to-test

# Analyze your security policy
cd compliance-gap-analyzer
python analyzer.py /path/to/your/policy.md

# Start the LLM firewall
cd prompt-injection-proxy
python proxy.py
# → http://127.0.0.1:5001

# Check your AI tool governance
cd ai-governance-framework
python governance.py --scan "paste any prompt here"

# Analyze your SaaS inventory
cd saas-security-posture
python analyzer.py -i /path/to/your/inventory.json

# Detect identity threats
cd itdr-engine
python itdr.py -i /path/to/your/identity_logs.json

# Monitor your network
cd personal-firewall
python firewall.py monitor
```

### View Reports
Every tool generates an interactive HTML report. Open it in any browser:
```bash
# Windows
start reports/sast_report.html

# Mac
open reports/sast_report.html

# Linux
xdg-open reports/sast_report.html
```

---

## Persistence (Survives Shutdown/Restart)

The installer automatically adds the dashboard to your system's startup:

**Windows:** A `.bat` file is placed in:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```
The dashboard starts automatically when you log in.

**Linux/Mac:** A systemd user service is created:
```
~/.config/systemd/user/security-dashboard.service
```
Auto-starts on login.

### Manual Start/Stop
```bash
# Start
python master_setup.py start

# Stop
python master_setup.py stop

# Check status
python master_setup.py status
```

---

## Complete Uninstall

```bash
python master_setup.py uninstall
```

This removes:
- All 10 tool directories
- All generated reports, logs, and databases
- Windows Startup shortcut / systemd service
- Install metadata

**Nothing is left behind.** No registry entries, no hidden files, no orphan services.

---

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.11+ |
| Git | any | latest |
| RAM | 512 MB | 2 GB |
| Disk | 200 MB | 500 MB |
| OS | Windows 10+ / macOS 12+ / Ubuntu 20+ | Any |
| Network | Optional (for threat intel updates) | Recommended |
| Browser | Any modern browser | Chrome/Firefox |

**No Docker required.** No Node.js. No Java. No cloud accounts. No API keys.
Just Python and Git.

---

## Troubleshooting

**"python is not recognized"**
→ Install Python from https://python.org and check "Add to PATH" during install.

**"git is not recognized"**
→ Install Git from https://git-scm.com

**Dashboard won't start**
→ Check if port 5500 is in use: `netstat -ano | findstr :5500`
→ Use a different port: `python server.py --port 5501`

**A tool fails its self-test**
→ Check the tool's README.md for specific requirements
→ Most tools are zero-dependency (pure Python stdlib)
→ Only prompt-injection-proxy needs Flask (`pip install flask`)

**Reports are empty**
→ Run the tool first, then open the report
→ Reports are generated in each tool's `reports/` directory

---

Built by **Mohith Vasamsetti** | [github.com/CyberEnthusiastic](https://github.com/CyberEnthusiastic)
