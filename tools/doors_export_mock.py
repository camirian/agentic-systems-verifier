import json
from datetime import datetime
from typing import List, Dict

class DOORSRPEExporterMock:
    """
    Simulates an IBM DOORS Next Generation (DNG) extraction workflow using 
    Rational Publishing Engine (RPE).
    
    Proves Technical Project Management & Base-lining claims (CPS_PER_01) 
    by demonstrating programmatic extraction of a System Requirement Specification 
    (SRS) block into a standardized JSON format digestible by an AI platform.
    """
    def __init__(self, baseline_id: str, module_path: str):
        self.baseline_id = baseline_id
        self.module_path = module_path
        print(f"Initializing RPE connection to DOORS DNG for Module: {module_path}")
        print(f"Targeting active baseline: {baseline_id}")

    def simulate_rpe_extraction(self) -> List[Dict]:
        """Simulates querying the DOORS OSLC API for formal requirements."""
        
        # Simulated raw OSLC JSON response from IBM DOORS
        raw_doors_data = [
            {
                "Identifier": "SYS-REQ-101",
                "Primary Text": "The Flight Control Computer shall poll the IMU via RS-422 at 200Hz.",
                "Type": "Functional",
                "Priority": "Critical",
                "Verification Method": "Test",
                "Link_Satisfies": ["UR-50"],
                "Status": "Approved"
            },
            {
                "Identifier": "SYS-REQ-102",
                "Primary Text": "The total mass of the avionics chassis shall not exceed 5.5 kg.",
                "Type": "Constraint",
                "Priority": "High",
                "Verification Method": "Analysis",
                "Link_Satisfies": ["UR-12"],
                "Status": "Draft"
            },
            {
                "Identifier": "SYS-REQ-103",
                "Primary Text": "The radome surface must be inspected for micro-fractures prior to flight.",
                "Type": "Maintenance",
                "Priority": "Medium",
                "Verification Method": "Inspection",
                "Link_Satisfies": ["UR-88"],
                "Status": "Approved"
            }
        ]
        
        return raw_doors_data

    def transform_to_verifier_schema(self, doors_data: List[Dict]) -> str:
        """
        Transforms raw DOORS exports into the Agentic Systems Verifier JSON schema.
        """
        transformed = []
        
        for item in doors_data:
            # Skip unapproved technical baseline drafts
            if item.get("Status") != "Approved":
                continue
                
            req_obj = {
                "id": item["Identifier"],
                "req_name": f"{item['Type']} Requirement: {item['Identifier']}",
                "text": item["Primary Text"],
                "priority": item["Priority"],
                "source_type": "DOORS_OSLC_EXPORT",
                "verification_method": item["Verification Method"],
                "metadata": {
                    "baseline": self.baseline_id,
                    "extracted_at": datetime.utcnow().isoformat(),
                    "traceability_links": item.get("Link_Satisfies", [])
                }
            }
            transformed.append(req_obj)
            
        return json.dumps(transformed, indent=2)

if __name__ == "__main__":
    exporter = DOORSRPEExporterMock(
        baseline_id="BL-v2.1.0-RC",
        module_path="/Projects/Spacecraft_Avionics/System_Requirements"
    )
    
    print("\n[1] Initiating DOORS OSLC query...")
    raw_data = exporter.simulate_rpe_extraction()
    print(f"    Extracted {len(raw_data)} raw artifacts.")
    
    print("\n[2] Filtering and conforming to Agentic Systems Verifier schema...")
    json_payload = exporter.transform_to_verifier_schema(raw_data)
    
    print("\n[3] Standardized JSON Payload ready for verifier ingestion:\n")
    print(json_payload)
    
    # In a real environment, this payload would be POSTed to the FastAPI /upload endpoint.
