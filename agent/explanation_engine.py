from agent.decision_engine import evaluate_decision

EXPLANATION_TEMPLATES = {
    "approved": "This is a {risk_level} risk operation and does not modify external systems or violate core safety policies. Action allowed.",
    "need approval": "This {risk_level} risk operation requires explicit human approval because it has external side effects or modifies critical state.",
    "reject": "This action has been rejected because it is classified as {risk_level} and violates strict security boundaries."
}

def generate_explanation(action: str) -> dict:
    """
    Generates a human-readable explanation for the decision on an action.
    """
    decision_data = evaluate_decision(action)
    decision = decision_data["decision"]
    risk_level = decision_data["risk_level"]
    
    # Custom specific explanations for demonstration
    if action == "send_email":
        explanation = "External communication can affect third parties and therefore requires additional approval."
    elif action == "read_email":
        explanation = "This is a read-only operation and does not modify external systems."
    elif action == "delete_account":
        explanation = "Deleting an account is a catastrophic, irreversible action and is strictly blocked by system policy."
    else:
        # Fallback template
        template = EXPLANATION_TEMPLATES.get(decision, "Action evaluated.")
        explanation = template.format(risk_level=risk_level.lower())
        
    decision_data["explanation"] = explanation
    return decision_data

if __name__ == "__main__":
    print(generate_explanation("read_email"))
    print(generate_explanation("draft_email"))
    print(generate_explanation("send_email"))
    print(generate_explanation("delete_account"))
