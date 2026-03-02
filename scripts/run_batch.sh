#!/bin/bash
# Provide your actual Google API Key here to run headlessly:
export GOOGLE_API_KEY="YOUR_API_KEY_HERE" 

echo "Starting Batch Ingestion Pipeline..."

# 1. Ingest the single AC_20-193.pdf
echo "Ingesting AC_20-193.pdf..."
python3 scripts/batch_process.py --file /home/caaren/dev/personal/agentic-systems-verifier/data/AC_20-193.pdf

# 2. Ingest the entire directory of renamed PDFs
echo "Ingesting directory: renamed-pdfs..."
python3 scripts/batch_process.py --dir /home/caaren/Downloads/renamed-pdfs
