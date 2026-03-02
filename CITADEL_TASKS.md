# Citadel Proofing Tasks — `agentic-systems-verifier`

> **Sprint 1** — These deliverables close 4 resume gap claims by expanding the scope of this repo.

## Deliverables

### 1. `/evaluation` Module (Claim: AI_NG_02)
**Goal:** Prove quantitative RAG evaluation and hallucination prevention methodology.

- [ ] Create `src/evaluation/` package
- [ ] Implement precision, recall, and faithfulness scoring against a gold-standard Q&A dataset
- [ ] Add a `ragas`-style evaluation pipeline that measures retrieval quality
- [ ] Write unit tests validating metric calculations
- [ ] Add a summary section to `README.md` linking to the evaluation module

### 2. `/sysml_v2` Folder (Claim: AI_NG_03)
**Goal:** Prove SysML v2 → LLM code generation pipeline.

- [ ] Create `sysml_v2/` directory with a sample `.sysml` model (e.g., a system block definition)
- [ ] Write a `sysml_to_json.py` parser that exports the model to JSON
- [ ] Demonstrate feeding the JSON into the Gemini prompt context window
- [ ] Show the LLM generating verifiable Python code from the model

### 3. `ARCHITECTURE.md` (Claim: EDU_JHU_02)
**Goal:** Prove software systems engineering rigor via a formal C4 architecture model.

- [ ] Create `ARCHITECTURE.md` at repo root
- [ ] Document Context (C1), Container (C2), and Component (C3) views
- [ ] Include Mermaid diagrams for each level
- [ ] Map components to actual source code modules

### 4. `/tools/doors_export_mock.py` (Claim: CPS_PER_01)
**Goal:** Prove DOORS requirements extraction and data pipeline automation.

- [ ] Create `tools/` directory
- [ ] Write `doors_export_mock.py` that parses structured requirements from PDF/markdown
- [ ] Output structured CSV/JSON with requirement IDs, text, verification methods
- [ ] Demonstrate how the output feeds into the ASV ingestion pipeline
