import os
from typing import Dict, Any, List
import google.generativeai as genai

class RAGEvaluator:
    """
    Evaluates Retrieval-Augmented Generation (RAG) outputs using quantitative metrics.
    Proves Applied AI Architect claim AI_NG_02 (Precision, Recall, Faithfulness).
    """

    def __init__(self, api_key: str = None):
        """Initializes the RAG Evaluator with Gemini for LLM-as-a-judge capabilities."""
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            
        if not api_key:
            raise ValueError("Google Gemini API key required for RAG evaluation.")
            
        genai.configure(api_key=api_key)
        # Using flash for fast, cost-effective evaluation
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def evaluate_faithfulness(self, requirement: str, generated_response: str) -> float:
        """
        Measures if the generated response relies solely on the provided context.
        Returns a score between 0.0 and 1.0.
        """
        prompt = f"""
        You are an expert systems engineering quality evaluator.
        
        Given the following original requirement (Context) and an AI-generated verification strategy (Response), 
        evaluate the FAITHFULNESS of the Response.
        
        Faithfulness means the Response is strictly derived from the Context and does not hallucinate 
        or invent new constraints that are not present in the original requirement.
        
        Context (Requirement):
        "{requirement}"
        
        Generated Response:
        "{generated_response}"
        
        Return ONLY a floating point number between 0.0 (completely unfaithful/hallucinated) 
        and 1.0 (perfectly faithful to the context). No other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Basic cleanup in case Gemini returns "0.95" or "Score: 0.95"
            score_text = response.text.strip().replace("Score:", "").strip()
            return float(score_text)
        except Exception as e:
            print(f"Faithfulness evaluation failed: {e}")
            return 0.0

    def evaluate_recall(self, requirement: str, generated_response: str) -> float:
        """
        Measures how much of the original requirement's intent is captured in the response.
        Returns a score between 0.0 and 1.0.
        """
        prompt = f"""
        You are an expert systems engineering quality evaluator.
        
        Given the following original requirement (Context) and an AI-generated verification strategy (Response), 
        evaluate the RECALL of the Response.
        
        Recall measures whether all critical components, conditions, and constraints from the original 
        Context are addressed and verified by the Response.
        
        Context (Requirement):
        "{requirement}"
        
        Generated Response:
        "{generated_response}"
        
        Return ONLY a floating point number between 0.0 (misses most aspects) 
        and 1.0 (perfectly addresses all elements of the context). No other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            score_text = response.text.strip().replace("Score:", "").strip()
            return float(score_text)
        except Exception as e:
            print(f"Recall evaluation failed: {e}")
            return 0.0

    def evaluate_precision(self, requirement: str, generated_response: str) -> float:
        """
        Measures how much of the generated response is relevant to the system requirement.
        Returns a score between 0.0 and 1.0.
        """
        prompt = f"""
        You are an expert systems engineering quality evaluator.
        
        Given the following original requirement (Context) and an AI-generated verification strategy (Response), 
        evaluate the PRECISION of the Response.
        
        Precision measures how concise and directly relevant the Response is to the Context. 
        A highly precise response contains no extraneous information, generic filler, or irrelevant test steps.
        
        Context (Requirement):
        "{requirement}"
        
        Generated Response:
        "{generated_response}"
        
        Return ONLY a floating point number between 0.0 (mostly irrelevant noise) 
        and 1.0 (highly concise and purely relevant content). No other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            score_text = response.text.strip().replace("Score:", "").strip()
            return float(score_text)
        except Exception as e:
            print(f"Precision evaluation failed: {e}")
            return 0.0

    def run_full_evaluation(self, requirement: str, generated_response: str) -> Dict[str, float]:
        """Runs all RAG metrics and returns a cohesive scorecard."""
        
        faithfulness = self.evaluate_faithfulness(requirement, generated_response)
        recall = self.evaluate_recall(requirement, generated_response)
        precision = self.evaluate_precision(requirement, generated_response)
        
        # Harmonic mean of precision and recall
        f1_score = 0.0
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
            
        return {
            "faithfulness": faithfulness,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "overall_quality": (faithfulness + f1_score) / 2
        }

if __name__ == "__main__":
    # Example usage / Test
    sample_req = "The thermal control system shall maintain the battery temperature between 10C and 25C during eclipse operations."
    
    good_response = "Test strategy: 1. Place SUT in thermal vacuum chamber. 2. Simulate eclipse conditions (0 solar flux). 3. Monitor battery telemetry. 4. Verify temperature remains >= 10C and <= 25C for the duration of the 60-minute eclipse."
    
    bad_response = "The battery is important. We should test it in the desert to see if it gets hot. Also replace the solar panels."
    
    print("Testing Evaluator... (requires GEMINI_API_KEY in environment)")
    try:
        evaluator = RAGEvaluator()
        
        print("\n--- GOOD RESPONSE EVALUATION ---")
        good_scores = evaluator.run_full_evaluation(sample_req, good_response)
        for k, v in good_scores.items():
            print(f"{k.capitalize()}: {v:.2f}")
            
        print("\n--- BAD RESPONSE EVALUATION ---")
        bad_scores = evaluator.run_full_evaluation(sample_req, bad_response)
        for k, v in bad_scores.items():
            print(f"{k.capitalize()}: {v:.2f}")
            
    except Exception as e:
        print(f"Skipping test run: {e}")
