# Agentic Systems Verifier: Platform Walkthrough

## Overview
This document summarizes the transformation of the HDTN prototype into the **Agentic Systems Verifier (ASV)** platform. The system is now a configuration-driven orchestrator capable of verifying various specifications (NASA, ESA, etc.) through a generic engine.

## 1. Platform Architecture
The project is structured to separate the core engine from specific implementations:
- **`core/engine/`**: Contains the generic logic.
    - `base_bundle.py`: A generic `BaseBundle` class that serializes data based on a configuration dictionary.
    - `cbor_utils.py`: Generic CBOR encoding utilities.
- **`config/`**: Persona definitions (Architect, QA).
- **`examples/nasa_hdtn/`**: A specific implementation for NASA HDTN.
    - `config.json`: Defines the BPv6 and BPv7 protocols (fields, encoding types).
    - `buffer_manager.py`: A thin wrapper that loads `config.json` and instantiates `BaseBundle`.

## 2. Configuration-Driven Design
The core engine is agnostic to the specific protocol. It relies on `config.json` to determine:
- **Encoding Strategy**: `sdnv_cbhe` (BPv6) or `cbor` (BPv7).
- **Field Structure**: Ordered list of fields for the primary block.
- **Defaults**: Version numbers, lifetimes, time offsets.

### Example Config (NASA HDTN)
```json
"bpv7": {
    "version": 7,
    "encoding": "cbor",
    "primary_block": {
        "fields": ["version", "proc_flags", "crc_type", "dest_eid", ...]
    }
}
```

## 3. Implementation Status
- **Refactoring**: `buffer_manager.py` was refactored to remove hardcoded logic and use `BaseBundle`.
- **Migration**: All code and artifacts were migrated to `~/dev/personal/agentic-systems-verifier`.
- **Verification**: Unit tests in `tests/` were updated and verified to pass against the new architecture.

## 4. Verification Results
```
Ran 3 tests in 0.000s

OK
```
The tests confirm that the generic engine correctly serializes BPv6 and BPv7 bundles as per the NASA specification, driven entirely by the configuration file.
