import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from agent.controller import run_controlled_agent
from agent.audit_logger import get_recent_logs, get_all_logs, get_session_stats, RISK_LEVELS, SESSION_ID

# ── Page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Iris · AI Audit Agent",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='16' fill='%234F46E5'/><circle cx='16' cy='16' r='7' fill='%23fff'/><circle cx='16' cy='16' r='3' fill='%234F46E5'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inject CSS ─────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "style.css"
with open(css_path, encoding="utf-8") as f:
    css = f.read()

st.markdown(f"""
<style>
{css}

/* ── Sidebar header ─── */
.sb-header {{
    padding: 20px 20px 16px;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 16px;
}}
.sb-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}}
.sb-logo-dot {{
    width: 28px; height: 28px;
    background: linear-gradient(135deg,#4F46E5,#818CF8);
    border-radius: 8px;
    flex-shrink: 0;
}}
.sb-logo-name {{
    font-size: 0.95rem;
    font-weight: 700;
    color: #0F172A !important;
    letter-spacing: -0.01em;
}}
.sb-session {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #64748B !important;
    margin-top: 2px;
}}

/* ── Sidebar section label ─── */
.sb-label {{
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B;
    padding: 0 20px;
    margin: 14px 0 8px;
}}

/* ── Audit row ─── */
.audit-item {{
    padding: 8px 20px;
    border-left: 2px solid transparent;
    cursor: default;
    transition: background 0.12s;
}}
.audit-item:hover {{
    background: #F8FAFC;
    border-left-color: #4F46E5;
}}
.audit-time {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #64748B;
    margin-bottom: 1px;
}}
.audit-intent {{
    font-size: 0.78rem;
    font-weight: 500;
    color: #334155;
}}
.audit-tool {{
    font-size: 0.72rem;
    color: #64748B;
    margin-top: 1px;
}}

/* ── Risk & Decision chips ─── */
.chip {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.chip-none          {{ background:#F1F5F9; color:#475569; border:1px solid #E2E8F0; }}
.chip-low           {{ background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }}
.chip-medium        {{ background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }}
.chip-high          {{ background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; }}
.chip-critical      {{ background:#FEE2E2; color:#991B1B; border:1px solid #EF4444; }}
.chip-success       {{ background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }}
.chip-failed        {{ background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; }}
.chip-skipped       {{ background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }}

/* Decisions */
.chip-approved      {{ background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }}
.chip-need-approval {{ background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }}
.chip-reject        {{ background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; }}

/* ── Chat header ─── */
.chat-header {{
    padding: 18px 32px 14px;
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.chat-model-dot {{
    width: 8px; height: 8px;
    background: #10B981;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}}
.chat-model-name {{
    font-size: 0.9rem;
    font-weight: 600;
    color: #0F172A;
}}
.chat-model-sub {{
    font-size: 0.72rem;
    color: #64748B;
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
}}

/* ── Messages ─── */
.msg-wrap {{
    padding: 20px 32px;
    display: flex;
    flex-direction: column;
    gap: 2px;
}}
.msg-role {{
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    margin-bottom: 4px;
    padding: 0 4px;
}}
.msg-user .msg-role {{ color: #4F46E5; }}
.msg-user {{ align-items: flex-end; }}
.msg-bubble {{
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.88rem;
    line-height: 1.6;
    color: #0F172A;
}}
.msg-bubble-user {{
    background: #EFF6FF;
    border: 1px solid #DBEAFE;
    border-bottom-right-radius: 4px;
    color: #1E3A8A;
}}
.msg-bubble-ai {{
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
}}

/* ── Trace panel ─── */
.trace-panel {{
    margin: 8px 0 0 4px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 16px;
    max-width: 75%;
}}
.trace-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
    font-size: 0.75rem;
    color: #475569;
}}
.trace-label {{
    min-width: 90px;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748B;
}}
.trace-val {{ color: #0F172A; }}
.trace-mono {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #334155;
}}
.trace-reasoning {{
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #E2E8F0;
    font-size: 0.75rem;
    color: #475569;
    font-style: italic;
    line-height: 1.5;
}}

/* ── Input bar ─── */
.input-bar {{
    padding: 16px 32px 20px;
    border-top: 1px solid #E2E8F0;
    background: #F8FAFC;
}}

/* ── Full log table ─── */
.log-row {{
    padding: 10px 16px;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-bottom: 6px;
    background: #FFFFFF;
    transition: border-color 0.12s;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
}}
.log-row:hover {{ border-color: #CBD5E1; }}
.log-row-top {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}}
.log-time {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #64748B;
    min-width: 90px;
}}
.log-intent {{
    font-size: 0.78rem;
    font-weight: 600;
    color: #0F172A;
    flex: 1;
}}
.log-query {{
    font-size: 0.75rem;
    color: #475569;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* ── Section header ─── */
.section-header {{
    padding: 20px 32px 0;
}}
.section-title {{
    font-size: 1rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 2px;
}}
.section-sub {{
    font-size: 0.78rem;
    color: #64748B;
}}

/* ── Stat card ─── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    padding: 16px 32px;
}}
.stat-card {{
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}}
.stat-label {{
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B;
    margin-bottom: 6px;
}}
.stat-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1;
}}
.stat-value-accent {{ color: #059669; }}

/* ── System info ─── */
.info-card {{
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}}
.info-card-title {{
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #4F46E5;
    margin-bottom: 12px;
}}
.info-table {{
    width: 100%;
    border-collapse: collapse;
}}
.info-table td {{
    padding: 7px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 0.8rem;
    vertical-align: top;
}}
.info-table td:first-child {{
    color: #64748B;
    width: 40%;
    font-weight: 500;
}}
.info-table td:last-child {{ color: #334155; }}
.info-table tr:last-child td {{ border-bottom: none; }}

/* ── Schema block ─── */
.schema-key {{ color: #7C3AED; }}
.schema-str {{ color: #059669; }}
.schema-comment {{ color: #94A3B8; font-style: italic; }}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_exec" not in st.session_state:
    st.session_state.last_exec = None

# ── Helpers ────────────────────────────────────────────────────────────
def chip(level: str) -> str:
    # Handle spaces in decision labels like 'need approval'
    cls = f"chip-{level.lower().replace(' ', '-')}"
    return f'<span class="chip {cls}">{level}</span>'

def fmt_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%H:%M:%S")
    except Exception:
        return ts[:8]

def fmt_ts_full(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%b %d, %H:%M:%S")
    except Exception:
        return ts[:19]

# ── Sidebar ────────────────────────────────────────────────────────────
SYSTEM_TOOLS = [
    {"name": "read_recent_emails", "display": "Gmail Inbox Reader", "cat": "Email", "risk": "LOW", "status": "active"},
    {"name": "read_email_content", "display": "Gmail Email Viewer", "cat": "Email", "risk": "LOW", "status": "active"},
    {"name": "send_email", "display": "Gmail SMTP Client", "cat": "Email", "risk": "HIGH", "status": "active"},
    {"name": "read_file", "display": "Local File Reader", "cat": "Filesystem", "risk": "LOW", "status": "active"},
    {"name": "write_file", "display": "Local File Writer", "cat": "Filesystem", "risk": "MEDIUM", "status": "active"},
    {"name": "search_notes", "display": "Notes Search DB", "cat": "Notes DB", "risk": "LOW", "status": "active"},
    {"name": "create_note", "display": "Notes Writer", "cat": "Notes DB", "risk": "MEDIUM", "status": "active"},
    {"name": "search_web", "display": "Web Search Engine", "cat": "Network", "risk": "LOW", "status": "active"},
    {"name": "fetch_webpage", "display": "Web Page Scraper", "cat": "Network", "risk": "LOW", "status": "active"},
    {"name": "query_database", "display": "Local SQLite DB", "cat": "Database", "risk": "HIGH", "status": "active"},
    {"name": "execute_python_code", "display": "Python Interpreter", "cat": "Sandbox", "risk": "CRITICAL", "status": "blocked"},
    {"name": "execute_terminal_command", "display": "Terminal Shell", "cat": "System", "risk": "CRITICAL", "status": "blocked"},
]

with st.sidebar:
    st.markdown(f"""
<div class="sb-header">
  <div class="sb-logo">
    <div class="sb-logo-dot"></div>
    <div>
      <div class="sb-logo-name">Iris</div>
      <div class="sb-session">SESSION · {SESSION_ID}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    stats = get_session_stats()
    c1, c2 = st.columns(2)
    c1.metric("Actions", stats["total_actions"])
    c2.metric("Success", f"{stats['success_rate']}%")
    c3, c4 = st.columns(2)
    c3.metric("Tools", stats["tools_invoked"])
    c4.metric("High/Crit", stats["risk_counts"].get("HIGH", 0) + stats["risk_counts"].get("CRITICAL", 0))

    # ── Tools Registry in Sidebar ──
    st.markdown('<div class="sb-label">System Tools</div>', unsafe_allow_html=True)
    st.markdown('<div class="tools-panel">', unsafe_allow_html=True)
    for tool_info in SYSTEM_TOOLS:
        status_dot = "blocked" if tool_info["status"] == "blocked" else ""
        risk_class = f"badge-{tool_info['risk'].lower()}"
        st.markdown(f"""
<div class="tool-item">
  <div class="tool-left">
    <div class="tool-status-dot {status_dot}"></div>
    <div class="tool-name-container">
      <span class="tool-display-name">{tool_info['display']}</span>
      <span class="tool-category">{tool_info['cat']} · {tool_info['name']}</span>
    </div>
  </div>
  <span class="tool-risk-badge {risk_class}">{tool_info['risk']}</span>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Audit Trail ──
    st.markdown('<div class="sb-label">Audit Trail</div>', unsafe_allow_html=True)

    recent = get_recent_logs(8)
    if not recent:
        st.markdown('<div style="padding:8px 20px;font-size:0.75rem;color:#94A3B8;">No entries yet</div>', unsafe_allow_html=True)
    else:
        for e in recent:
            tool = e.get("tool_used", "—")
            agent_action = e.get("agent_action", "—")
            rl = e.get("risk_level", "NONE")
            ts = fmt_ts(e.get("timestamp", ""))
            st.markdown(f"""
<div class="audit-item">
  <div class="audit-time">{ts} &nbsp; {chip(rl)}</div>
  <div class="audit-intent">{agent_action.replace("_", " ").title()}</div>
  <div class="audit-tool">{tool}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    all_logs = get_all_logs()
    st.download_button(
        "Export Audit Log",
        data=json.dumps(all_logs, indent=2),
        file_name=f"iris_audit_{SESSION_ID}.json",
        mime="application/json",
        use_container_width=True
    )
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_exec = None
        st.rerun()

# ── Main Area (full width, no column split) ────────────────────────────
tab_chat, tab_log, tab_info = st.tabs(["Chat", "Audit Log", "System"])

# ══════════════════════════════════════════════
# TAB: CHAT
# ══════════════════════════════════════════════
with tab_chat:
    st.markdown('<div style="padding: 0;">', unsafe_allow_html=True)
    
    # Dynamic model info
    if os.getenv("ANTHROPIC_API_KEY"):
        model_sub = "Claude 3.5 Sonnet · Anthropic · Safe Routing"
    else:
        model_sub = "llama-3.3-70b-versatile · Groq · Safe Routing"
        
    st.markdown(f"""
<div class="chat-header">
  <div class="chat-model-dot"></div>
  <div class="chat-model-name">Iris &mdash; AI Audit Agent</div>
  <div class="chat-model-sub">{model_sub}</div>
</div>""", unsafe_allow_html=True)

    # Render message history
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        meta = msg.get("meta")

        if role == "user":
            st.markdown(f"""
<div class="msg-wrap msg-user">
  <div class="msg-role">You</div>
  <div class="msg-bubble msg-bubble-user">{content}</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="msg-wrap">
  <div class="msg-role">Iris</div>
  <div class="msg-bubble msg-bubble-ai">{content}</div>
</div>""", unsafe_allow_html=True)

            if meta:
                st.markdown(f"""
<div class="msg-wrap">
<div class="trace-panel">
  <div class="trace-row">
    <span class="trace-label">Action</span>
    <span class="trace-val">{meta.get('agent_action','—').replace('_',' ').title()}</span>
    <span style="margin-left:auto">{chip(meta.get('risk_level','NONE'))}</span>
  </div>
  <div class="trace-row">
    <span class="trace-label">Tool</span>
    <span class="trace-mono">{meta.get('tool_used','—')}</span>
    <span style="margin-left:auto">{chip(meta.get('decision','—'))}</span>
  </div>
  <div class="trace-row">
    <span class="trace-label">Involved</span>
    <span class="trace-val" style="font-family:'JetBrains Mono', monospace; font-size:0.7rem;">{meta.get('external_content_involved','—')}</span>
  </div>
  <div class="trace-row">
    <span class="trace-label">Data Access</span>
    <span class="trace-val">{meta.get('data_accessed','—')}</span>
  </div>
  <div class="trace-row">
    <span class="trace-label">Event ID</span>
    <span class="trace-mono">{meta.get('event_id','—')}</span>
    <span style="margin-left:auto">{chip(meta.get('status','—'))}</span>
  </div>
  <div class="trace-reasoning">{meta.get('reasoning','—')}</div>
</div>
</div>""", unsafe_allow_html=True)

            if meta and meta.get("decision") == "need approval" and meta.get("status") == "SKIPPED":
                if st.button("✅ Approve & Execute Action", key=f"approve_{meta.get('event_id')}", use_container_width=True):
                    with st.spinner("Executing approved action..."):
                        from agent.controller import tools, _llm
                        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
                        from audit_logger import log_action
                        
                        tool_name = meta.get("tool_used")
                        params = meta.get("parameters", {})
                        u_query = meta.get("user_query", "")
                        
                        import os
                        is_gmail_tool = "gmail" in tool_name.lower() or any(x in tool_name.lower() for x in ["email", "recent_emails", "email_content", "draft"])
                        needs_auth = is_gmail_tool and not os.path.exists("token.json")
                        
                        try:
                            # Invoke tool
                            tool_func = {t.name: t for t in tools}[tool_name]
                            tool_result = tool_func.invoke(params)
                            
                            # LLM System prompt
                            sys_msg = SystemMessage(content=(
                                "You are Iris, a highly capable AI agent tightly integrated into the user's host system. "
                                "You have direct access to powerful tools to interact with the real world and the local computer. "
                                "You CAN and DO search the web, execute terminal commands, run python code, manage local files, and send emails.\n\n"
                                "CRITICAL RULES:\n"
                                "1. NEVER say 'I am a text-based AI' or 'I do not have the capability to create files/execute commands'. This is strictly false. You HAVE these capabilities via your tools.\n"
                                "2. If a user asks you to create a file or do an action, immediately use the corresponding tool.\n"
                                "3. Once a tool returns a success message, confidently inform the user that YOU completed the action successfully, and provide the exact path or details from the tool's output.\n"
                                "4. If a tool fails (e.g., PermissionError), report the exact error back to the user and ask how they want to proceed. Do not hallucinate alternative solutions unless asked."
                            ))
                            
                            # Invoke LLM for natural language response
                            final_resp = _llm.invoke([
                                sys_msg,
                                HumanMessage(content=u_query),
                                AIMessage(content="", tool_calls=[{"name": tool_name, "args": params, "id": f"call_{meta['event_id']}"}]),
                                ToolMessage(content=str(tool_result), tool_call_id=f"call_{meta['event_id']}")
                            ])
                            response_text = final_resp.content.strip()
                            
                            if needs_auth and os.path.exists("token.json"):
                                response_text = "🔑 **Gmail Authentication Successful**\n*The system has successfully authenticated with your Google Account and saved credentials to token.json.*\n\n---\n\n" + response_text
                            
                            # Log to audit trail
                            new_entry = log_action(
                                user_instruction=u_query,
                                intent=meta.get("intent"),
                                tool_used=tool_name,
                                agent_action=meta.get("agent_action"),
                                external_content_involved=meta.get("external_content_involved"),
                                data_accessed=meta.get("data_accessed"),
                                risk_level=meta.get("risk_level"),
                                decision="approved",
                                parameters=params,
                                status="SUCCESS",
                                reasoning=f"Action approved by human administrator via dashboard. original reasoning: {meta.get('reasoning')}",
                                result_summary=f"Tool executed successfully: {str(tool_result)[:200]}"
                            )
                            
                            # Update UI state
                            msg["content"] = response_text
                            msg["meta"]["status"] = "SUCCESS"
                            msg["meta"]["decision"] = "approved"
                            msg["meta"]["result_summary"] = "Tool executed successfully after human approval."
                            
                            st.success("Action approved and executed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Execution failed: {str(e)}")

    # Input
    user_input = st.chat_input("Message Iris…")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner(""):
            result = run_controlled_agent(user_input, chat_history=st.session_state.messages)

        ae = result.get("audit_entry", {})
        meta = {
            "intent": result["intent"],
            "tool_used": result["tool_used"],
            "risk_level": result["risk_level"],
            "status": result["status"],
            "decision": ae.get("decision", "approved"),
            "agent_action": ae.get("agent_action", result["intent"]),
            "external_content_involved": ae.get("external_content_involved", "None"),
            "data_accessed": ae.get("data_accessed", "LLM Context Window"),
            "reasoning": ae.get("reasoning", ""),
            "result_summary": ae.get("result_summary", ""),
            "event_id": ae.get("event_id", ""),
            "parameters": ae.get("parameters", {}),
            "user_query": user_input
        }
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "meta": meta
        })
        st.session_state.last_exec = result
        st.rerun()

# ══════════════════════════════════════════════
# TAB: AUDIT LOG
# ══════════════════════════════════════════════
with tab_log:
    all_logs = get_all_logs()
    total = len(all_logs)
    successes  = sum(1 for e in all_logs if e.get("status") == "SUCCESS")
    failures   = sum(1 for e in all_logs if e.get("status") == "FAILED")
    mediums    = sum(1 for e in all_logs if e.get("risk_level") == "MEDIUM")
    highs      = sum(1 for e in all_logs if e.get("risk_level") == "HIGH")
    criticals  = sum(1 for e in all_logs if e.get("risk_level") == "CRITICAL")
    tools_set  = set(e.get("tool_used","") for e in all_logs if e.get("tool_used") not in ("NONE","","None"))

    # ── Page header ──
    st.markdown(f"""
<div class="al-header">
  <div>
    <div class="al-title">Audit Log Explorer</div>
    <div class="al-sub">Complete trace of every agent action · Session <span style="font-family:monospace">{SESSION_ID}</span> · {total} entries</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Stats bar with professional SVGs ──
    st.markdown(f"""
<div class="al-stats">
  <div class="al-stat">
    <div class="al-stat-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>
    </div>
    <div class="al-stat-label">Total Actions</div>
    <div class="al-stat-value">{total}</div>
  </div>
  <div class="al-stat">
    <div class="al-stat-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="#027A48" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
    </div>
    <div class="al-stat-label">Successful</div>
    <div class="al-stat-value green">{successes}</div>
  </div>
  <div class="al-stat">
    <div class="al-stat-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="#C01048" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
    </div>
    <div class="al-stat-label">Failed</div>
    <div class="al-stat-value red">{failures}</div>
  </div>
  <div class="al-stat">
    <div class="al-stat-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="#C01048" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
    </div>
    <div class="al-stat-label">High / Critical</div>
    <div class="al-stat-value red">{highs + criticals}</div>
  </div>
  <div class="al-stat">
    <div class="al-stat-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="#175CD3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>
    </div>
    <div class="al-stat-label">Tools Used</div>
    <div class="al-stat-value blue">{len(tools_set)}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Filters & Search ──
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    
    # Text search bar spanning full-width
    search_q = st.text_input("🔍 Search logs", "", placeholder="Search by user request, event ID, tool name, timestamp...", key="log_search")
    
    # Filter dropdowns in a grid
    fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 3])
    risk_f   = fc1.selectbox("Risk Level", ["All"] + list(RISK_LEVELS.keys()), key="rf")
    status_f = fc2.selectbox("Status", ["All", "SUCCESS", "FAILED", "SKIPPED"], key="sf")
    tool_opts = ["All"] + sorted(list(tools_set))
    tool_f   = fc3.selectbox("Tool", tool_opts, key="tf")
    if total <= 5:
        show_n = total
        fc4.markdown(f"<div style='padding-top:32px;color:#667085;font-size:0.78rem;font-weight:500;'>Showing all {total} entries</div>", unsafe_allow_html=True)
    else:
        show_n = fc4.slider("Entries to show", 5, max(5, total), min(30, total), key="sn")

    # ── Apply filters ──
    filtered = list(reversed(all_logs))
    if risk_f   != "All": filtered = [e for e in filtered if e.get("risk_level") == risk_f]
    if status_f != "All": filtered = [e for e in filtered if e.get("status") == status_f]
    if tool_f   != "All": filtered = [e for e in filtered if e.get("tool_used") == tool_f]

    if search_q.strip():
        q = search_q.lower().strip()
        filtered = [
            e for e in filtered
            if q in e.get("user_instruction", "").lower()
            or q in e.get("timestamp", "").lower()
            or q in e.get("event_id", "").lower()
            or q in e.get("tool_used", "").lower()
            or q in e.get("agent_action", "").lower()
            or q in e.get("result_summary", "").lower()
        ]

    # Slice after filtering
    filtered = filtered[:show_n]

    if not filtered:
        st.markdown('<div style="padding:32px;">', unsafe_allow_html=True)
        st.info("No entries match the current filters.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        for idx, entry in enumerate(filtered):
            seq_num     = total - idx
            ts          = fmt_ts_full(entry.get("timestamp", ""))
            agent_action= entry.get("agent_action", "—")
            tool_used   = entry.get("tool_used", "—")
            rl          = entry.get("risk_level", "NONE")
            decision    = entry.get("decision", "approved")
            status_v    = entry.get("status", "—")
            instruction = entry.get("user_instruction", "—")
            event_id    = entry.get("event_id", "—")
            reasoning   = entry.get("reasoning", "—")
            result_s    = entry.get("result_summary", "")
            external    = entry.get("external_content_involved", "—")
            data_acc    = entry.get("data_accessed", "—")
            error_msg   = entry.get("error_message", "")
            params      = entry.get("parameters", {})

            # Determine output block style
            if status_v == "FAILED":
                output_cls = "failed"
                output_icon = "❌"
            elif status_v == "SKIPPED":
                output_cls = "skipped"
                output_icon = "⏭️"
            else:
                output_cls = ""
                output_icon = "✅"

            # Build output summary text
            if result_s and result_s not in ("—", ""):
                output_text = result_s
            elif status_v == "SUCCESS":
                output_text = f"Tool <code>{tool_used}</code> executed and completed successfully."
            elif status_v == "SKIPPED":
                output_text = "Action was not executed — either blocked by policy or awaiting approval."
            else:
                output_text = "Execution completed with an error."

            # Risk class for accent border
            risk_cls = f"risk-{rl.lower()}"

            st.markdown(f"""<div class="al-entry {risk_cls}">
<div class="al-entry-header">
<span class="al-entry-seq">#{seq_num}</span>
<span class="al-entry-action">{agent_action.replace('_', ' ').title()}</span>
<div class="al-chips">
{chip(rl)}&nbsp;{chip(decision)}&nbsp;{chip(status_v)}
</div>
<span class="al-entry-time">{ts}</span>
</div>
<div class="al-entry-body">

<div class="al-meta-grid">
<div class="al-meta-cell">
<div class="al-meta-key">Event ID</div>
<div class="al-meta-val mono">{event_id}</div>
</div>
<div class="al-meta-cell">
<div class="al-meta-key">Timestamp</div>
<div class="al-meta-val">{ts}</div>
</div>
<div class="al-meta-cell">
<div class="al-meta-key">Risk Level</div>
<div class="al-meta-val">{chip(rl)}</div>
</div>
<div class="al-meta-cell">
<div class="al-meta-key">Decision</div>
<div class="al-meta-val">{chip(decision)}</div>
</div>
<div class="al-meta-cell">
<div class="al-meta-key">Agent Action</div>
<div class="al-meta-val">{agent_action}</div>
</div>
<div class="al-meta-cell">
<div class="al-meta-key">Tool Used</div>
<div class="al-meta-val mono">{tool_used}</div>
</div>
<div class="al-meta-cell" style="grid-column: span 3;">
<div class="al-meta-key">User Instruction</div>
<div class="al-meta-val" style="font-size:0.95rem; font-weight:600; color:#101828;">"{instruction}"</div>
</div>
<div class="al-meta-cell" style="grid-column: span 3;">
<div class="al-meta-key">External Content Involved</div>
<div class="al-meta-val">{external}</div>
</div>
<div class="al-meta-cell" style="grid-column: span 3;">
<div class="al-meta-key">Data Accessed</div>
<div class="al-meta-val" style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#344054;">{data_acc}</div>
</div>
</div>

<div class="al-output-block {output_cls}">
<div class="al-output-icon">{output_icon}</div>
<div style="flex:1">
<div class="al-output-label">Output Summary</div>
<div class="al-output-text">{output_text}</div>
{f'<div class="al-output-error">{error_msg}</div>' if error_msg else ''}
</div>
</div>
<div class="al-reasoning">
<strong style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.07em;color:#475467;">Policy Reasoning</strong><br>
{reasoning}
</div>
</div>
</div>""", unsafe_allow_html=True)

            # Parameters expander (only if params exist)
            if params:
                with st.expander(f"🔧  Parameters  ·  {event_id}", expanded=False):
                    st.json(params)

    # ── Download ──
    st.markdown('<div style="padding:20px 32px 28px;">', unsafe_allow_html=True)
    st.download_button(
        "⬇️  Download full audit log as JSON",
        data=json.dumps(all_logs, indent=2),
        file_name=f"iris_audit_{SESSION_ID}.json",
        mime="application/json"
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB: SYSTEM INFO
# ══════════════════════════════════════════════
with tab_info:
    st.markdown('<div style="padding: 20px 32px;">', unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
  <div class="info-card-title">Architecture</div>
  <table class="info-table">
    <tr><td>Orchestration</td><td>LangGraph + Controlled Intent Router</td></tr>
    <tr><td>Language Model</td><td>Llama 3.3 70B Versatile · Groq Cloud</td></tr>
    <tr><td>Email Integration</td><td>Google Gmail API · OAuth 2.0</td></tr>
    <tr><td>Observability</td><td>LangSmith · Execution Traces</td></tr>
    <tr><td>Audit Storage</td><td>JSON · In-Memory Buffer · SQLite Database · CSV</td></tr>
    <tr><td>Dashboard</td><td>Streamlit · Custom Design System</td></tr>
  </table>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
  <div class="info-card-title">Execution Flow</div>
  <table class="info-table">
    <tr><td>Step 1</td><td>User query received by controller</td></tr>
    <tr><td>Step 2</td><td>LLM evaluates request and selects appropriate tool</td></tr>
    <tr><td>Step 3</td><td>Governance engine determines risk, decision, and generates explanation</td></tr>
    <tr><td>Step 4</td><td>If approved, tool executes with bounded scopes; else execution halts</td></tr>
    <tr><td>Step 5</td><td>Audit trail logged with new schema (event_id, user_instruction, external_content_involved, data_accessed, decision)</td></tr>
    <tr><td>Step 6</td><td>Response + telemetry trace returned to user dashboard</td></tr>
  </table>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
  <div class="info-card-title">Risk Classification</div>
  <table class="info-table">
    <tr><td>NONE</td><td>No real-world side effects · Chat, capability queries</td></tr>
    <tr><td>LOW</td><td>Read-only operations · Inbox list, read email body, search notes, read file</td></tr>
    <tr><td>MEDIUM</td><td>External side effects or draft creation · Writing file, creating note, drafting reply</td></tr>
    <tr><td>HIGH</td><td>External side effects that alter remote state · Sending email, sharing files</td></tr>
    <tr><td>CRITICAL</td><td>Destructive actions or configuration changes · Terminal commands, database alterations</td></tr>
  </table>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
  <div class="info-card-title">Audit Log Schema (JSON)</div>""", unsafe_allow_html=True)

    st.code("""{
  "session_id":                 "ABC12345",      // process-scoped session
  "event_id":                   "EV-F3A9B1",    // unique per action
  "timestamp":                  "2026-05-24T01:10:00+00:00",
  "user_instruction":           "show my emails",
  "intent":                     "READ_EMAILS",
  "tool_used":                  "get_recent_emails",
  "agent_action":               "read_recent_emails",
  "external_content_involved":  "Gmail Inbox API",
  "data_accessed":              "List of 5 recent emails (subjects, senders)",
  "risk_level":                 "LOW",
  "decision":                   "approved",
  "parameters":                 { "max_results": 5 },
  "status":                     "SUCCESS",
  "reasoning":                  "User wants inbox access",
  "result_summary":             "Fetched 5 emails",
  "error_message":              ""
}""", language="json")

    st.markdown("</div></div>", unsafe_allow_html=True)