# Quickstart: Deploying the Agentic Verifier Template

Welcome! By clicking **"Use this template"**, you have successfully cloned the boilerplate for a Systems Engineering multi-agent test verifier.

This guide will help you instantiate your local environment and run your first Agentic test within 5 minutes.

## 1. Environment Setup

### Prerequisites
You will need an active API key for Google Gemini (used by the reasoning agents).

### Installation
Clone your newly generated repository to your local machine:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

Create a virtual environment and install the required dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configuration

Create a `.env` file in the root of your project to hold your API keys:
```bash
touch .env
```

Add your Gemini API key to the `.env` file:
```env
GEMINI_API_KEY="your_api_key_here"
```

## 3. Execution

You can now run the core Verification Agent architecture. The default test will parse a sample PDF specification and attempt to generate and verify executable Python code against it.

Run the test suite:
```bash
pytest src/tests/
```

If successful, you will see the Agentic Verification process autonomously decompose the requirements, generate code, execute the tests in an isolated context, and report the validation results.

## Next Steps
Now that the core architecture is running, you can customize the:
1.  **Ingestion Agent:** To read from specific ALM tools (Jama, DOORS) instead of PDFs.
2.  **Code Gen Agent:** To output languages other than Python (e.g., C++ for embedded systems).
3.  **Test Harness:** To deploy the generated code to hardware-in-the-loop (HIL) testbeds.
