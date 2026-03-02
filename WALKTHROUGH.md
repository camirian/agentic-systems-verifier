# ASV User Walkthrough

The Agentic Systems Verifier (ASV) has been upgraded from a synchronous prototype to a production-grade, decoupled web application. This guide covers how to execute the system in a local development environment.

## 1. System Architecture
ASV is now built using a modern **"PERN-like" Stack** (Python/FastAPI Engine, React/Next.js UI):
- **Backend (`/api`)**: A high-performance FastAPI server managing SQLite connections (via SQLAlchemy) and orchestrating Google Gemini agent paths.
- **Frontend (`/web`)**: A premium Next.js 14 React application featuring dark-mode glassmorphism and real-time state management.
- **Offline Batch Processing**: A headless CLI script (`scripts/batch_process.py`) to bypass the UI for large-scale document ingestion.

## 2. Startup Sequence

You must start the Backend and Frontend concurrently in separate terminal sessions.

### Step 2.1: Start the FastAPI Backend
```bash
# From the project root
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the uvicorn server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
*The backend is now live at `http://localhost:8000`. You can view the API documentation at `http://localhost:8000/docs`.*

### Step 2.2: Start the Next.js Frontend
```bash
# In a new terminal
cd web
npm install
npm run dev
```
*The frontend is now live at `http://localhost:3000`.*

---

## 3. The Mission Control Dashboard
Navigate your browser to `http://localhost:3000`.

![ASV Next.js Mission Control](/home/caaren/.gemini/antigravity/brain/88b991a1-0f43-4651-8566-3a26f294cf13/nextjs_app_main_ui_1772338250147.png)

1. **Authentication**: Enter your Google Gemini API Key in the top right input field. It will securely cache in your browser.
2. **Project Selection**: Use the top-left dropdown to swap between your ingested documentation.
3. **Traceability Matrix**: The central table displays ingested requirements, status, and verification priority.
4. **Agent Inspector**: Click on any requirement row to open the Inspector Panel on the right. 
    - View the complete text.
    - View the AI rationale for determining the Verification Method (Analysis, Inspection, Test).
    - If "Test" is determined, click **Generate Pytest Script**.
    - Click **Execute Test** to run the generated code in a secure subprocess and stream the logs back to the UI.

---

## 4. Headless Batch Ingestion (The "Forge" Pipeline)
For bulk operations (like processing 45 PDFs), do not use the UI. Use the dedicated CLI script. Ensure your FastAPI server is running.

```bash
# Target the directory of PDFs
chmod +x scripts/run_batch.sh
./scripts/run_batch.sh
```
*The script includes intelligent rate-limiting specifically designed for the Gemini API.*
