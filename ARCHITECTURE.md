# System Architecture: Agentic Systems Verifier

This document outlines the formal C4 (Context, Container, Component, Code) architecture for the **Agentic Systems Verifier**, a platform designed to automate Systems Engineering workflows (like Requirements Verification) using Large Language Models.

This formalization substantiates Applied AI Architect and Systems Engineering software design claims (EDU_JHU_02).

## 1. System Context Diagram
*The high-level view showing how users and external systems interact with the platform.*

```mermaid
C4Context
    title System Context: Agentic Systems Verifier

    Person(SysEng, "Systems Engineer", "Uploads requirements,<br>reviews AI-generated<br>verification & code.")
    
    System(AgenticVerifier, "Agentic Systems Verifier", "Automates requirements analysis,<br>Python test generation, and<br>secure execution.")
    
    System_Ext(GeminiAPI, "Google Gemini API", "Provides LLM reasoning for<br>MBSE parsing and Pytest generation.")
    System_Ext(DOORS, "DOORS Next Generation", "External ALM tool holding the technical baseline.")

    Rel_D(SysEng, AgenticVerifier, "Uploads PDFs/CSVs,<br>executes verification batches")
    Rel_R(AgenticVerifier, GeminiAPI, "Prompts for Verification Method<br>and Pytest Code")
    Rel_D(AgenticVerifier, DOORS, "Simulates RPE API data extraction")
```

## 2. Container Diagram
*The distinct deployable units that make up the software system.*

```mermaid
C4Container
    title Container Diagram: Agentic Systems Verifier

    Person(SysEng, "Systems Engineer", "Primary User")

    Container_Boundary(CloudRun, "Google Cloud Run Environment") {
        Container(Frontend, "Next.js Web Frontend", "React, TypeScript", "Provides the Matrix View and<br>3-step Inspector Panel.")
        Container(Backend, "FastAPI Backend", "Python 3.10+", "Handles document parsing,<br>AI orchestration, and execution.")
        ContainerDb(Database, "SQLite Database", "Local File", "Stores session requirements,<br>generated code, and logs.")
    }

    System_Ext(GeminiAPI, "Google Gemini API", "LLM engine")

    Rel(SysEng, Frontend, "Views UI,<br>clicks 'Execute Test'")
    Rel(Frontend, Backend, "RESTful API Calls<br>(JSON)")
    Rel(Backend, Database, "Reads/Writes state<br>via SQLAlchemy")
    Rel_R(Backend, GeminiAPI, "Sends context & parameters<br>for completion")
    
    UpdateRelStyle(SysEng, Frontend, $offsetX="-50", $offsetY="-20")
    UpdateRelStyle(Frontend, Backend, $offsetX="-50", $offsetY="-20")
    UpdateRelStyle(Backend, Database, $offsetX="-50", $offsetY="20")
```

## 3. Component Diagram (Backend API)
*Zooming into the Python FastAPI Backend container to view internal architectural blocks.*

```mermaid
C4Component
    title Component Diagram: FastAPI Backend

    Container_Boundary(Backend, "FastAPI Application") {
        Component(Router, "API Router", "FastAPI Endpoints", "Routes requests to controllers")
        
        Component(DocParser, "Document Parsing Engine", "PyMuPDF, CSV Reader", "Extracts requirements<br>from basic PDFs.")
        
        Component(VerificationEngine, "Verification Engine", "Python class", "Interacts with Gemini to assign<br>methods and generate Pytests.")
        
        Component(ExecutionSandbox, "Subprocess Execution Sandbox", "Python subprocess", "Runs code in isolation<br>to prevent contamination.")
        
        Component(MetricsModule, "RAG Evaluation Module", "/evaluation", "Scores generation quality based<br>on Precision, Recall, Faithfulness.")
        
        Component(SysMLPipeline, "SysML v2 Parser", "/sysml_v2", "Parses formal MBSE models via<br>AST into JSON for LLM.")
    }

    System_Ext(GeminiAPI, "Google Gemini API", "LLM provider")
    ContainerDb(Database, "SQLite DB", "Session storage")

    Rel(Router, DocParser, "Triggers extraction")
    Rel(Router, VerificationEngine, "Requests AI completion")
    Rel(Router, ExecutionSandbox, "Executes 'Test' scripts")
    
    Rel(VerificationEngine, GeminiAPI, "Sends prompt payload")
    Rel(VerificationEngine, MetricsModule, "Logs telemetry/scores")
    Rel(VerificationEngine, Database, "Updates DB values")
    
    UpdateRelStyle(Router, DocParser, $offsetX="-40", $offsetY="-20")
    UpdateRelStyle(Router, VerificationEngine, $offsetX="20", $offsetY="20")
    UpdateRelStyle(Router, ExecutionSandbox, $offsetX="-40", $offsetY="20")
    UpdateRelStyle(VerificationEngine, GeminiAPI, $offsetX="20", $offsetY="-20")
    UpdateRelStyle(VerificationEngine, MetricsModule, $offsetX="-30", $offsetY="20")
    UpdateRelStyle(VerificationEngine, Database, $offsetX="20", $offsetY="20")
```

## Architectural Design Decisions & Trade-offs
1.  **Monolithic Storage (SQLite):** For MVP velocity and Cloud Run concurrency limitations (Scale to Zero), SQLite provides a simple, self-contained persistence layer without the network overhead of Cloud SQL.
2.  **Stateless Sandboxing (Subprocess):** Generated Pytests are executed via `subprocess.run(["python", "-m", "pytest", temp_file])`. While lacking full Docker isolation, it prevents basic namespace collisions and module bleeding during concurrent execution.
3.  **Client-Side Rate Limiting (10 Items):** Gemini Free-tier limits strictly enforce 15 Requests Per Minute (RPM). The `Next.js` frontend queues batched operations ("Generate Next 10") rather than overwhelming the FastAPI queue.
