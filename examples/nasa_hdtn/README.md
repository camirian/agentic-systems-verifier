# NASA HDTN Bundle Protocol Implementation

**Source Specification:** `TM-20240011318.pdf` (Section 3.2)
**Protocols Implemented:** Bundle Protocol Version 6 (BPv6) and Version 7 (BPv7)

## Overview
This example demonstrates the **Agentic Systems Verifier** applied to NASA's High-Rate Delay Tolerant Networking (HDTN) requirements. It implements the bundle structures defined in the "HDTN Bundle Requirements" section of the specification.

## Configuration
The implementation is driven by `config.json`, which maps the PDF requirements to executable code:
- **BPv6**: Uses `sdnv_cbhe` encoding (Compressed Bundle Header Encoding with SDNVs).
- **BPv7**: Uses `cbor` encoding (Concise Binary Object Representation).

## Structure
- `config.json`: The "DNA" of this implementation. Defines fields, ordering, and encoding rules.
- `buffer_manager.py`: The specific adapter that initializes the generic engine with the NASA configuration.
- `spec.pdf`: The original source of truth (located in `docs/specs/`).

## Verification
This implementation is verified against the extracted "Shall" statements found in `docs/artifacts/Requirements_Trace.md`.

### Running Tests
To verify this specific example, run the tests from the project root:
```bash
python3 -m unittest tests/nasa_hdtn/test_buffer_manager.py
```
