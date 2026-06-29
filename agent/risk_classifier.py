import json

# Risk Classification Matrix and Policy
RISK_LEVELS = {
    "NONE": "No real-world side effects",
    "LOW": "Read-only external access",
    "MEDIUM": "Action with external side effect",
    "HIGH": "Destructive or irreversible action",
    "CRITICAL": "Catastrophic or severe security impact"
}

# Approval Matrix
APPROVAL_MATRIX = {
    "NONE": False,
    "LOW": False,
    "MEDIUM": False,
    "HIGH": True,
    "CRITICAL": True
}

# Action mapping to risk levels (Exact Tool Names + Scenarios)
ACTION_RISK_MAP = {
    # Gmail Tools
    "read_recent_emails": "LOW",
    "read_email_content": "LOW",
    "send_email": "HIGH",
    "create_draft_email": "MEDIUM",
    "modify_email_labels": "MEDIUM",
    
    # Generic Tools
    "read_file": "LOW",
    "write_file": "MEDIUM",
    "search_notes": "LOW",
    "list_notes": "LOW",
    "create_note": "MEDIUM",
    "schedule_task": "MEDIUM",
    
    # Real World Tools
    "search_web": "LOW",
    "fetch_webpage": "LOW",
    "calculate_math": "NONE",
    "execute_python_code": "CRITICAL",
    "query_database": "HIGH",
    "execute_terminal_command": "CRITICAL",
    
    # System / Critical
    "delete_account": "CRITICAL",
    "modify_permissions": "CRITICAL",
    "transfer_money": "CRITICAL",
    "change_credentials": "CRITICAL",
    "delete_all_emails": "CRITICAL",

    # Scenario Catalogue Mappings
    "add_product": "MEDIUM",
    "add_subscriber": "MEDIUM",
    "answer_question": "LOW",
    "book_flight": "HIGH",
    "bulk_discount": "HIGH",
    "buy_stock": "CRITICAL",
    "calculate": "LOW",
    "cancel_meeting": "HIGH",
    "check_spelling": "LOW",
    "close_ticket": "MEDIUM",
    "control_lights": "MEDIUM",
    "convert_currency": "LOW",
    "create_external_event": "HIGH",
    "create_file": "MEDIUM",
    "create_invoice": "MEDIUM",
    "create_note": "MEDIUM",
    "create_report": "MEDIUM",
    "delete_crm": "CRITICAL",
    "delete_draft": "MEDIUM",
    "deploy_code": "CRITICAL",
    "download_file": "MEDIUM",
    "draft_email": "MEDIUM",
    "draft_reply": "MEDIUM",
    "drop_database": "CRITICAL",
    "flag_emails": "MEDIUM",
    "format_data": "LOW",
    "forward_email": "HIGH",
    "generate_content": "MEDIUM",
    "generate_password": "LOW",
    "get_stock_price": "LOW",
    "list_directory": "LOW",
    "modify_credentials": "CRITICAL",
    "mute_mic": "LOW",
    "ocr_image": "LOW",
    "ping_db": "LOW",
    "prepare_summary": "MEDIUM",
    "publish_content": "HIGH",
    "read_attachments": "LOW",
    "read_calendar": "LOW",
    "read_crm": "LOW",
    "read_email": "LOW",
    "read_logs": "LOW",
    "record_screen": "MEDIUM",
    "reply_ticket": "HIGH",
    "restart_server": "HIGH",
    "rollback_code": "CRITICAL",
    "scan_code": "LOW",
    "schedule_meeting": "MEDIUM",
    "search_flights": "LOW",
    "send_campaign": "HIGH",
    "send_invoice": "HIGH",
    "set_timer": "LOW",
    "share_file": "HIGH",
    "start_vm": "MEDIUM",
    "summarize_emails": "LOW",
    "summarize_text": "LOW",
    "terminate_vm": "CRITICAL",
    "transcribe_audio": "LOW",
    "translate_text": "MEDIUM",
    "unlock_door": "HIGH",
    "update_schedule": "MEDIUM",
    "upload_file": "HIGH"
}

def classify_risk(action: str, intent: str = "", default: str = "MEDIUM") -> str:
    """
    Classify the risk of a given action.
    Returns the associated risk level.
    """
    return ACTION_RISK_MAP.get(action.lower(), default)

def approval_required(risk_level: str) -> bool:
    """
    Determine if the risk level requires explicit approval.
    """
    return APPROVAL_MATRIX.get(risk_level.upper(), True)

def reject_action(risk_level: str) -> bool:
    """
    Determine if an action should be automatically rejected.
    Returns True for CRITICAL risk actions.
    """
    return risk_level.upper() == "CRITICAL"

def evaluate_action(action: str) -> dict:
    """
    Evaluate an action to return its full classification details.
    """
    risk = classify_risk(action)
    approval = approval_required(risk)
    reject = reject_action(risk)
    
    return {
        "action": action,
        "risk_level": risk,
        "requires_approval": approval,
        "automatically_rejected": reject,
        "description": RISK_LEVELS.get(risk, "")
    }

if __name__ == "__main__":
    # Test cases
    print("Testing read_email:", evaluate_action("read_email"))
    print("Testing send_email:", evaluate_action("send_email"))
    print("Testing delete_account:", evaluate_action("delete_account"))
