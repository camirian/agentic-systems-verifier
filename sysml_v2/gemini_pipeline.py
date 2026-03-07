import os
import google.generativeai as genai
from sysml_parser import SysMLv2Parser

class SysMLGeminiPipeline:
    """
    Feeds parsed SysML v2 Architecture models into Google Gemini to automatically 
    verify if the designed system blocks satisfy the declared requirements.
    Proves Applied AI Architect claim AI_NG_03.
    """
    
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Google Gemini API key required for the SysML Pipeline.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def verify_architecture(self, sysml_filepath: str) -> str:
        """
        Parses the SysML v2 file and prompts Gemini to logically verify that the 
        model properties satisfy the linked requirements.
        """
        # 1. Parse MBSE artifact to structured JSON AST
        parser = SysMLv2Parser(sysml_filepath)
        ast_json = parser.to_json()
        
        # 2. Construct the logical verification prompt
        prompt = f"""
        You are an expert Spacecraft Systems Engineer and Applied AI Architect.
        
        I am providing you with a JSON Abstract Syntax Tree (AST) representing a 
        formal SysML v2 architecture model. Your task is to perform an automated 
        design-time verification.
        
        Analyze the "satisfy_links" to see which Requirements are satisfied by which Parts.
        Then, inspect the "attributes" (like coolingCapacity, targetTemp, etc.) of those Parts.
        
        Determine if the engineering parameters defined in the Part logically satisfy 
        the constraints defined in the Requirement text. 
        
        Output a formal Design Verification Report.
        
        SysML v2 JSON AST:
        {ast_json}
        """
        
        try:
            print("Sending SysML v2 AST to Gemini for architectural verification...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Pipeline execution failed: {e}"

if __name__ == "__main__":
    test_file = os.path.join(os.path.dirname(__file__), "sample_architecture.sysml")
    try:
        pipeline = SysMLGeminiPipeline()
        report = pipeline.verify_architecture(test_file)
        
        print("\n\n" + "="*50)
        print("  SYSML v2 GEMINI ARCHITECTURE VERIFICATION REPORT")
        print("="*50)
        print(report)
        print("="*50)
        
    except Exception as e:
        print(f"Skipping pipeline execution: {e}")
