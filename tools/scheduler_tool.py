import threading
import time
from datetime import datetime, timedelta
from dateutil.parser import parse
from agent.audit_logger import log_action

# Keep track of active tasks in memory
_scheduled_tasks = {}

def execute_task_callback(action_type: str, action_args: dict, parent_event_id: str):
    """Callback function executed in a background thread when the delay expires."""
    try:
        if action_type == "send_email":
            from tools.gmail_tool import send_email
            res = send_email(
                to=action_args.get("to"),
                subject=action_args.get("subject"),
                body=action_args.get("body")
            )
        elif action_type == "create_note":
            from tools.generic_tools import create_note
            res = create_note(content=action_args.get("content"))
        elif action_type == "write_file":
            from tools.generic_tools import write_file
            res = write_file(
                filepath=action_args.get("filepath"),
                content=action_args.get("content")
            )
        else:
            res = f"Error: Unsupported action type '{action_type}'"
            
        # Determine status
        status = "SUCCESS"
        if isinstance(res, dict) and res.get("status") == "ERROR":
            status = "FAILED"
        elif "error" in str(res).lower():
            status = "FAILED"
            
        # Log completion event
        log_action(
            user_instruction=f"Asynchronous execution of scheduled task: {action_type}",
            intent=action_type.upper(),
            tool_used=action_type,
            agent_action=action_type,
            external_content_involved=f"Daemon Scheduler (Trigger Ref: {parent_event_id})",
            data_accessed=f"Arguments: {action_args}",
            risk_level="HIGH" if action_type == "send_email" else "MEDIUM",
            decision="approved",
            parameters=action_args,
            status=status,
            reasoning=f"Asynchronously executed background task scheduled by event {parent_event_id}.",
            result_summary=str(res)
        )
    except Exception as e:
        log_action(
            user_instruction=f"Asynchronous execution of scheduled task: {action_type}",
            intent=action_type.upper(),
            tool_used=action_type,
            agent_action=action_type,
            external_content_involved=f"Daemon Scheduler (Trigger Ref: {parent_event_id})",
            data_accessed=f"Arguments: {action_args}",
            risk_level="HIGH" if action_type == "send_email" else "MEDIUM",
            decision="approved",
            parameters=action_args,
            status="FAILED",
            reasoning=f"Failed to execute background task scheduled by event {parent_event_id}.",
            result_summary=f"Execution error: {e}"
        )

def schedule_action(target_time: str, action_type: str, action_args: dict, parent_event_id: str = "SYSTEM") -> str:
    """
    Schedules an action (e.g. send_email, write_file) to run at a specific future target time.
    
    :param target_time: E.g. "2:09 AM" or "2026-06-16 02:09:00"
    :param action_type: The name of the tool/action (e.g. "send_email")
    :param action_args: Dictionary of arguments (e.g. {"to": "...", "subject": "...", "body": "..."})
    :return: A confirmation message.
    """
    try:
        import re
        now = datetime.now()
        target_time_clean = target_time.strip().lower()
        
        # Parse relative or absolute time
        match = re.search(r'in\s+(\d+)\s+(second|sec|minute|min|hour|hr|day)s?', target_time_clean)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if 'second' in unit or 'sec' in unit:
                target_dt = now + timedelta(seconds=amount)
            elif 'minute' in unit or 'min' in unit:
                target_dt = now + timedelta(minutes=amount)
            elif 'hour' in unit or 'hr' in unit:
                target_dt = now + timedelta(hours=amount)
            elif 'day' in unit:
                target_dt = now + timedelta(days=amount)
        else:
            target_dt = parse(target_time)
            
        # Handle timezone naive/aware comparison
        if target_dt.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=target_dt.tzinfo)
        elif target_dt.tzinfo is None and now.tzinfo is not None:
            target_dt = target_dt.replace(tzinfo=now.tzinfo)
            
        # If the target time has already passed today (e.g., they ask for 2:09 AM but it's 2:12 AM),
        # assume they mean tomorrow at that time.
        if target_dt < now:
            if target_dt.date() == now.date():
                target_dt += timedelta(days=1)
                
        delay_seconds = (target_dt - now).total_seconds()
        
        if delay_seconds < 0:
            return f"Error: Calculated delay ({delay_seconds:.1f}s) is negative. Cannot schedule in the past."
            
        # Start a daemon thread
        t = threading.Thread(
            target=lambda: (time.sleep(delay_seconds), execute_task_callback(action_type, action_args, parent_event_id))
        )
        t.daemon = True
        t.start()
        
        task_id = f"TASK-{int(time.time())}"
        _scheduled_tasks[task_id] = {
            "target_time": target_dt.isoformat(),
            "action_type": action_type,
            "args": action_args,
            "thread": t
        }
        
        return f"Successfully scheduled task '{action_type}' to run at {target_dt.strftime('%Y-%m-%d %I:%M:%S %p')} (in {delay_seconds:.1f} seconds)."
    except Exception as e:
        return f"Error scheduling task: {e}"
