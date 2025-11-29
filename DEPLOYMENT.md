# Deployment Guide: Agentic Systems Verifier

This guide explains how to deploy ASV to **Google Cloud Run**, a serverless platform that scales automatically.

## Prerequisites

1.  **Google Cloud Project:** Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Billing Enabled:** Ensure billing is enabled for your project.
3.  **Google Cloud SDK:** Install the [`gcloud` CLI](https://cloud.google.com/sdk/docs/install).

## Step 1: Configuration

Open `app.py` or check your environment variables. Ensure `GOOGLE_API_KEY` is NOT hardcoded. It should be retrieved via `os.getenv("GOOGLE_API_KEY")` or Streamlit secrets.

## Step 2: Containerize & Deploy

Run the following commands in your terminal (from the project root):

```bash
# 1. Authenticate with Google Cloud
gcloud auth login

# 2. Set your project ID
gcloud config set project [YOUR_PROJECT_ID]

# 3. Build and Deploy to Cloud Run
# Replace [YOUR_PROJECT_ID] with your actual project ID.
gcloud run deploy agentic-verifier \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=[YOUR_GEMINI_API_KEY]
```

## Step 3: Verification

1.  Wait for the deployment to finish. The terminal will output a URL (e.g., `https://agentic-verifier-xyz-uc.a.run.app`).
2.  Open the URL in your browser.
3.  Verify that the app loads and "Mission Control" is accessible.

## Troubleshooting

*   **"Error: Container failed to start"**: Check the logs in the Google Cloud Console (Cloud Run > Logs).
*   **"Quota Exceeded"**: Ensure your project has sufficient quota for Cloud Run and Cloud Build.
*   **"Permission Denied"**: Ensure your user account has the `Cloud Run Admin` and `Service Account User` roles.

## Why Cloud Run?

*   **Scalability:** Scales to 0 when not in use (saves money) and scales up to handle traffic.
*   **Security:** Runs in a secure, isolated container.
*   **Integration:** Easy access to other Google Cloud services (Vertex AI, Cloud SQL).
