import os
import sys
import json

# Add project root to path so we can import core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.verification_engine import VerificationEngine
from core.db import get_requirements, update_verification_result, update_generated_code, update_execution_result

def test_generation():
    # Use a generic demo key or prompt the user, since we can't extract it easily from Next.js localstorage via terminal
    # But for a backend script we actually need a *real* key to show them the real output.
    # The user has the key and entered it in the UI. When they hit "Brainstorm All", the UI handles it.
    
    # We will just verify what happened in the database
    reqs = get_requirements(source_file="nasa-tm-20240011318-hdt-7150-2d-srs.pdf")
    
    analyzed = 0
    generated = 0
    executed = 0
    
    for r in reqs:
        print(f"[{r['ID']}] Status: {r['Status']} | Code Length: {len(r.get('Generated Code', ''))}")
        if r['Status'] != 'Pending':
            analyzed += 1
        if r.get('Generated Code'):
            generated += 1
        if r.get('Verification Method') == 'Test' and r.get('Generated Code') and 'Pass' in str(r):
             executed += 1

    print(f"\nSummary:")
    print(f"Total Reqs: {len(reqs)}")
    print(f"Analyzed: {analyzed}")
    print(f"Generated Scripts: {generated}")
    print(f"Executed Tests: {executed}")

if __name__ == "__main__":
    test_generation()
