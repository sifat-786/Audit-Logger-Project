"""
audit_logger.py — Structured Audit Trail for AI Agent Actions

Refactored to include:
- event_id
- timestamp
- user_instruction
- external_content_involved
- tool_used
- agent_action
- data_accessed
- risk_level (including CRITICAL)
- decision: approved / need approval / reject
"""

import json
import csv
import sqlite3
import uuid
import threading
from datetime import datetime, timezone
from pathlib import Path

# =====================================================
# CONFIGURATION
# =====================================================

AUDIT_LOG_JSON_PATH = Path(__file__).parent.parent / "logs" / "audit_log.json"
AUDIT_LOG_CSV_PATH = Path(__file__).parent.parent / "logs" / "audit_log.csv"
AUDIT_LOG_DB_PATH = Path(__file__).parent.parent / "logs" / "audit_log.db"

# Ensure logs folder exists
AUDIT_LOG_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

# In-memory log buffer — allows Streamlit to read without file I/O
_log_buffer: list[dict] = []
_buffer_lock = threading.Lock()

# Session ID is generated once per process lifetime
SESSION_ID = str(uuid.uuid4())[:8].upper()


# =====================================================
# RISK LEVEL MAP
# =====================================================

RISK_LEVELS = {
    "NONE": {
        "label": "NONE",
        "color": "#6b7280",   # gray
        "icon": "⚪",
        "description": "No real-world side effects"
    },
    "LOW": {
        "label": "LOW",
        "color": "#10b981",   # green
        "icon": "🟢",
        "description": "Read-only operation"
    },
    "MEDIUM": {
        "label": "MEDIUM",
        "color": "#f59e0b",   # amber
        "icon": "🟡",
        "description": "Action with minor external side effect"
    },
    "HIGH": {
        "label": "HIGH",
        "color": "#ef4444",   # red
        "icon": "🔴",
        "description": "Destructive or irreversible action"
    },
    "CRITICAL": {
        "label": "CRITICAL",
        "color": "#7f1d1d",   # dark red
        "icon": "💀",
        "description": "Catastrophic or severe security impact"
    }
}


# =====================================================
# INITIALIZE SQLITE DB
# =====================================================

def _init_sqlite_db():
    conn = sqlite3.connect(AUDIT_LOG_DB_PATH)
    cursor = conn.cursor()
    
    # Check if table exists and has the new event_id column. If not, reset it.
    try:
        cursor.execute("SELECT event_id FROM audit_logs LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("DROP TABLE IF EXISTS audit_logs")
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            event_id TEXT PRIMARY KEY,
            session_id TEXT,
            timestamp TEXT,
            user_instruction TEXT,
            intent TEXT,
            tool_used TEXT,
            agent_action TEXT,
            external_content_involved TEXT,
            data_accessed TEXT,
            risk_level TEXT,
            decision TEXT,
            parameters TEXT,
            status TEXT,
            reasoning TEXT,
            result_summary TEXT,
            error_message TEXT
        )
    ''')
    conn.commit()
    conn.close()

_init_sqlite_db()

# =====================================================
# LOAD EXISTING LOGS ON MODULE IMPORT
# =====================================================

def _load_existing_logs() -> list[dict]:
    """Load logs from disk into memory buffer on startup."""
    try:
        if AUDIT_LOG_JSON_PATH.exists():
            with open(AUDIT_LOG_JSON_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
                if logs and "event_id" not in logs[0]:
                    # Schema mismatch, discard and delete files
                    try:
                        AUDIT_LOG_JSON_PATH.unlink()
                        AUDIT_LOG_CSV_PATH.unlink()
                    except Exception:
                        pass
                    return []
                return logs
    except Exception:
        pass
    return []


with _buffer_lock:
    _log_buffer = _load_existing_logs()


# =====================================================
# CORE LOGGING FUNCTION
# =====================================================

def log_action(
    user_instruction: str,
    intent: str,
    tool_used: str,
    agent_action: str,
    external_content_involved: str,
    data_accessed: str,
    risk_level: str,
    decision: str,
    parameters: dict,
    status: str,
    reasoning: str,
    result_summary: str = "",
    error_message: str = "",
    event_id: str = None
) -> dict:
    """
    Log a single agent action to both memory buffer and disk.

    Returns the log entry dict so callers can display it immediately.
    """

    if not event_id:
        event_id = f"EV-{str(uuid.uuid4())[:6].upper()}"
    timestamp = datetime.now(timezone.utc).isoformat()

    # Normalise risk_level
    risk_level = risk_level.upper() if risk_level else "NONE"
    if risk_level not in RISK_LEVELS:
        risk_level = "NONE"

    log_entry = {
        "session_id":                 SESSION_ID,
        "event_id":                   event_id,
        "timestamp":                  timestamp,
        "user_instruction":           user_instruction,
        "intent":                     intent,
        "tool_used":                  tool_used,
        "agent_action":               agent_action,
        "external_content_involved":  external_content_involved,
        "data_accessed":              data_accessed,
        "risk_level":                 risk_level,
        "decision":                   decision,       # approved | need approval | reject
        "parameters":                 parameters,
        "status":                     status,         # SUCCESS | FAILED | SKIPPED
        "reasoning":                  reasoning,
        "result_summary":             result_summary,
        "error_message":              error_message
    }

    # Thread-safe in-memory append
    with _buffer_lock:
        _log_buffer.append(log_entry)
        _persist_logs(_log_buffer)

    return log_entry


# =====================================================
# PERSISTENCE
# =====================================================

def _persist_logs(logs: list[dict]) -> None:
    """Write current buffer to disk (called within lock)."""
    # 1. JSON Persistence
    try:
        with open(AUDIT_LOG_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[AUDIT WARNING] Could not persist log to JSON: {e}")
        
    # 2. CSV Persistence
    if not logs:
        return
    try:
        keys = logs[0].keys()
        with open(AUDIT_LOG_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for log in logs:
                row = dict(log)
                row['parameters'] = json.dumps(row.get('parameters', {}))
                writer.writerow(row)
    except Exception as e:
        print(f"[AUDIT WARNING] Could not persist log to CSV: {e}")

# 3. SQLite Persistence
    try:
        conn = sqlite3.connect(AUDIT_LOG_DB_PATH)
        cursor = conn.cursor()
        
        for log in logs:
            cursor.execute('''
                INSERT OR IGNORE INTO audit_logs (
                    event_id, session_id, timestamp, user_instruction, intent, 
                    tool_used, agent_action, external_content_involved, data_accessed, 
                    risk_level, decision, parameters, status, reasoning, 
                    result_summary, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log['event_id'], log['session_id'], log['timestamp'], log['user_instruction'], log['intent'],
                log['tool_used'], log['agent_action'], log['external_content_involved'], log['data_accessed'],
                log['risk_level'], log['decision'], json.dumps(log.get('parameters', {})), 
                log['status'], log['reasoning'], log['result_summary'], log['error_message']
            ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AUDIT WARNING] Could not persist log to SQLite: {e}")


# =====================================================
# READ FUNCTIONS (used by Streamlit dashboard)
# =====================================================

def get_all_logs() -> list[dict]:
    """Return a copy of the full in-memory log buffer."""
    with _buffer_lock:
        return list(_log_buffer)


def get_recent_logs(n: int = 20) -> list[dict]:
    """Return the N most recent log entries, newest first."""
    with _buffer_lock:
        return list(reversed(_log_buffer[-n:]))


def get_logs_by_risk(risk_level: str) -> list[dict]:
    """Filter logs by risk level."""
    with _buffer_lock:
        return [e for e in _log_buffer if e.get("risk_level") == risk_level.upper()]


def get_session_stats() -> dict:
    """Aggregate stats for the current session only."""
    with _buffer_lock:
        session_logs = [e for e in _log_buffer if e.get("session_id") == SESSION_ID]

    total = len(session_logs)
    tools_used = [e["tool_used"] for e in session_logs if e.get("tool_used") not in ("NONE", "")]
    risk_counts = {"NONE": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for e in session_logs:
        rl = e.get("risk_level", "NONE")
        risk_counts[rl] = risk_counts.get(rl, 0) + 1

    return {
        "session_id":   SESSION_ID,
        "total_actions": total,
        "tools_invoked": len(tools_used),
        "unique_tools":  len(set(tools_used)),
        "risk_counts":   risk_counts,
        "success_rate":  (
            round(sum(1 for e in session_logs if e.get("status") == "SUCCESS") / total * 100, 1)
            if total > 0 else 0.0
        )
    }
