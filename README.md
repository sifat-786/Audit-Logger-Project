# Iris — Observability & Audit Logger AI Agent

Iris is a tool-agnostic AI agent framework integrated with a deterministic security governance layer and a premium real-time observability dashboard. 

The platform guarantees predictable agent execution, human-in-the-loop validation for risky behaviors, and tamper-resistant logging across three persistence layers (JSON, CSV, and SQLite).

---

## 🌟 Key Features

* **Controlled Intent Routing**: Replaces unpredictable ReAct loops with a deterministic single-turn router driven by Groq LLaMA 3.3 70B or Claude 3.5 Sonnet.
* **Risk Classification Matrix**: Evaluates and routes agent actions into four risk tiers:
  * ⚪ `NONE`: Normal conversation or math calculations (Auto-allowed).
  * 🟢 `LOW`: Read-only queries like checking emails or reading local files (Auto-allowed).
  * 🟡 `MEDIUM`: Internal state modifications like creating notes or writing local files (Auto-allowed).
  * 🔴 `HIGH`: Outbound operations like sending emails (Intercepted; requires human-in-the-loop approval).
  * 💀 `CRITICAL`: Destructive actions like python/bash execution or database drops (Systematically blocked).
* **Multi-Format Audit trail**: Simultaneously logs each action to `logs/audit_log.db` (SQLite), `logs/audit_log.json`, and `logs/audit_log.csv` using a thread-safe write-through logger.
* **WCAG 2.1 Compliant Dashboard**: Custom Streamlit user interface featuring a session timeline, clean HSL badges, a unified search card, and direct logs export capabilities.
* **Pre-Execution Typo Checker**: Pre-validates user queries to catch email typos (e.g., `@gmal.com` instead of `@gmail.com`) and displays correction recommendations.

---

## 📂 Project Structure

```
Audit-Logger-Project/
│
├── 📁 agent/                  # Core AI Agent & Security Governance Modules
│   ├── audit_logger.py        # Multi-format logger (SQLite, JSON, CSV)
│   ├── controller.py          # Controlled Intent Router orchestrator
│   ├── decision_engine.py     # Gating decisions (Allow, Hold, Reject)
│   ├── explanation_engine.py  # Generates real-time reasoning explanations
│   ├── query_validator.py     # Captures query typos and displays suggestions
│   └── risk_classifier.py     # Risk classification dictionary mapping
│
├── 📁 tools/                  # Extensible System and External Capabilities
│   ├── generic_tools.py       # Bound file system, web search, database, etc.
│   ├── gmail_tool.py          # Gmail API actions and credentials management
│   └── scheduler_tool.py      # Background task runner & callback logger
│
├── 📁 docs/                   # Reports, Academic LaTeX Paper, and Diagrams
│   ├── comprehensive_project_report.tex  # LaTeX academic report (includes Usability Study)
│   ├── final_project_report.md           # Markdown comprehensive final report
│   ├── user_study_report.md              # Usability study SUS scores
│   ├── project_tasks_completion.md       # Final project checklist summary
│   ├── iiitdm_logo.png                   # Institutional logo for LaTeX
│   ├── risk_policy.md                    # System security thresholds
│   ├── schema_documentation.md           # 9-field audit schema documentation
│   └── task_tracing_walkthrough.md      # Developer onboarding guide
│
├── 📁 evaluation/             # Programmatic Testing & Scenario Verification
│   ├── evaluate_scenarios.py             # Scenario test runner
│   ├── scenario_catalogue.csv            # 70 ground-truth test scenarios
│   ├── scenario_evaluation_report.md     # Markdown test verification report
│   └── scenario_results.json             # Programmatic test outcome JSON
│
├── 📁 logs/                   # Data Store and Audit Database Logs
│   ├── audit_log.json         # JSON audit trace
│   ├── audit_log.csv          # CSV tabular export
│   └── audit_log.db           # SQLite database
│
├── 📄 app.py                  # Streamlit Dashboard UI Entrypoint
├── 📄 style.css               # Premium CSS Stylesheet
└── 📄 run_iris.bat            # Double-click launcher shortcut
```

---

## 📊 Verification & Usability Metrics

### 1. Scenario Verification
Running the test harness (`python evaluation/evaluate_scenarios.py`) evaluates the governance system against **70 distinct test scenarios** (covering email, calendar, system configurations, and databases):
* **Risk Classification Accuracy**: **100.00% (70/70)**
* **Approval Requirement Correctness**: **100.00% (70/70)**
* **Log Schema Completeness**: **PASSED (100.00%)**

### 2. User Usability Study
A study involving **5 professional participants** measuring the efficiency and interface design of the dashboard yielded:
* **Task Success Rate**: **100.00%**
* **Average Time on Task**: **15.0 seconds**
* **System Usability Scale (SUS) Score**: **85.5 / 100** ("Excellent", Grade A)

---

## 🚀 Setup & Launch

### 1. Prerequisites
Make sure python is installed and your API keys are configured in your `.env` file in the root directory:
```bash
GROQ_API_KEY=your-groq-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. Launch Streamlit Dashboard
Simply double-click the **`run_iris.bat`** file in the root directory to activate the virtual environment and launch the platform:
```bash
# Or run manually:
venv\Scripts\activate
streamlit run app.py
```

### 3. Run Programmatic Evaluation
To verify the policy engine against the scenario catalogue, run:
```bash
python evaluation/evaluate_scenarios.py
```
