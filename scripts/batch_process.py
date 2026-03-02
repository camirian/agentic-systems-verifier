import os
import sys
import argparse
import requests
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"

def get_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = input("Please enter your Google API Key: ")
    return api_key

def ingest_pdf(file_path: str, api_key: str):
    filename = os.path.basename(file_path)
    print(f"\n[+] Processing: {filename}")
    
    url = f"{API_URL}/ingest"
    files = {'file': (filename, open(file_path, 'rb'), 'application/pdf')}
    data = {'api_key': api_key}
    
    try:
        response = requests.post(url, files=files, data=data, timeout=300) # 5 min timeout for big PDFs
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] {result['message']}")
            return True
        else:
            print(f"[FAIL] {filename} returned error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"[ERROR] API Request timed out for {filename} after 5 minutes.")
        return False
    except Exception as e:
        print(f"[ERROR] Exception occurred for {filename}: {e}")
        return False

def process_directory(directory: str, api_key: str):
    path = Path(directory)
    if not path.is_dir():
        print(f"[ERROR] Directory '{directory}' does not exist.")
        sys.exit(1)
        
    pdf_files = list(path.glob("*.pdf"))
    total_files = len(pdf_files)
    
    if total_files == 0:
        print(f"No PDF files found in {directory}.")
        return

    print(f"Found {total_files} PDF files in '{directory}'. Starting batch execution...")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for i, file_path in enumerate(pdf_files):
        print(f"\n--- File {i+1} of {total_files} ---")
        success = ingest_pdf(str(file_path), api_key)
        if success:
            success_count += 1
        else:
            fail_count += 1
            
        print("Sleeping for 10 seconds to respect Gemini API rate limits...")
        time.sleep(10)
        
    print("\n" + "=" * 50)
    print("BATCH PROCESSING COMPLETE")
    print(f"Total Processed: {total_files}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")

def check_server():
    try:
        response = requests.get(f"{API_URL}/projects")
        if response.status_code == 200:
             print("✅ Connected to FastAPI Backend on localhost:8000")
             return True
    except:
        pass
    
    print("❌ Cannot connect to FastAPI server. Please ensure it is running on port 8000.")
    print("Run: uvicorn api.main:app --host 0.0.0.0 --port 8000")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASV Headless Batch Processor for PDFs")
    parser.add_argument("--dir", type=str, required=True, help="Directory containing PDF files")
    
    args = parser.parse_args()
    
    check_server()
    api_key = get_api_key()
    
    process_directory(args.dir, api_key)
