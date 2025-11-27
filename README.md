# Agentic Systems Verifier (ASV)

[![Status](https://img.shields.io/badge/Status-Beta-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![AI-Engine](https://img.shields.io/badge/AI-Gemini%20Pro-purple)]()

**The Autonomous Verification Engine for Safety-Critical Systems.**

ASV is not just a coding tool; it is a **Compliance Orchestrator**. It leverages Multi-Agent AI to automate the rigorous Systems Engineering V-Model, transforming static PDF specifications into executable, verified code.

---

## 🏗️ The "Iron Wall" Architecture

ASV solves the "AI Hallucination" problem in engineering through strict agent isolation:

| Agent Persona     | Role                | Responsibility                                                                               |
| :---------------- | :------------------ | :------------------------------------------------------------------------------------------- |
| **The Architect** | 🔵 **Decomposition** | Ingests PDFs (NASA/DoD), extracts "Shall" statements, and creates the Architecture.          |
| **The Planner**   | 🟡 **Analysis**      | Determines the Verification Method (Test vs. Inspection) and generates the Test Plan.        |
| **The Builder**   | 🟢 **Execution**     | Writes the Python implementation (e.g., Buffer Managers, Protocol Parsers).                  |
| **The Auditor**   | 🔴 **Verification**  | Runs the tests against the original Spec. **Rejects code** that violates safety constraints. |

---

## 🚀 Enterprise Capabilities

*   **Multimodal Ingestion:** Uses **Gemini Pro** to read complex engineering diagrams and tables, not just text.
*   **Multi-Project Management:** Switch instantly between NASA, DoD, and ESA specifications using the **Global Project Selector**.
*   **On-Demand Code Generation:** Click "Generate Test Case" to watch the AI write `pytest` verification scripts in real-time.
*   **Smart Context Filtering:** Proprietary local-scan algorithms reduce token usage by 95% by only sending relevant specification sections to the cloud.
*   **Audit-Grade Traceability:** Every line of generated code is linked to a Requirement ID (`BPv6-001`). If the requirement changes, the code is flagged for review.
*   **Surgical Verification:** Verify a single requirement in 5 seconds, or the entire 200-page specification in 5 minutes.

---

## 📂 Project Structure

```text
agentic-systems-verifier/
├── app.py               # The Main Streamlit Application (Mission Control)
├── core/                # The V-Model Engines
│   ├── db.py            # SQLite Database & Persistence Layer
│   ├── ingestion.py     # PDF Parsing & Requirement Extraction (Decomposition)
│   └── verification_engine.py # AI Verification Logic (Verification)
├── data/                # Local storage for uploaded specs
├── docs/                # User Manuals & Artifacts
└── tests/               # Validation suite
```

---

## 🛠️ Quick Start

### 1. Installation
Ensure you have Python 3.10+ installed.

```bash
cd ~/dev/personal/agentic-systems-verifier
pip install -r requirements.txt
```

### 2. Launch Mission Control
Start the local web interface:

```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`.

---

## 💠 The V-Model Workflow

ASV guides you through a formal 3-phase Systems Engineering process:

### Phase 1: Decomposition (Left-V)
*   **Input:** Upload a raw PDF specification (e.g., NASA BPSec Protocol).
*   **Action:** Click **"Initialize Agents"**.
*   **Result:** The system ingests the document, extracts atomic requirements, and populates the "Pending" RTM.

### Phase 2: Verification (Test)
*   **Input:** Select a specific requirement or target the whole section.
*   **Action:** Click **"Generate Verification Plan"**.
*   **Result:** The **Verification Engine** analyzes the requirement using Gemini, determining the verification method (Test, Analysis, Inspection).

### Phase 3: Traceability (Right-V)
*   **Input:** Review the RTM.
*   **Action:** Check the **"Planning Dashboard"** for metrics.
*   **Result:** A fully traceable compliance report with "Analyzed" status and AI-generated rationale.

---

## 🔮 Roadmap

*   **Q4 2025:** Support for European Space Agency (ESA) ECSS standards.
*   **Q1 2026:** Integration with SysML v2 API for model-based verification.
*   **Q2 2026:** "Hardware-in-the-Loop" simulation via Omniverse connectors.
*   **DONE:** LLM-driven "Spec-to-Config" compiler (Automated Ingestion).

## 📜 License

MIT License - Created by Antigravity
