"""
Security Command Center - unified dashboard for the AI Security Projects suite.

Orchestrates and visualizes results from all 5 tools:
  1. AI SAST Scanner
  2. Cloud Misconfiguration Hunter
  3. Prompt Injection Proxy
  4. Compliance Gap Analyzer
  5. WAF Bypass Lab

Architecture:
  - Flask web server
  - SQLite persistence (scan history, trend data)
  - Subprocess runners for each tool (expects sibling repos or --tool-dir flag)
  - Single-page dashboard (HTML + vanilla JS, no build step)

Author: Mohith Vasamsetti (CyberEnthusiastic)
License: MIT
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "scc.db"

# Default sibling directories - each tool is expected to be cloned next to this one
DEFAULT_TOOL_PATHS = {
    "sast":       "../ai-sast-scanner",
    "cloud":      "../cloud-misconfig-hunter",
    "prompt":     "../prompt-injection-proxy",
    "compliance": "../compliance-gap-analyzer",
    "waf":        "../waf-bypass-lab",
}

TOOL_METADATA = {
    "sast": {
        "name": "AI SAST Scanner",
        "icon": "shield",
        "color": "#60a5fa",
        "description": "Static code analysis for SQLi, XSS, secrets, weak crypto, etc.",
        "entry": "scanner.py",
        "default_args": ["samples/"],
    },
    "cloud": {
        "name": "Cloud Misconfig Hunter",
        "icon": "cloud",
        "color": "#34d399",
        "description": "CIS-mapped AWS IaC misconfiguration scanner.",
        "entry": "hunter.py",
        "default_args": ["samples/"],
    },
    "prompt": {
        "name": "Prompt Injection Proxy",
        "icon": "brain",
        "color": "#a78bfa",
        "description": "Hybrid ML + heuristic prompt injection classifier.",
        "entry": "benchmark.py",
        "default_args": [],
    },
    "compliance": {
        "name": "Compliance Gap Analyzer",
        "icon": "file-check",
        "color": "#fbbf24",
        "description": "RAG-based policy analyzer for SOC 2 and ISO 27001.",
        "entry": "analyzer.py",
        "default_args": ["samples/acme_security_policy.md"],
    },
    "waf": {
        "name": "WAF Bypass Lab",
        "icon": "swords",
        "color": "#f87171",
        "description": "Defensive WAF coverage assessment.",
        "entry": "waf_lab.py",
        "default_args": ["http://127.0.0.1:8088", "--i-am-authorized-to-test", "--delay-ms", "5"],
    },
}


# -----------------------------------------------------------
# SQLite persistence
# -----------------------------------------------------------
def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            tool TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            summary_json TEXT,
            raw_output TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_scans_tool ON scans(tool);
        CREATE INDEX IF NOT EXISTS idx_scans_started ON scans(started_at);
    """)
    conn.commit()
    conn.close()


def save_scan(tool: str, status: str, summary: dict, raw: str, scan_id: Optional[str] = None) -> str:
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).isoformat()
    sid = scan_id or str(uuid.uuid4())
    if scan_id:
        conn.execute(
            "UPDATE scans SET finished_at=?, status=?, summary_json=?, raw_output=? WHERE id=?",
            (now, status, json.dumps(summary), raw[-8000:], scan_id),
        )
    else:
        conn.execute(
            "INSERT INTO scans (id, tool, started_at, finished_at, status, summary_json, raw_output) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sid, tool, now, now, status, json.dumps(summary), raw[-8000:]),
        )
    conn.commit()
    conn.close()
    return sid


def list_scans(tool: Optional[str] = None, limit: int = 50) -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if tool:
        rows = conn.execute(
            "SELECT * FROM scans WHERE tool=? ORDER BY started_at DESC LIMIT ?",
            (tool, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM scans ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "tool": r["tool"],
            "started_at": r["started_at"],
            "finished_at": r["finished_at"],
            "status": r["status"],
            "summary": json.loads(r["summary_json"]) if r["summary_json"] else {},
        }
        for r in rows
    ]


def get_scan(scan_id: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "tool": row["tool"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "status": row["status"],
        "summary": json.loads(row["summary_json"]) if row["summary_json"] else {},
        "raw_output": row["raw_output"],
    }


# -----------------------------------------------------------
# Tool execution
# -----------------------------------------------------------
def resolve_tool_path(tool_key: str, config: Dict[str, str]) -> Optional[Path]:
    p = config.get(tool_key) or DEFAULT_TOOL_PATHS.get(tool_key)
    if not p:
        return None
    candidate = (BASE_DIR / p).resolve()
    if candidate.exists():
        return candidate
    return None


def run_tool(tool_key: str, tool_dir: Path, extra_args: Optional[List[str]] = None) -> dict:
    meta = TOOL_METADATA[tool_key]
    entry = meta["entry"]
    args = meta["default_args"][:]
    if extra_args:
        args = extra_args

    cmd = [sys.executable, entry] + args
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(tool_dir),
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout + "\n---STDERR---\n" + result.stderr
        status = "success" if result.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        output = "Timeout after 300s"
        status = "timeout"
    except Exception as e:
        output = f"Error: {e}"
        status = "error"

    # Try to parse a JSON report from the tool's reports/ directory
    summary = {}
    reports_dir = tool_dir / "reports"
    if reports_dir.exists():
        json_files = sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if json_files:
            try:
                data = json.loads(json_files[0].read_text(encoding="utf-8"))
                summary = data.get("summary", data)
            except Exception:
                pass

    return {"status": status, "summary": summary, "output": output}


# -----------------------------------------------------------
# Flask routes
# -----------------------------------------------------------
@app.route("/")
def index():
    return render_template("dashboard.html", tools=TOOL_METADATA)


@app.route("/api/tools")
def api_tools():
    config = app.config.get("TOOL_PATHS", {})
    resolved = {}
    for key, meta in TOOL_METADATA.items():
        path = resolve_tool_path(key, config)
        resolved[key] = {
            **meta,
            "installed": path is not None,
            "path": str(path) if path else None,
        }
    return jsonify(resolved)


@app.route("/api/scans")
def api_scans():
    tool = request.args.get("tool")
    limit = int(request.args.get("limit", 50))
    return jsonify(list_scans(tool=tool, limit=limit))


@app.route("/api/scans/<scan_id>")
def api_scan_detail(scan_id):
    s = get_scan(scan_id)
    if not s:
        return jsonify({"error": "not found"}), 404
    return jsonify(s)


@app.route("/api/run/<tool_key>", methods=["POST"])
def api_run(tool_key):
    if tool_key not in TOOL_METADATA:
        return jsonify({"error": "unknown tool"}), 404
    config = app.config.get("TOOL_PATHS", {})
    tool_dir = resolve_tool_path(tool_key, config)
    if not tool_dir:
        return jsonify({
            "error": f"Tool '{tool_key}' not found. Clone the sibling repo or set the path in config.json",
            "expected_path": DEFAULT_TOOL_PATHS.get(tool_key),
        }), 404

    payload = request.get_json(silent=True) or {}
    extra_args = payload.get("args")

    result = run_tool(tool_key, tool_dir, extra_args)
    scan_id = save_scan(
        tool=tool_key,
        status=result["status"],
        summary=result["summary"],
        raw=result["output"],
    )
    return jsonify({
        "scan_id": scan_id,
        "status": result["status"],
        "summary": result["summary"],
    })


@app.route("/api/stats")
def api_stats():
    """Aggregate stats across all scans - for the dashboard header."""
    scans = list_scans(limit=500)
    by_tool = {}
    for s in scans:
        t = s["tool"]
        by_tool.setdefault(t, {"runs": 0, "last_run": None, "last_summary": {}})
        by_tool[t]["runs"] += 1
        if by_tool[t]["last_run"] is None or s["started_at"] > by_tool[t]["last_run"]:
            by_tool[t]["last_run"] = s["started_at"]
            by_tool[t]["last_summary"] = s["summary"]
    return jsonify({
        "total_scans": len(scans),
        "by_tool": by_tool,
        "last_scan": scans[0] if scans else None,
    })


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok", "version": "1.0.0"})


# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Security Command Center")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5500)
    parser.add_argument("--config", default="config.json",
                        help="JSON file with tool paths (optional)")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    # Load config if present
    config_path = BASE_DIR / args.config
    tool_paths = {}
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            tool_paths = cfg.get("tool_paths", {})
        except Exception as e:
            print(f"[!] Failed to load {config_path}: {e}")
    app.config["TOOL_PATHS"] = tool_paths

    init_db()

    print("=" * 60)
    print("   SECURITY COMMAND CENTER v1.0")
    print("   Unified dashboard for the AI Security Projects suite")
    print("=" * 60)
    print(f"   Dashboard: http://{args.host}:{args.port}")
    print(f"   Database : {DB_PATH}")
    print(f"   Tool discovery:")
    for key, meta in TOOL_METADATA.items():
        path = resolve_tool_path(key, tool_paths)
        status = "[OK]" if path else "[--]"
        label = f"{meta['name']:<28}"
        location = str(path) if path else "not found (clone sibling repo)"
        print(f"     {status} {label} {location}")
    print("=" * 60)
    print()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
