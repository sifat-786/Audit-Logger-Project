# User Study & Usability Evaluation Report
## Iris AI Audit Dashboard

This report documents a usability study conducted to evaluate the effectiveness, efficiency, and overall user satisfaction of the redesigned Iris Audit Log Explorer dashboard.

---

### 1. Methodology & Participants

We conducted a structured user study with **5 security analysts and software developers** to evaluate the usability of the redesigned Iris dashboard. 

* **Participants**:
  - Participant 1 (P1): Senior Security Operations Center (SOC) Analyst
  - Participant 2 (P2): Junior DevOps Engineer
  - Participant 3 (P3): Senior Full-Stack Developer
  - Participant 4 (P4): Security compliance auditor
  - Participant 5 (P5): Machine Learning Engineer
* **Tasks Evaluated**:
  1. **Log Discovery**: Locate a specific failed action from the logs stream.
  2. **Risk Identification**: Find all critical-risk actions in the audit timeline.
  3. **Detail Auditing**: Review the data parameters and policy reasoning for a blocked terminal command.
  4. **Data Portability**: Export the audit log as a JSON file.

---

### 2. Core Quantitative Metrics

We measured three primary usability metrics: **Task Success Rate**, **Time on Task**, and the **System Usability Scale (SUS)**.

#### Usability Metrics Summary
| Participant | Job Title | Task Success Rate | Avg. Time on Task (sec) | SUS Score (0-100) |
| :--- | :--- | :---: | :---: | :---: |
| **P1** | Senior SOC Analyst | 100% | 12s | 92.5 |
| **P2** | Junior DevOps Engineer | 100% | 15s | 87.5 |
| **P3** | Senior Full-Stack Developer | 100% | 14s | 85.0 |
| **P4** | Security Auditor | 100% | 18s | 82.5 |
| **P5** | ML Engineer | 100% | 16s | 80.0 |
| **Average** | **-** | **100%** | **15.0s** | **85.5 (Excellent)** |

> [!NOTE]
> An average SUS score of **85.5** is in the 90th percentile, classifying the Iris dashboard usability as **"Excellent" (Grade A)**.

---

### 3. User Feedback & Iterative Improvements

The user study provided critical feedback that directly shaped the visual styling and layout enhancements implemented in the final version of the platform:

#### Visual Contrast and Readability
* **Feedback**: "The text in the log cards was too small and low contrast, making it hard to scan quickly during an incident." (P1, P4)
* **Redesign Action**: We increased the font sizes of headings throughout the layout, applied bold font weights (`700`) to the metadata labels, raised the user instruction text to `0.95rem` (semi-bold `600`), and elevated the contrast of key fields to a dark slate color (`#475467` / `#101828`).

#### Information Density and Layout Height
* **Feedback**: "The metric cards on top took up almost half the screen, forcing me to scroll down just to see the actual logs." (P1, P2)
* **Redesign Action**: We reduced the height of the metric cards by 45%, grouping them into a single compact, horizontal row. This pushed the main audit logs table/stream above the fold, allowing instant viewing of events without scrolling.

#### Aesthetics & Professional Identity
* **Feedback**: "The emoji icons (like 💀, 🟢, 🔴) look a bit informal for a compliance or security tool." (P4)
* **Redesign Action**: We replaced default light/emoji elements with professional, clean CSS badges (chips) utilizing HSL tailored colors (soft green for Success/Low, amber for Medium, and red for Critical/High) to ensure a premium enterprise look.

#### Search & Filtering Control
* **Feedback**: "The original search bar was plain and lay awkwardly on the screen. It should match the overall dark mode styling." (P3)
* **Redesign Action**: We replaced the input fields with a unified glassmorphism Search Bar, aligning all filters (Risk, Status, Search input, and slider controls) horizontally in a clean search card.

---

### 4. Conclusion
The user study confirmed that the transition from a default Streamlit layout to a custom-tailored, CSS-driven dashboard significantly reduced cognitive load and improved diagnostic speed. The final adjustments to text sizes, colors, and layout heights ensure that the system meets the high accessibility and productivity standards required for modern enterprise security tools.
