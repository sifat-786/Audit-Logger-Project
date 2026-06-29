from agent.risk_classifier import evaluate_action

def evaluate_decision(action: str) -> dict:
    """
    Determine the decision for a given action.
    Returns 'approved', 'need approval', or 'reject'.
    """
    evaluation = evaluate_action(action)
    
    if evaluation["automatically_rejected"]:
        decision = "reject"
    elif evaluation["requires_approval"]:
        decision = "need approval"
    else:
        decision = "approved"
        
    return {
        "action": action,
        "risk_level": evaluation["risk_level"],
        "decision": decision
    }

if __name__ == "__main__":
    print(evaluate_decision("read_email"))
    print(evaluate_decision("draft_email"))
    print(evaluate_decision("send_email"))
    print(evaluate_decision("delete_account"))
