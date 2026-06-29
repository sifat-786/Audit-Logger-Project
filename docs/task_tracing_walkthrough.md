# Task Tracing Walkthrough
## Iris AI Audit Agent — Proof of Completion

This walkthrough traces **each of the 8 project tasks** to the exact files and line numbers in the codebase so you can verify everything yourself.

---

## Task 1 — Study How OpenClaw-Style Agents Perform Actions

> **Goal**: Understand how AI agents use tools/skills to act on behalf of users.

### Where to look:
| What | File | What you'll see |
|------|------|-----------------|
| OpenClaw skill config | [openclaw_fixed.json](file:///d:/Antigravity/Projects/Audit-Logger-Project/openclaw_fixed.json) | The raw JSON defining how OpenClaw skills are declared (tool names, descriptions, parameters) |
| Our tool wrappers | [tools/generic_tools.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/tools/generic_tools.py) | 10+ tool functions (`read_file`, `write_file`, `search_web`, `execute_terminal_command`, etc.) that the agent can invoke |
| Gmail tool integration | [tools/gmail_tool.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/tools/gmail_tool.py) | Real Gmail API wrappers (`read_recent_emails`, `read_email_content`, `send_email`) using OAuth 2.0 |
| LangChain tool binding | [agent/controller.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/controller.py) | Each raw tool function is wrapped with `@tool` decorator and bound to the LLM |

### How to verify:
1. Open `agent/controller.py` — you'll see `@tool`-decorated functions and the `tools` list.
2. Open `tools/generic_tools.py` — these are the actual implementations the agent calls.
3. The LLM autonomously picks which tool to call based on the user's query (`ai_msg = _llm_with_tools.invoke(...)`).

---

## Task 2 — Identify Why Agent Actions Need Audit Logging

> **Goal**: Document the rationale for transparency, traceability, and human-in-the-loop validation.

### Where to look:
| What | File |
|------|------|
| Comprehensive project report | [docs/comprehensive_project_report.tex](file:///d:/Antigravity/Projects/Audit-Logger-Project/docs/comprehensive_project_report.tex) |
| Final project report | [docs/final_project_report.md](file:///d:/Antigravity/Projects/Audit-Logger-Project/docs/final_project_report.md) |
| Risk policy document | [docs/risk_policy.md](file:///d:/Antigravity/Projects/Audit-Logger-Project/docs/risk_policy.md) |
| Explanation engine | [agent/explanation_engine.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/explanation_engine.py) |

### How to verify:
1. Open `docs/final_project_report.md` — Section 1 explains **why** audit logging is needed (accountability, security, compliance).
2. Open `docs/risk_policy.md` — documents the policy framework: which actions are safe, which need approval, which are blocked.
3. Open `agent/explanation_engine.py` — each tool action gets a human-readable explanation string (e.g. *"This action reads your recent Gmail inbox. Read-only, no side effects."*).

---

## Task 3 — Prepare a Taxonomy of Risky Agent Actions

> **Goal**: Create a 5-tier classification: NONE → LOW → MEDIUM → HIGH → CRITICAL

### Where to look:
| What | File |
|------|------|
| Risk level definitions | [agent/risk_classifier.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/risk_classifier.py) |
| Approval matrix | [agent/risk_classifier.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/risk_classifier.py) |
| Action → risk mapping | [agent/risk_classifier.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/risk_classifier.py) |

### How to verify:
Open `agent/risk_classifier.py` and you'll see **three key data structures**:

```python
# The 5-tier taxonomy
RISK_LEVELS = {
    "NONE":     "No real-world side effects",
    "LOW":      "Read-only external access",
    "MEDIUM":   "Action with external side effect",
    "HIGH":     "Destructive or irreversible action",
    "CRITICAL": "Catastrophic or severe security impact"
}

# Which levels need approval
APPROVAL_MATRIX = {
    "NONE": False, "LOW": False, "MEDIUM": False,
    "HIGH": True, "CRITICAL": True
}

# Every tool mapped to its risk tier
ACTION_RISK_MAP = {
    "read_recent_emails": "LOW",
    "send_email": "HIGH",
    "execute_terminal_command": "CRITICAL",
    # ... 50+ more mappings
}
```

---

## Task 4 — Create 50–70 Agent-Action Test Scenarios

> **Goal**: Build a comprehensive catalogue of test cases.

### Where to look:
| What | File |
|------|------|
| Full scenario catalogue | [evaluation/scenario_catalogue.csv](file:///d:/Antigravity/Projects/Audit-Logger-Project/evaluation/scenario_catalogue.csv) |

### How to verify:
1. Open `evaluation/scenario_catalogue.csv`.
2. Count the rows: **70 scenarios** (SCN-001 through SCN-070).
3. Each row has: `scenario_id`, `user_request`, `agent_action`, `tool_used`, `risk_level`, `approval_required`, `explanation`.

---

## Task 5 — Divide Scenarios into Risk Tiers

> **Goal**: Each scenario must be tagged as safe/medium/high/critical.

### How to verify:
In `evaluation/scenario_catalogue.csv`, check the `risk_level` column:

| Risk Level | Example Scenarios | Count |
|------------|------------------|-------|
| **LOW** | SCN-001 (weather), SCN-003 (read email), SCN-006 (read file), SCN-026 (calculate) | ~20 |
| **MEDIUM** | SCN-007 (draft email), SCN-011 (create note), SCN-027 (create spreadsheet) | ~15 |
| **HIGH** | SCN-014 (send email), SCN-025 (book flight), SCN-045 (cancel meeting) | ~15 |
| **CRITICAL** | SCN-018 (delete account), SCN-020 (transfer money), SCN-022 (wipe database) | ~20 |

Every scenario has `approval_required` set to `TRUE` or `FALSE` matching the risk tier.

---

## Task 6 — Include Email-Specific Scenarios

> **Goal**: Reading, sending, drafting, summarizing, forwarding email scenarios.

### Where to look:
In [evaluation/scenario_catalogue.csv](file:///d:/Antigravity/Projects/Audit-Logger-Project/evaluation/scenario_catalogue.csv), these email scenarios exist:

| ID | Action | Risk |
|----|--------|------|
| SCN-003 | Read latest email | LOW |
| SCN-007 | Draft email to John | MEDIUM |
| SCN-014 | Send email to client | HIGH |
| SCN-029 | Delete all emails | CRITICAL |
| **SCN-066** | Summarize emails from Alice | LOW |
| **SCN-067** | Flag emails from finance as urgent | MEDIUM |
| **SCN-068** | Find attachments in unread emails | LOW |
| **SCN-069** | Draft reply to newsletter | MEDIUM |
| **SCN-070** | Forward invoice to accounting | HIGH |

---

## Task 7 — Design a Structured Audit-Log Schema

> **Goal**: Define the exact JSON/SQLite/CSV schema for audit records.

### Where to look:
| What | File |
|------|------|
| Schema documentation | [docs/schema_documentation.md](file:///d:/Antigravity/Projects/Audit-Logger-Project/docs/schema_documentation.md) |
| Schema implementation | [agent/audit_logger.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/audit_logger.py) |

### How to verify:
1. Open `docs/schema_documentation.md` — full documentation of every field, its type, and purpose.
2. Open `agent/audit_logger.py` — the `log_action()` function constructs the record dict and writes to JSON, SQLite, and CSV simultaneously.

---

## Task 8 — Each Audit Record Must Contain the Exact Fields

> **Goal**: `event_id`, `timestamp`, `user_instruction`, `external_content_involved`, `tool_used`, `agent_action`, `data_accessed`, `risk_level`, `decision`

### Where to look:
| What | File |
|------|------|
| Record construction | [agent/audit_logger.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/audit_logger.py) |
| Dynamic field extraction | [agent/controller.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/controller.py) |
| Decision engine | [agent/decision_engine.py](file:///d:/Antigravity/Projects/Audit-Logger-Project/agent/decision_engine.py) |

### How to verify — **field by field**:

Open `agent/controller.py` and trace each field:

| Required Field | Where It's Set | Evidence |
|----------------|---------------|----------|
| `event_id` | `agent/audit_logger.py` → `log_action()` | Generated as `"EV-" + random hex` |
| `timestamp` | `agent/audit_logger.py` → `log_action()` | `datetime.now(timezone.utc).isoformat()` |
| `user_instruction` | `agent/controller.py` | Passed as `user_instruction=user_query` |
| `external_content_involved` | `agent/controller.py` | Dynamic per-tool extraction (e.g. `"Gmail Inbox API"`, `"Local File System (report.txt)"`) |
| `tool_used` | `agent/controller.py` | `tool_used=tool_name` (the LangChain function name) |
| `agent_action` | `agent/controller.py` | `agent_action=tool_name` |
| `data_accessed` | `agent/controller.py` | Dynamic per-tool (e.g. `"List of 5 recent emails"`, `"Outbound email content"`) |
| `risk_level` | `agent/controller.py` | From `generate_explanation(tool_name)` → `risk_classifier.py` |
| `decision` | `agent/controller.py` | Returns lowercase: `"approved"`, `"need approval"`, or `"reject"` |

---

## Quick-Reference File Map

| Task | Primary File(s) |
|------|----------------|
| 1. OpenClaw study | `agent/controller.py`, `tools/generic_tools.py`, `openclaw_fixed.json` |
| 2. Why audit logging | `docs/final_project_report.md`, `docs/risk_policy.md` |
| 3. Risk taxonomy | `agent/risk_classifier.py` |
| 4. 70 test scenarios | `evaluation/scenario_catalogue.csv` |
| 5. Risk tier division | `evaluation/scenario_catalogue.csv` → `risk_level` column |
| 6. Email scenarios | `evaluation/scenario_catalogue.csv` → SCN-003/007/014/029/066-070 |
| 7. Schema design | `docs/schema_documentation.md`, `agent/audit_logger.py` |
| 8. Exact audit fields | `agent/audit_logger.py`, `agent/controller.py` |
