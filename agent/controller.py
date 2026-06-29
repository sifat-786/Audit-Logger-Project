import os
import re
import uuid
import threading
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

from tools.gmail_tool import (
    read_recent_emails as _gmail_read_recent,
    read_email_content as _gmail_read_specific,
    send_email as _gmail_send,
    create_draft as _gmail_create_draft,
    modify_email_labels as _gmail_modify_labels
)
from tools.generic_tools import (
    read_file as _read_file,
    write_file as _write_file,
    create_note as _create_note,
    search_notes as _search_notes,
    list_notes as _list_notes,
    search_web as _search_web,
    execute_terminal_command as _execute_terminal_command,
    fetch_webpage as _fetch_webpage,
    execute_python_code as _execute_python_code,
    calculate_math as _calculate_math,
    query_database as _query_database
)

from agent.audit_logger import log_action
from agent.risk_classifier import evaluate_action
from agent.decision_engine import evaluate_decision
from agent.explanation_engine import generate_explanation
from agent.query_validator import validate_query
from tools.scheduler_tool import schedule_action as _schedule_action

thread_local_ctx = threading.local()

load_dotenv()

# =====================================================
# LLM INSTANCE
# =====================================================

_llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

# =====================================================
# LANGCHAIN TOOLS REGISTRY
# =====================================================

@tool
def read_recent_emails(max_results: int = 5) -> str:
    """Fetches a list of recent emails from the user's inbox."""
    return str(_gmail_read_recent(max_results))

@tool
def read_email_content(email_index: int = 1) -> str:
    """Reads the full body content of a specific email by its index (1 for the newest)."""
    return str(_gmail_read_specific(email_index))

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Sends an email to a specific recipient."""
    return str(_gmail_send(to, subject, body))

@tool
def create_draft_email(to: str, subject: str, body: str) -> str:
    """Creates a draft email in the user's Gmail mailbox."""
    return str(_gmail_create_draft(to, subject, body))

@tool
def modify_email_labels(email_index: int = 1, add_labels: list = None, remove_labels: list = None) -> str:
    """Modifies Gmail labels for a specific email index. Can be used to star/flag, archive, or categorize emails."""
    return str(_gmail_modify_labels(email_index, add_labels, remove_labels))

@tool
def read_file(filepath: str) -> str:
    """Reads the content of a local file."""
    return _read_file(filepath)

@tool
def write_file(filepath: str, content: str) -> str:
    """Writes content to a local file."""
    return _write_file(filepath, content)

@tool
def search_notes(query: str) -> str:
    """Searches existing notes for a given keyword query."""
    return str(_search_notes(query))

@tool
def create_note(content: str) -> str:
    """Creates a new note."""
    return _create_note(content)

@tool
def list_notes() -> list:
    """Lists all currently saved notes."""
    return _list_notes()

@tool
def search_web(query: str) -> str:
    """Searches the internet for up-to-date information."""
    return str(_search_web(query))

@tool
def execute_terminal_command(command: str) -> str:
    """Executes a terminal/bash/powershell command directly on the host computer."""
    return str(_execute_terminal_command(command))

@tool
def fetch_webpage(url: str) -> str:
    """Fetches the raw HTML or text content of a webpage."""
    return str(_fetch_webpage(url))

@tool
def execute_python_code(code: str) -> str:
    """Executes Python code in a safe local environment and returns the stdout output."""
    return str(_execute_python_code(code))

@tool
def calculate_math(expression: str) -> str:
    """Safely evaluates a mathematical expression."""
    return str(_calculate_math(expression))

@tool
def query_database(sql_query: str) -> str:
    """Executes an SQL query against the local SQLite database."""
    return str(_query_database(sql_query))

@tool
def schedule_task(target_time: str, action_type: str, action_args: dict) -> str:
    """
    Schedules an action (like send_email or write_file) to run at a specific future target time.
    target_time: E.g., '2:09 AM' or '2026-06-16 02:09:00'
    action_type: The name of the action (e.g. 'send_email')
    action_args: The parameters to pass (e.g. {'to': '...', 'subject': '...', 'body': '...'}).
                 IMPORTANT: Do not include the scheduling time or relative delay string (e.g., 'at 2:09 AM', 'in 2 seconds')
                 inside the email's subject or body unless explicitly requested by the user.
    """
    parent_ev = getattr(thread_local_ctx, "event_id", "SYSTEM")
    return _schedule_action(target_time, action_type, action_args, parent_event_id=parent_ev)

# The tools list provided to the LLM
tools = [
    read_recent_emails,
    read_email_content,
    send_email,
    create_draft_email,
    modify_email_labels,
    read_file,
    write_file,
    search_notes,
    create_note,
    list_notes,
    search_web,
    execute_terminal_command,
    fetch_webpage,
    execute_python_code,
    calculate_math,
    query_database,
    schedule_task
]

_llm_with_tools = _llm.bind_tools(tools)

# =====================================================
# MAIN CONTROLLER FUNCTION
# =====================================================

def run_controlled_agent(user_query: str, chat_history: list = None) -> dict:
    """
    Execute one turn of the tool-agnostic controlled agent pipeline.
    
    Workflow:
    1. Intent Detection (LLM tool selection)
    2. Governance Pipeline (Auth/Risk/Approval/Reject)
    3. Tool Execution
    4. Audit Logging
    5. Natural Response Generation
    """
    thread_local_ctx.event_id = f"EV-{str(uuid.uuid4())[:6].upper()}"
    suggestions = validate_query(user_query)
    
    sys_msg = SystemMessage(content=(
        "You are Iris, a highly capable AI agent tightly integrated into the user's host system. "
        "You have direct access to powerful tools to interact with the real world and the local computer. "
        "You CAN and DO search the web, execute terminal commands, run python code, manage local files, and send emails.\n\n"
        "CRITICAL RULES:\n"
        "1. NEVER say 'I am a text-based AI' or 'I do not have the capability to create files/execute commands'. This is strictly false. You HAVE these capabilities via your tools.\n"
        "2. If a user asks you to create a file or do an action, immediately use the corresponding tool.\n"
        "3. Once a tool returns a success message, confidently inform the user that YOU completed the action successfully, and provide the exact path or details from the tool's output.\n"
        "4. If a tool fails (e.g., PermissionError), report the exact error back to the user and ask how they want to proceed. Do not hallucinate alternative solutions unless asked.\n"
        "5. When scheduling a task (e.g., sending an email at a specific time), the target time is ONLY for the 'target_time' parameter of the schedule_task tool. DO NOT include scheduling times, delays, or relative time descriptions (like 'at 2:09 AM' or 'in 2 seconds') inside the actual content of the task (such as the email subject or body) unless the user explicitly asked you to put that text in the message."
    ))

    messages = [sys_msg]
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                meta = msg.get("meta", {})
                tool_used = meta.get("tool_used") if meta else None
                if tool_used and tool_used != "NONE":
                    params = meta.get("parameters", {})
                    ev_id = meta.get("event_id", "dummy")
                    res_sum = meta.get("result_summary", "") or meta.get("error_message", "Tool executed.")
                    messages.append(AIMessage(
                        content="",
                        tool_calls=[{"name": tool_used, "args": params, "id": f"call_{ev_id}"}]
                    ))
                    messages.append(ToolMessage(
                        content=str(res_sum),
                        tool_call_id=f"call_{ev_id}"
                    ))
                messages.append(AIMessage(content=msg["content"]))
    else:
        messages.append(HumanMessage(content=user_query))

    # Step 1: LLM decides whether to use a tool or answer purely via LLM
    ai_msg = _llm_with_tools.invoke(messages)
    
    # --------------------------------------------------
    # A. PURE LLM TASK (No tools required)
    # --------------------------------------------------
    if not ai_msg.tool_calls:
        intent = "NORMAL_CHAT"
        tool_used = "NONE"
        risk_level = "NONE"
        status = "SUCCESS"
        reasoning = "Pure LLM Task. No external access required."
        response = ai_msg.content.strip()
        result_summary = "Conversational response generated natively."
        
        if suggestions:
            suggestion_prefix = "⚠️ **Did you mean?**\n" + "\n".join([f"- {s}" for s in suggestions]) + "\n\n---\n\n"
            response = suggestion_prefix + response
        
        audit_entry = log_action(
            user_instruction=user_query,
            intent=intent,
            tool_used=tool_used,
            agent_action=intent,
            external_content_involved="None",
            data_accessed="LLM Context Window",
            risk_level=risk_level,
            decision="approved",
            parameters={},
            status=status,
            reasoning=reasoning,
            result_summary=result_summary,
            event_id=thread_local_ctx.event_id
        )
        thread_local_ctx.event_id = None
        return {"intent": intent, "response": response, "tool_used": tool_used, "risk_level": risk_level, "status": status, "audit_entry": audit_entry, "data": None}

    # --------------------------------------------------
    # B. TOOL-BASED AGENT TASK
    # --------------------------------------------------
    tool_call = ai_msg.tool_calls[0]
    tool_name = tool_call["name"]
    parameters = tool_call["args"]
    intent = tool_name.upper()
    tool_used = tool_name
    data = None
    error_message = ""
    
    # Step 2: Governance Pipeline (Risk Classification, Decision Engine, Explanation Generation)
    decision_data = generate_explanation(tool_name)
    risk_level = decision_data["risk_level"]
    decision = decision_data["decision"]
    policy_reasoning = decision_data["explanation"]
    
    reasoning = f"Tool selected: {tool_name}. Policy check: {policy_reasoning}"
    
    # Dynamic extraction of telemetry fields
    external_content_involved = "None"
    data_accessed = "None"
    
    if tool_name == "read_recent_emails":
        external_content_involved = "Gmail Inbox API"
        data_accessed = f"List of {parameters.get('max_results', 5)} recent emails (subjects, senders)"
    elif tool_name == "read_email_content":
        idx = parameters.get('email_index', 1)
        external_content_involved = f"Gmail API Email Index: {idx}"
        data_accessed = "Full text body and headers of specific email"
    elif tool_name == "send_email":
        to_addr = parameters.get('to', 'unknown')
        external_content_involved = f"Gmail SMTP Client (Recipient: {to_addr})"
        subj = parameters.get('subject', 'No Subject')
        data_accessed = f"Outbound email content (Subject: '{subj}')"
    elif tool_name == "read_file":
        filepath = parameters.get('filepath', 'unknown')
        external_content_involved = f"Local File System ({filepath})"
        data_accessed = "Read-only access to file content"
    elif tool_name == "write_file":
        filepath = parameters.get('filepath', 'unknown')
        external_content_involved = f"Local File System ({filepath})"
        data_accessed = f"Write/overwrite content ({len(parameters.get('content', ''))} characters)"
    elif tool_name == "search_notes":
        q = parameters.get('query', '')
        external_content_involved = "In-memory Notes DB"
        data_accessed = f"Notes query matches for '{q}'"
    elif tool_name == "create_note":
        external_content_involved = "In-memory Notes DB"
        data_accessed = "Appended new note content"
    elif tool_name == "list_notes":
        external_content_involved = "In-memory Notes DB"
        data_accessed = "List of all saved notes"
    elif tool_name == "search_web":
        q = parameters.get('query', '')
        external_content_involved = f"Web Search API (Query: '{q}')"
        data_accessed = "Search results and summary text"
    elif tool_name == "execute_terminal_command":
        cmd = parameters.get('command', '')
        external_content_involved = "Host OS Command Shell"
        data_accessed = f"Standard output of command: '{cmd}'"
    elif tool_name == "fetch_webpage":
        url = parameters.get('url', '')
        external_content_involved = f"HTTP Web Request ({url})"
        data_accessed = "Raw HTML/Text webpage source"
    elif tool_name == "execute_python_code":
        external_content_involved = "Local Python Interpreter Sandbox"
        data_accessed = "Executed script stdout and globals modifications"
    elif tool_name == "calculate_math":
        expr = parameters.get('expression', '')
        external_content_involved = "Math evaluation engine"
        data_accessed = f"Evaluated expression value for: '{expr}'"
    elif tool_name == "query_database":
        sql = parameters.get('sql_query', '')
        external_content_involved = "Local SQLite Database"
        data_accessed = f"Database rows matching query: '{sql}'"
    else:
        external_content_involved = f"System Tool: {tool_name}"
        data_accessed = f"Tool arguments: {str(parameters)}"
    
    if decision == "reject":
        status = "SKIPPED"
        response = f"❌ **Action Blocked**\n\n{policy_reasoning}"
        result_summary = "Action systematically rejected by decision engine."
        
    elif decision == "need approval":
        status = "SKIPPED"
        response = (
            f"⚠️ **Approval Required**\n\n"
            f"{policy_reasoning}\n\n"
            f"**Pending Execution Details:**\n"
            f"- **Tool**: `{tool_name}`\n"
            f"- **Arguments**: `{parameters}`\n\n"
            f"*Please approve this action via the dashboard to proceed.*"
        )
        result_summary = "Execution halted pending user approval."
        
    else:
        # ALLOW - Step 3: Tool Execution
        try:
            tool_func = {t.name: t for t in tools}[tool_name]
            
            import os
            is_gmail_tool = "gmail" in tool_name.lower() or any(x in tool_name.lower() for x in ["email", "recent_emails", "email_content", "draft"])
            needs_auth = is_gmail_tool and not os.path.exists("token.json")
            
            result = tool_func.invoke(parameters)
            data = result
            status = "SUCCESS"
            result_summary = f"Tool {tool_name} executed successfully."
            
            # Step 5: Natural Response Generation (Feed tool output back to LLM)
            tool_msg = ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            final_resp = _llm.invoke([sys_msg, HumanMessage(content=user_query), ai_msg, tool_msg])
            response = final_resp.content.strip()
            
            if needs_auth and os.path.exists("token.json"):
                response = "🔑 **Gmail Authentication Successful**\n*The system has successfully authenticated with your Google Account and saved credentials to token.json.*\n\n---\n\n" + response
            
        except Exception as exc:
            status = "FAILED"
            error_message = str(exc)
            response = f"⚠️ An error occurred while executing `{tool_name}`: {exc}"
            result_summary = "Tool execution failed."
            reasoning += " Failure occurred during execution."

    if suggestions:
        suggestion_prefix = "⚠️ **Did you mean?**\n" + "\n".join([f"- {s}" for s in suggestions]) + "\n\n---\n\n"
        response = suggestion_prefix + response

    # Step 4: Audit Logging
    audit_entry = log_action(
        user_instruction=user_query,
        intent=intent,
        tool_used=tool_used,
        agent_action=tool_name,
        external_content_involved=external_content_involved,
        data_accessed=data_accessed,
        risk_level=risk_level,
        decision=decision,
        parameters=parameters,
        status=status,
        reasoning=reasoning,
        result_summary=result_summary,
        error_message=error_message,
        event_id=thread_local_ctx.event_id
    )

    thread_local_ctx.event_id = None

    return {
        "intent":      intent,
        "response":    response,
        "tool_used":   tool_used,
        "risk_level":  risk_level,
        "status":      status,
        "audit_entry": audit_entry,
        "data":        data
    }
