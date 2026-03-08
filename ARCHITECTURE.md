# System Architecture: Agentic Systems Verifier

This document outlines the formal C4 (Context, Container, Component, Code) architecture for the **Agentic Systems Verifier**, a platform designed to automate Systems Engineering workflows (like Requirements Verification) using Large Language Models.

This formalization substantiates Applied AI Architect and Systems Engineering software design claims (EDU_JHU_02).

## 1. System Context Diagram
*The high-level view showing how users and external systems interact with the platform.*

```mermaid
flowchart TD
    classDef person fill:#08427b,color:#fff,stroke:#052e56,stroke-width:2px
    classDef system fill:#1168bd,color:#fff,stroke:#0b4884,stroke-width:2px
    classDef ext_system fill:#999999,color:#fff,stroke:#6b6b6b,stroke-width:2px

    SysEng(["Systems Engineer<br>[Person]"]):::person
    
    AgenticVerifier["Agentic Systems Verifier<br>[System]"]:::system
    GeminiAPI["Google Gemini API<br>[External System]"]:::ext_system
    DOORS["DOORS Next Gen<br>[External System]"]:::ext_system

    SysEng -->|"Uploads requirements,<br>reviews AI verification & code"| AgenticVerifier
    AgenticVerifier -->|"Prompts for Verification Method<br>and Pytest code"| GeminiAPI
    AgenticVerifier -->|"Simulates RPE API<br>data extraction"| DOORS
```

## 2. Container Diagram
*The distinct deployable units that make up the software system.*

```mermaid
flowchart TD
    classDef person fill:#08427b,color:#fff,stroke:#052e56,stroke-width:2px
    classDef container fill:#438dd5,color:#fff,stroke:#3c7fc0,stroke-width:2px
    classDef ext_system fill:#999999,color:#fff,stroke:#6b6b6b,stroke-width:2px
    classDef db fill:#438dd5,color:#fff,stroke:#3c7fc0,stroke-width:2px

    SysEng(["Systems Engineer<br>[Person]"]):::person
    GeminiAPI["Google Gemini API<br>[External System]"]:::ext_system

    subgraph CloudRun ["Google Cloud Run Environment"]
        Frontend["Next.js Web Frontend<br>[React, TypeScript]<br><br>Provides Matrix View and<br>3-step Inspector Panel"]:::container
        Backend["FastAPI Backend<br>[Python 3.10+]<br><br>Handles parsing, AI orchestration,<br>and execution"]:::container
        Database[("SQLite Database<br>[Local File]<br><br>Stores session requirements<br>and execution logs")]:::db
    end

    SysEng --->|"Views UI,<br>clicks 'Execute Test'"| Frontend
    Frontend -->|"RESTful API Calls (JSON)"| Backend
    Backend -->|"Reads/Writes state<br>via SQLAlchemy"| Database
    Backend -->|"Sends context & parameters<br>for completion"| GeminiAPI
    
    style CloudRun fill:none,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5
```

## 3. Component Diagram (Backend API)
*Zooming into the Python FastAPI Backend container to view internal architectural blocks.*

```mermaid
flowchart TD
    classDef component fill:#85bbf0,color:#000,stroke:#5b82a7,stroke-width:2px
    classDef ext_system fill:#999999,color:#fff,stroke:#6b6b6b,stroke-width:2px
    classDef db fill:#438dd5,color:#fff,stroke:#3c7fc0,stroke-width:2px

    GeminiAPI["Google Gemini API<br>[External System]"]:::ext_system
    Database[("SQLite DB<br>[Local File]")]:::db

    subgraph BackendApp ["FastAPI Application"]
        Router["API Router<br>[FastAPI Endpoints]<br><br>Routes HTTP requests"]:::component
        DocParser["Document Parsing Engine<br>[PyMuPDF]<br><br>Extracts requirements"]:::component
        VerificationEngine["Verification Engine<br>[Python class]<br><br>Interacts with Gemini<br>to generate Pytests"]:::component
        ExecutionSandbox["Execution Sandbox<br>[Python subprocess]<br><br>Runs code in isolation"]:::component
        MetricsModule["RAG Evaluation Module<br>[/evaluation]<br><br>Scores logic quality"]:::component
        SysMLPipeline["SysML v2 Parser<br>[/sysml_v2]<br><br>Parses MBSE models"]:::component
    end

    Router -->|"Triggers extraction"| DocParser
    Router -->|"Requests AI completion"| VerificationEngine
    Router -->|"Executes 'Test' scripts"| ExecutionSandbox
    
    VerificationEngine -->|"Sends prompt payload"| GeminiAPI
    VerificationEngine -->|"Logs telemetry/scores"| MetricsModule
    VerificationEngine -->|"Updates DB values"| Database
    
    style BackendApp fill:none,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5
```

## Architectural Design Decisions & Trade-offs
1.  **Monolithic Storage (SQLite):** For MVP velocity and Cloud Run concurrency limitations (Scale to Zero), SQLite provides a simple, self-contained persistence layer without the network overhead of Cloud SQL.
2.  **Stateless Sandboxing (Subprocess):** Generated Pytests are executed via `subprocess.run(["python", "-m", "pytest", temp_file])`. While lacking full Docker isolation, it prevents basic namespace collisions and module bleeding during concurrent execution.
3.  **Client-Side Rate Limiting (10 Items):** Gemini Free-tier limits strictly enforce 15 Requests Per Minute (RPM). The `Next.js` frontend queues batched operations ("Generate Next 10") rather than overwhelming the FastAPI queue.
