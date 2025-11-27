import google.generativeai as genai
import json
import time
from core.db import get_requirements, update_verification_result, log_event

class VerificationEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest',
                                      generation_config={"response_mime_type": "application/json"})

    def _analyze_requirement(self, req):
        """Helper to analyze a single requirement dict."""
        req_id = req['ID']
        text = req['Requirement']
        
        # 1. Define Schema for Structured Output
        verification_schema = {
            "type": "OBJECT",
            "properties": {
                "method": {"type": "STRING", "enum": ["Test", "Analysis", "Inspection", "Demonstration"]},
                "rationale": {"type": "STRING"},
                "confidence": {"type": "STRING"}
            },
            "required": ["method", "rationale"]
        }
        
        # 2. Retry Logic (3 Attempts)
        for attempt in range(3):
            try:
                prompt = f"""
                You are a Lead Systems Engineer. Analyze this NASA software requirement: '{text}'.
                Determine the standard Verification Method (VM) required to close it.
                
                Return JSON adhering to the schema.
                """
                
                # Update generation config for this call to enforce schema
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=verification_schema
                    )
                )
                
                result = json.loads(response.text)
                
                method = result.get("method", "Analysis")
                rationale = result.get("rationale", "No rationale provided.")
                
                # Success! Update DB
                db_status = "Analyzed"
                update_verification_result(req_id, db_status, method, rationale)
                
                return f"Plan Generated for {req_id}: {method} ({db_status})"
                
            except Exception as e:
                log_event(f"Attempt {attempt+1}/3 failed for {req_id}: {str(e)}", level="WARN")
                time.sleep(1) # Wait before retry
                continue
        
        # 3. Fallback (If all retries fail)
        error_msg = f"Failed to analyze {req_id} after 3 attempts."
        log_event(error_msg, level="ERROR")
        
        # Mark as Error in DB so user sees it
        update_verification_result(req_id, "Error", "Manual Review", "AI Processing Failed")
        
        return error_msg

    def verify_section(self, section_id=None):
        """
        Analyzes all pending requirements in a section (or all if section_id is None).
        Yields log messages for the UI.
        """
        requirements = get_requirements(section_id)
        pending_reqs = [r for r in requirements if r['Status'] == 'Pending']
        
        scope_name = f"Section {section_id}" if section_id else "ALL sections"
        
        if not pending_reqs:
            log_event(f"No pending requirements found for {scope_name}.", level="WARN")
            yield f"No pending requirements found for {scope_name}."
            return

        total = len(pending_reqs)
        log_event(f"Starting verification for {total} requirements in {scope_name}...")
        yield f"Starting verification for {total} requirements..."

        for i, req in enumerate(pending_reqs):
            # Rate limiting
            time.sleep(1) 
            log_msg = self._analyze_requirement(req)
            log_event(log_msg)
            yield log_msg
                
        log_event(f"Verification complete for {scope_name}.")
        yield "Verification complete."

    def verify_single_requirement(self, req_id):
        """
        Analyzes a specific requirement by ID.
        Yields log messages.
        """
        from core.db import get_requirement_by_id
        req = get_requirement_by_id(req_id)
        
        if not req:
            yield f"Error: Requirement {req_id} not found."
            return
            
        log_event(f"Starting verification for single requirement {req_id}...")
        yield f"Verifying {req_id}..."
        
        log_msg = self._analyze_requirement(req)
        log_event(log_msg)
        yield log_msg
        yield "Verification complete."

    def generate_test_code(self, requirement_text):
        """
        Generates Python pytest code for a given requirement.
        """
        prompt = f"""
        You are a Python Test Engineer. Write a `pytest` unit test to verify this requirement: '{requirement_text}'.
        
        Return ONLY the python code block. Do not include markdown formatting (like ```python).
        Just return the raw code string.
        """
        
        try:
            # Use a simpler generation config for code (text output)
            response = self.model.generate_content(prompt)
            
            # Clean up potential markdown if the model ignores instructions
            code = response.text.replace("```python", "").replace("```", "").strip()
            
            return code
        except Exception as e:
            log_event(f"Code generation failed: {str(e)}", level="ERROR")
            return f"# Error generating code: {str(e)}"
