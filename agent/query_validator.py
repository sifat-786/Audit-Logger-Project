import re

# Common email domain typo mappings
EMAIL_TYPO_MAP = {
    r"\b([a-zA-Z0-9._%+-]+)@gmal\.com\b": "gmail.com",
    r"\b([a-zA-Z0-9._%+-]+)@gamil\.com\b": "gmail.com",
    r"\b([a-zA-Z0-9._%+-]+)@gmial\.com\b": "gmail.com",
    r"\b([a-zA-Z0-9._%+-]+)@hotmal\.com\b": "hotmail.com",
    r"\b([a-zA-Z0-9._%+-]+)@yaho\.com\b": "yahoo.com",
    r"\b([a-zA-Z0-9._%+-]+)@outlok\.com\b": "outlook.com",
}

# Missing dot in common domains
MISSING_DOT_MAP = {
    r"\b([a-zA-Z0-9._%+-]+)@gmailcom\b": "gmail.com",
    r"\b([a-zA-Z0-9._%+-]+)@yahoocom\b": "yahoo.com",
    r"\b([a-zA-Z0-9._%+-]+)@hotmailcom\b": "hotmail.com",
    r"\b([a-zA-Z0-9._%+-]+)@outlookcom\b": "outlook.com",
}

# Common action/keyword spelling errors
KEYWORD_TYPO_MAP = {
    r"\bdelte\b": "delete",
    r"\brestar\b": "restart",
    r"\bcread\b": "create",
    r"\bexcute\b": "execute",
    r"\bdrob\b": "drop",
    r"\bseach\b": "search",
}

def validate_query(query: str) -> list[str]:
    """
    Analyzes the query for common typos and spelling errors.
    Returns a list of suggestion/warning messages if anomalies are detected.
    """
    suggestions = []

    # 1. Check email domain typos
    for pattern, correct in EMAIL_TYPO_MAP.items():
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            suggestions.append(
                f"It looks like you wrote `{match}@gmal.com` (or a similar typo). "
                f"Did you mean `{match}@{correct}`?"
            )

    # 2. Check missing dot in email domains
    for pattern, correct in MISSING_DOT_MAP.items():
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            suggestions.append(
                f"It looks like you wrote `{match}@gmailcom` (or a similar typo). "
                f"Did you mean `{match}@{correct}`? (Missing dot before TLD)."
            )

    # 3. Check command keywords typos
    for typo, correct in KEYWORD_TYPO_MAP.items():
        if re.search(typo, query, re.IGNORECASE):
            clean_typo = typo.replace(r"\b", "")
            suggestions.append(
                f"Detected possible typo `{clean_typo}`. "
                f"Did you mean `{correct}`?"
            )

    return suggestions
