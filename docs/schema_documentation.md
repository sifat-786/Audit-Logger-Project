# Audit Log Schema Documentation

## 1. JSON Schema (`audit_log.json`)

The JSON audit log is an array of objects representing individual audit events.

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "session_id": { "type": "string", "description": "Process-scoped session identifier" },
      "event_id": { "type": "string", "description": "Unique identifier per action" },
      "timestamp": { "type": "string", "format": "date-time", "description": "ISO-8601 timestamp with timezone" },
      "user_instruction": { "type": "string", "description": "Original user instruction" },
      "intent": { "type": "string", "description": "Detected intent by the controller" },
      "tool_used": { "type": "string", "description": "Specific tool invoked" },
      "agent_action": { "type": "string", "description": "Internal action identifier" },
      "external_content_involved": { "type": "string", "description": "External files, emails, or APIs involved" },
      "data_accessed": { "type": "string", "description": "Specific data read or written during execution" },
      "risk_level": { "type": "string", "enum": ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"], "description": "Assessed risk classification" },
      "decision": { "type": "string", "enum": ["approved", "need approval", "reject"], "description": "Governance decision outcome" },
      "parameters": { "type": "object", "description": "Parameters passed to the tool" },
      "status": { "type": "string", "enum": ["SUCCESS", "FAILED", "SKIPPED"], "description": "Execution outcome" },
      "reasoning": { "type": "string", "description": "Explanation for why the action was taken" },
      "result_summary": { "type": "string", "description": "Summary of the tool's output" },
      "error_message": { "type": "string", "description": "Error details if the action failed" }
    },
    "required": [
      "event_id", 
      "session_id", 
      "timestamp", 
      "user_instruction", 
      "intent", 
      "tool_used", 
      "agent_action", 
      "external_content_involved", 
      "data_accessed", 
      "risk_level", 
      "decision", 
      "status", 
      "reasoning"
    ]
  }
}
```

## 2. CSV Schema (`audit_log.csv`)

The CSV audit log provides a flat, spreadsheet-friendly representation of the audit events. Complex structures like `parameters` are serialized as JSON strings.

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `session_id` | String | Process-scoped session identifier |
| `event_id` | String | Unique identifier per action |
| `timestamp` | String | ISO-8601 timestamp with timezone |
| `user_instruction` | String | Original user instruction |
| `intent` | String | Detected intent by the controller |
| `tool_used` | String | Specific tool invoked |
| `agent_action` | String | Internal action identifier |
| `external_content_involved` | String | External files, emails, or APIs involved |
| `data_accessed` | String | Specific data read or written during execution |
| `risk_level` | String | Assessed risk classification (`NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) |
| `decision` | String | Governance decision outcome (`approved`, `need approval`, `reject`) |
| `parameters` | String (JSON) | Serialized JSON string of parameters passed to the tool |
| `status` | String | Execution outcome (`SUCCESS`, `FAILED`, `SKIPPED`) |
| `reasoning` | String | Explanation for why the action was taken |
| `result_summary` | String | Summary of the tool's output |
| `error_message` | String | Error details if the action failed |

## 3. SQLite Schema (`audit_log.db`)

The SQLite database provides a persistent, queryable storage format for the audit events.

```sql
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
    parameters TEXT,       -- Stored as serialized JSON
    status TEXT,
    reasoning TEXT,
    result_summary TEXT,
    error_message TEXT
);
```
