# Contributing to Agentic Systems Verifier (ASV)

We welcome contributions to the Agentic Systems Verifier! To ensure the integrity of the "Iron Wall" isolate-agent architecture, please adhere to the following guidelines.

## 🏗️ Architectural Constraints
1.  **Agent Isolation:** The `Architect`, `Planner`, and `Builder` agents must *never* communicate directly. All state transfer must occur via structured JSON payloads through the central coordinating event bus.
2.  **Deterministic Testing:** The `Auditor` agent must rely solely on deterministic evaluation frameworks (e.g., `pytest`). Do not introduce LLM-based evaluation ("LLM-as-a-Judge") into the final verification gate.

## 🔄 Development Workflow
1.  Fork the repository and branch from `main`.
2.  Implement your changes, ensuring strict adherence to typing (`mypy`).
3.  Write test cases that explicitly cover the new semantic reasoning logic or prompt behavior.
4.  Run the local test suite: `pytest tests/`.
5.  Submit a Pull Request and ensure the Automated Verification Test Suite (GitHub Actions) passes.

## 📝 Commit Standards
We use Conventional Commits. Examples:
*   `feat(reasoning): update prompt logic to handle DO-254 errata`
*   `fix(auditor): resolve pytest parsing edge case`
