# Changelog

All notable changes to the **Agentic Systems Verifier** project will be documented in this file.

## [1.1.0] - 2025-11-24

### 🚀 New Features
*   **V-Model Workflow:** Implemented a formal 3-phase workflow (Decomposition -> Verification -> Traceability) with a visual tracker in the sidebar.
*   **Verification Engine:** Added `core/verification_engine.py` powered by Gemini 2.0 Pro to autonomously analyze requirements.
*   **Mission Control UI:** Completely refactored the sidebar into a "Mission Control" center with collapsible drawers and high-contrast controls.
*   **Surgical Verification:** Users can now verify a single requirement by selecting it in the RTM.
*   **Persistent Logging:** System logs are now stored in SQLite (`core/db.py`) and persist across sessions.

### 💅 UI/UX Improvements
*   **Nord Theme:** Applied a consistent Nord color palette (Polar Night, Snow Storm, Frost) via custom CSS.
*   **RTM Inspector:** Added a "Requirement Inspector" that dynamically appears when a row is selected.
*   **Audit Trail:** Added visual indicators ("⚠️ Modified") for requirements edited by the user.

### 🐛 Bug Fixes
*   Fixed `ImportError` caused by module name collision in `core/engine`.
*   Fixed "Target Section" being mandatory; it is now optional (defaults to "Verify All").
*   Fixed "Run Verification" triggering full analysis even when a single row was selected.

---

## [1.0.0] - 2025-11-20

### Initial Release
*   Basic PDF Ingestion.
*   Streamlit Interface.
*   SQLite Database Integration.
