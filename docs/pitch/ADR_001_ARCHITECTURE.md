# Architecture Decision Record (ADR) 001: Configuration-Driven Generic Engine

## Status
Accepted

## Context
Initial prototypes of ASV relied on hardcoded scripts for the NASA HDTN specification. To scale to other industries (Automotive, Medical), we needed an architecture that decoupled the "Verification Logic" from the "Domain Knowledge."

## Decision
We migrated from a script-based approach to a **Configuration-Driven Generic Engine**.
1.  **Logic:** The core Python engine (`core/engine.py`) contains NO domain-specific code.
2.  **Knowledge:** All protocol specifics (Field lengths, Encodings, Headers) are extracted into JSON Configuration files (`config/nasa_hdtn.json`).
3.  **Extraction:** We utilize **Gemini 1.5 Pro** for "Zero-Shot" extraction of these configurations from raw PDFs.

## Consequences
* **Positive:** We can now support a new specification (e.g., ESA ECSS) in hours rather than weeks, simply by ingesting a new PDF and generating a config file.
* **Positive:** The "Verification Engine" is now a reusable platform asset.
* **Negative:** Increased complexity in the `BaseBundle` serialization logic to handle generic types.

## Tech Stack Justification
* **Streamlit:** Chosen for rapid "Mission Control" UI development, allowing Systems Engineers to interact with data natively.
* **SQLite:** Chosen for local persistence to enable "Disconnected Operations" secure environments (common in Defense).
* **Google Gemini:** Chosen over GPT-4 for its superior Context Window (2M tokens), essential for ingesting entire subsystem specifications without fragmentation.
