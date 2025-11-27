# Agentic Systems Verifier - User Interface Guide

**Version:** 1.1
**Date:** November 2025
**Audience:** Systems Engineers, Compliance Officers, and Technical Auditors

---

## 1. Introduction

The **Agentic Systems Verifier (ASV)** is a "Human-in-the-Loop" AI platform that automates the verification of safety-critical software specifications. It follows the formal **V-Model** methodology, guiding you from Requirement Decomposition to Verification and Traceability.

---

## 2. The Mission Control Interface

The sidebar is your command center. It tracks your progress through the V-Model phases:

### 2.1 Project Selection (New)
*   **Multi-Project Support:** Use the **"📂 Active Specification"** dropdown at the top of the sidebar to switch between different projects (e.g., NASA vs. DoD).
*   **Global Filtering:** Selecting a project instantly filters the RTM, Metrics, and Logs to show only data for that specification.

### 🔵 Phase 1: Decomposition (Setup)
*   **Goal:** Ingest a raw PDF and break it down into atomic requirements.
*   **Action:**
    1.  Open the **"⚙️ Mission Setup"** drawer.
    2.  **Upload Spec:** Drag and drop your PDF (e.g., NASA BPSec). The system will automatically switch to this new project.
    3.  **Target Section:** (Optional) Enter a section number (e.g., "3.2") to focus the AI. Leave blank to scan the whole doc.
    4.  **Initialize Agents:** Click to start ingestion.
*   **Visual Cue:** The Phase Tracker at the top shows **"1. Decomposition"** as active.

### 🔵 Phase 2: Verification (Analysis & Code Gen)
*   **Goal:** Analyze requirements and generate verification artifacts.
*   **Action:**
    1.  **Run Verification:** Click **"▶️ Run Verification"** to analyze requirements.
    2.  **Generate Code:** Open the **Inspector** for a "Test" requirement and click **"⚡ Generate Test Case"**. The AI will write a custom `pytest` script in real-time.
*   **Modes:**
    *   **Batch Mode:** If *nothing* is selected in the main table, the AI verifies **ALL** pending requirements.
    *   **Surgical Mode:** If you select a specific row (checkbox), the AI verifies **ONLY** that requirement.
*   **Visual Cue:** The Phase Tracker moves to **"2. Verification"**.

### 🟢 Phase 3: Traceability (Report)
*   **Goal:** Review compliance and generate reports.
*   **Action:**
    1.  Check the **"Verification Metrics"** tab for pass/fail rates.
    2.  **Export VCRM:** Click **"📥 Download VCRM (Excel)"** to export the full compliance matrix.
*   **Visual Cue:** The Phase Tracker turns **Green** and shows **"3. Traceability"**.

---

## 3. The Requirements Matrix (RTM)

The main view is the **Requirements Traceability Matrix**. It is a live, interactive database.

### 3.1 Viewing & Editing
*   **Inspector:** Click any row to open the **"Requirement Inspector"** in the sidebar.
    *   **Manual Overrides:** Use the "🛠️ Manual Overrides" panel to force-update Status, Priority, or Method. Changes are flagged as "⚠️ Modified".
    *   **Code View:** See the AI-generated test code directly in the inspector.
*   **Inline Editing:** Double-click any cell in the "Requirement" column to fix typos or clarify text.
*   **Audit Trail:** Any change you make is logged. Modified requirements are flagged with a "⚠️ Modified" tag and tracked in the "Change Manifest" expander.

### 3.2 Status Indicators
*   **🟡 Pending:** Not yet analyzed.
*   **🟢 Verified:** The AI (or you) confirmed the requirement is met/valid.
*   **🔴 Failed:** The requirement is ambiguous, missing code, or logically inconsistent.

---

## 4. Troubleshooting

| Symptom                | Probable Cause     | Resolution                                                                                                                       |
| :--------------------- | :----------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| **"ImportError"**      | Python Environment | Ensure you are running `streamlit run app.py` from the root directory.                                                           |
| **AI Hangs**           | API Rate Limit     | The system automatically handles rate limits, but if it hangs for >1 min, restart the app.                                       |
| **Verification Fails** | Ambiguous Text     | If the AI marks a requirement as "Failed" due to ambiguity, use the **Inspector** to rewrite the text, then re-run verification. |

---

## 5. Support

For technical support, please refer to the `README.md` or contact the internal development team.
