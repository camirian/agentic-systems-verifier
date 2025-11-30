import google.generativeai as genai
import json
import time
from typing import Dict, Any, Generator, List, Optional
from core.db import get_requirements, update_verification_result, log_event

class VerificationEngine:
    def __init__(self, api_key: str):
        """
        Initializes the Verification Engine with the Google Gemini API.

        Args:
            api_key (str): The Google API Key for authentication.
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest',
                                      generation_config={"response_mime_type": "application/json"})

    def _analyze_requirement(self, req: Dict[str, Any]) -> str:
        """
        Helper to analyze a single requirement dict using AI.

        Args:
            req (Dict[str, Any]): The requirement dictionary containing 'ID' and 'Requirement'.

        Returns:
            str: A log message describing the analysis result.
        """
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

    def verify_section(self, section_id: Optional[str] = None) -> Generator[str, None, None]:
        """
        Analyzes all pending requirements in a section (or all if section_id is None).

        Args:
            section_id (Optional[str]): The specific section to verify. If None, verifies all sections.

        Yields:
            str: Log messages for the UI.
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

    def verify_single_requirement(self, req_id: str) -> Generator[str, None, None]:
        """
        Analyzes a specific requirement by ID.

        Args:
            req_id (str): The ID of the requirement to verify.

        Yields:
            str: Log messages for the UI.
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

    def generate_test_code(self, requirement_text: str) -> str:
        """
        Generates Python pytest code for a given requirement.

        Args:
            requirement_text (str): The text of the requirement to generate tests for.

        Returns:
            str: The generated Python code as a string.
        """
        prompt = f"""
        You are a Senior Python Test Engineer for NASA software.
        Write a robust `pytest` unit test for the following requirement.
        
        Requirement: "{requirement_text}"
        
        Constraints:
        1. Use `pytest`.
        2. Mock any external dependencies (telemetry, hardware).
        3. Include comments explaining the verification logic.
        4. Return ONLY the python code block (no markdown text).
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

    def execute_test_code(self, code_str: str) -> Dict[str, str]:
        """
        Executes the generated test code using pytest in a subprocess.

        Args:
            code_str (str): The Python code to execute.

        Returns:
            Dict[str, str]: A dictionary containing 'status' ('Pass'|'Fail'|'Error') and 'log' (str).
        """
        import subprocess
        import os
        import uuid
        
        # Create a temporary test file
        filename = f"tests/temp_test_{uuid.uuid4().hex}.py"
        
        try:
            with open(filename, "w") as f:
                f.write(code_str)
            
            # Run pytest
            # -q: quiet
            # --tb=short: shorter traceback
            result = subprocess.run(
                ["pytest", filename, "-q", "--tb=short"], 
                capture_output=True, 
                text=True,
                timeout=10 # Safety timeout
            )
            
            log_output = result.stdout + "\n" + result.stderr
            
            if result.returncode == 0:
                status = "Pass"
            else:
                status = "Fail"
                
            return {"status": status, "log": log_output}
            
        except subprocess.TimeoutExpired:
            return {"status": "Error", "log": "Execution timed out (10s limit)."}
        except Exception as e:
            return {"status": "Error", "log": f"Execution failed: {str(e)}"}
        finally:
            # Cleanup
            if os.path.exists(filename):
                os.remove(filename)
