import pypdf
import google.generativeai as genai
import json
import os
import time
import concurrent.futures
from core.db import log_event

def process_batch(batch_index, batch_text, model):
    """
    Helper function to process a single batch of text.
    """
    try:
        prompt = f"""
        Analyze the following technical specification text. Extract all 'Shall' statements. 
        
        Return a JSON list where each item has: 
        {{
            'id': 'The Requirement ID (e.g., BPv6-001)', 
            'name': 'The Name or Title of the requirement (e.g., BP Bundle Structure)', 
            'text': 'The full sentence containing the shall statement', 
            'priority': 'Medium'
        }}
        
        RULES:
        1. The 'Name' is the bold text or title preceding the sentence. If not explicitly clear, infer it from the context immediately preceding the ID.
        2. The 'Text' is the full sentence containing 'shall'.
        3. Exclude Tables and Figures.
        4. If no ID is present, generate one like 'REQ-GEN-<UUID>'.
        
        TEXT TO ANALYZE:
        {batch_text}
        """
        
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"Error processing batch {batch_index + 1}: {e}")
        return []

def extract_requirements_from_pdf(file_path, api_key, target_section=None, progress_callback=None):
    """
    Extracts requirements from a PDF file using Gemini AI with Smart Page Filtering.
    
    Args:
        file_path (str): Path to the PDF file.
        api_key (str): Google API Key.
        target_section (str, optional): Specific section to filter by.
        progress_callback (callable, optional): Function to call with progress (0.0 to 1.0) and status text.
        
    Returns:
        list: A list of dictionaries containing requirement details.
    """
    requirements = []
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest',
                                      generation_config={"response_mime_type": "application/json"})
        
        reader = pypdf.PdfReader(file_path)
        total_pages = len(reader.pages)
        
        # PHASE 1: Local Scan & Filtering
        pages_to_process = [] # List of (page_index, page_text)
        
        if progress_callback:
            msg = f"Scanning {total_pages} pages locally"
            if target_section:
                msg += f" for Section '{target_section}'..."
            else:
                msg += " (Quick Mode)..."
            progress_callback(0.1, msg)
            
        if not target_section:
            # Smart Auto-Discovery: Scan ALL pages for "shall"
            if progress_callback:
                progress_callback(0.1, f"Auto-scanning {total_pages} pages for 'shall' statements...")
                
            log_event("Full scan enabled. Filtering for pages with 'shall'.")
            for i in range(total_pages):
                text = reader.pages[i].extract_text()
                # Simple heuristic: Only process pages that mention "shall"
                if "shall" in text.lower():
                    pages_to_process.append((i, text))
            
            if not pages_to_process:
                log_event("No 'shall' statements found in the entire document.", level="WARN")
                if progress_callback:
                    progress_callback(1.0, "No 'shall' statements found in document.")
                return []
        else:
            # Smart Scan: Find pages with target_section
            matching_indices = set()
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if target_section in text:
                    matching_indices.add(i)
            
            if not matching_indices:
                log_event(f"No pages found containing section {target_section}", level="WARN")
                if progress_callback:
                    progress_callback(1.0, f"No pages found for Section {target_section}.")
                return []
                
            # Add buffer (1 page before and after)
            final_indices = set()
            for idx in matching_indices:
                final_indices.add(idx)
                if idx > 0: final_indices.add(idx - 1)
                if idx < total_pages - 1: final_indices.add(idx + 1)
                
            sorted_indices = sorted(list(final_indices))
            
            for idx in sorted_indices:
                text = reader.pages[idx].extract_text()
                if text.strip():
                    pages_to_process.append((idx, text))
        
        # PHASE 2: AI Extraction
        num_filtered_pages = len(pages_to_process)
        if progress_callback:
            progress_callback(0.2, f"Sending {num_filtered_pages} relevant pages to AI...")
            
        # Batching Configuration
        BATCH_SIZE = 10 
        MAX_WORKERS = 5 
        
        # Prepare Batches from filtered pages
        batches = []
        # We need to group the filtered pages into batches. 
        # Since pages_to_process is a list of tuples, we can chunk it.
        
        for i in range(0, num_filtered_pages, BATCH_SIZE):
            batch_subset = pages_to_process[i : min(i + BATCH_SIZE, num_filtered_pages)]
            batch_text = ""
            for idx, text in batch_subset:
                batch_text += text + "\n"
            
            if batch_text.strip():
                batches.append((i, batch_text))
        
        total_batches = len(batches)
        completed_batches = 0
        
        if total_batches == 0:
             if progress_callback:
                progress_callback(1.0, "No valid text content found in selected pages.")
             return []

        # Parallel Execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_batch = {
                executor.submit(process_batch, b[0]//BATCH_SIZE, b[1], model): b[0] 
                for b in batches
            }
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_reqs = future.result()
                
                # Normalize and add to list
                for req in batch_reqs:
                    requirements.append({
                        "ID": req.get('id', 'N/A'),
                        "Requirement Name": req.get('name', 'N/A'),
                        "Requirement": req.get('text', ''),
                        "Status": "Pending",
                        "Priority": req.get('priority', 'Medium'),
                        "Source": "Original"
                    })
                
                completed_batches += 1
                if progress_callback:
                    # Progress from 0.2 to 1.0
                    current_progress = 0.2 + (0.8 * (completed_batches / total_batches))
                    progress_callback(current_progress, f"Processed Batch {completed_batches}/{total_batches}...")

        if progress_callback:
            progress_callback(1.0, "Ingestion Complete.")

    except Exception as e:
        log_event(f"Error initializing AI extraction: {e}", level="ERROR")
        return []

    return requirements
