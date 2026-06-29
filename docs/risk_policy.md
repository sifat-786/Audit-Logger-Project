# Risk Classification and Approval Policy

## 1. Risk Matrix

Every agent action must be classified into one of the following five risk categories:

| Risk Level | Definition | Scope of Impact | Example Actions |
| :--- | :--- | :--- | :--- |
| **NONE** | No real-world side effects. Pure computational or conversational output. | Local memory, LLM context window | Answer a question, summarize provided text, math calculations |
| **LOW** | Read-only external access. No external state is modified. | Read access to files, emails, or APIs | Read an email, view a calendar, search notes, read database |
| **MEDIUM** | Internal side effects or low-risk external modification. Reversible or isolated impact. | Internal data structures, drafts, local files | Draft an email, create a local report, update internal schedule |
| **HIGH** | External side effects that impact third parties or are difficult to reverse. | External communication, significant internal changes | Send an email, share a file, book a flight, create a calendar event |
| **CRITICAL** | Destructive, severe security implications, or major financial impact. Irreversible. | System configuration, access control, financial | Delete an account, modify permissions, transfer money, wipe database |

## 2. Approval Matrix

The system enforces the following approval requirements based on the assessed risk level:

| Risk Level | Requires Explicit Approval? | Auto-Reject Conditions |
| :--- | :--- | :--- |
| **NONE** | **No** (ALLOW) | None |
| **LOW** | **No** (ALLOW) | None |
| **MEDIUM** | **No** (ALLOW)* | None |
| **HIGH** | **Yes** (APPROVAL_REQUIRED) | None |
| **CRITICAL** | **Yes** (APPROVAL_REQUIRED)** | Systematically rejected for non-admin users |

*\* MEDIUM risk actions are allowed by default but are heavily logged and may trigger anomalous activity alerts if invoked at high frequency.*
*\*\* CRITICAL actions are typically rejected outright unless explicitly overridden by a highly privileged human administrator.*

## 3. Policy Rules

1. **Default Deny:** If an action cannot be recognized or classified by the Intent Detection engine, it defaults to **MEDIUM** risk and may be flagged for review. If the tool is unknown, it defaults to **HIGH** risk and requires approval.
2. **Audit Mandatory:** All actions, regardless of risk level (even NONE), MUST be recorded in the audit trail.
3. **Traceability:** High and Critical risk actions must include the explicit user approval timestamp in the audit log.
4. **Explanation Requirement:** Any action that is halted (APPROVAL_REQUIRED or REJECT) must generate a human-readable explanation using the Explanation Engine.
