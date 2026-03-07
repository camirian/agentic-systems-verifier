# System Architecture: Agentic Systems Verifier

This document outlines the formal C4 (Context, Container, Component, Code) architecture for the **Agentic Systems Verifier**, a platform designed to automate Systems Engineering workflows (like Requirements Verification) using Large Language Models.

This formalization substantiates Applied AI Architect and Systems Engineering software design claims (EDU_JHU_02).

## 1. System Context Diagram
*The high-level view showing how users and external systems interact with the platform.*

```mermaid
C4Context
    title System Context: Agentic Systems Verifier

    Person(SysEng, "Systems Engineer", "Uploads requirements, reviews AI-generated verification strategies and test code.")
    
    System(AgenticVerifier, "Agentic Systems Verifier", "Automates requirements analysis, Python test generation, and secure sandboxed execution.")
    
    System_Ext(GeminiAPI, "Google Gemini API", "Provides LLM reasoning for MBSE parsing, RAG evaluation, and Pytest code generation.")
    System_Ext(DOORS, "IBM DOORS Next Generation", "External ALM tool holding the technical baseline. Target for automated RPE exports.")

    Rel(SysEng, AgenticVerifier, "Uploads PDFs/CSVs, executes verification batches")
    Rel(AgenticVerifier, GeminiAPI, "Prompts for Verification Method (Test, Analysis, Inspection) and Pytest Code generation")
    Rel(AgenticVerifier, DOORS, "Simulates RPE API data extraction")
```

## 2. Container Diagram
*The distinct deployable units that make up the software system.*

```mermaid
C4Container
    title Container Diagram: Agentic Systems Verifier

    Person(SysEng, "Systems Engineer", "Primary User")

    Container_Boundary(CloudRun, "Google Cloud Run Environment") {
        Container(Frontend, "Next.js Web Frontend", "React, TypeScript, Tailwind", "Provides the Matrix View and 3-step Inspector Panel for verification workflows.")
        Container(Backend, "FastAPI Backend", "Python 3.10+", "Handles document parsing, AI orchestration, and sandboxed code execution.")
        ContainerDb(Database, "SQLite Database", "Local File", "Stores session requirements, generated code, and execution logs.")
    }

    System_Ext(GeminiAPI, "Google Gemini API", "LLM reasoning engine")

    Rel(SysEng, Frontend, "Views UI, clicks 'Execute Test'")
    Rel(Frontend, Backend, "RESTful API Calls (JSON)")
    Rel(Backend, Database, "Reads/Writes Requirement state via SQLAlchemy")
    Rel(Backend, GeminiAPI, "Sends context & parameters for completion")
```

## 3. Component Diagram (Backend API)
*Zooming into the Python FastAPI Backend container to view internal architectural blocks.*

```mermaid
C4Component
    title Component Diagram: FastAPI Backend

    Container_Boundary(Backend, "FastAPI Application") {
        Component(Router, "API Router", "FastAPI Endpoints", "Routes Next.js requests to appropriate controllers (/analyze, /execute, /upload)")
        
        Component(DocParser, "Document Parsing Engine", "PyMuPDF, CSV Reader", "Extracts textual requirements and constraints from unstructured PDFs.")
        
        Component(VerificationEngine, "Verification Engine", "Python class", "Orchestrates prompts, interacts with Gemini to assign methods and generate Pytests.")
        
        Component(ExecutionSandbox, "Subprocess Execution Sandbox", "Python subprocess", "Saves generated code to /tmp/ and runs it in isolation to prevent host contamination.")
        
        Component(MetricsModule, "RAG Evaluation Module", "/evaluation", "Scores generation quality based on Precision, Recall, and Faithfulness.")
        
        Component(SysMLPipeline, "SysML v2 Parser", "/sysml_v2", "Parses formal MBSE models via AST into JSON for LLM injection.")
    }

    System_Ext(GeminiAPI, "Google Gemini API", "LLM provider")
    ContainerDb(Database, "SQLite DB", "Session storage")

    Rel(Router, DocParser, "Triggers standard extraction")
    Rel(Router, VerificationEngine, "Requests AI completion")
    Rel(Router, ExecutionSandbox, "Executes verification method == 'Test' scripts")
    
    Rel(VerificationEngine, GeminiAPI, "Sends prompt payload")
    Rel(VerificationEngine, MetricsModule, "Logs telemetry/quality scores")
    Rel(VerificationEngine, Database, "Updates DB with generated AST/Code")
```

## Architectural Design Decisions & Trade-offs
1.  **Monolithic Storage (SQLite):** For MVP velocity and Cloud Run concurrency limitations (Scale to Zero), SQLite provides a simple, self-contained persistence layer without the network overhead of Cloud SQL.
2.  **Stateless Sandboxing (Subprocess):** Generated Pytests are executed via `subprocess.run(["python", "-m", "pytest", temp_file])`. While lacking full Docker isolation, it prevents basic namespace collisions and module bleeding during concurrent execution.
3.  **Client-Side Rate Limiting (10 Items):** Gemini Free-tier limits strictly enforce 15 Requests Per Minute (RPM). The `Next.js` frontend queues batched operations ("Generate Next 10") rather than overwhelming the FastAPI queue.
