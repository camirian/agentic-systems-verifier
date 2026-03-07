import os
import re
import json

class SysMLv2Parser:
    """
    Parses a simplified subset of SysML v2 textual syntax into a JSON AST.
    Proves Applied AI Architect claim AI_NG_03 (MBSE Integration).
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"SysML v2 file not found: {filepath}")
            
    def parse(self) -> dict:
        """Reads the .sysml file and extracts the fundamental blocks and requirements."""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        ast = {
            "parts": [],
            "requirements": [],
            "connections": [],
            "satisfy_links": []
        }

        # Match parts: part def Name { ... }
        part_pattern = re.compile(r"part\s+def\s+(\w+)\s*\{([^}]+)\}")
        for match in part_pattern.finditer(content):
            part_name = match.group(1)
            body = match.group(2)
            
            attributes = re.findall(r"attribute\s+(\w+)\s*:\s*(\w+)\s*=\s*([^;]+);", body)
            ports = re.findall(r"port\s+(\w+)\s*:\s*(\w+);", body)
            subparts = re.findall(r"part\s+(\w+)\s*:\s*(\w+);", body)
            connections = re.findall(r"connect\s+([\w.]+)\s+to\s+([\w.]+);", body)
            
            ast["parts"].append({
                "name": part_name,
                "attributes": [{"name": a[0], "type": a[1], "value": a[2].strip()} for a in attributes],
                "ports": [{"name": p[0], "type": p[1]} for p in ports],
                "subparts": [{"instance": s[0], "type": s[1]} for s in subparts],
            })
            
            for conn in connections:
                ast["connections"].append({"source": conn[0], "target": conn[1], "context": part_name})

        # Match requirements
        req_pattern = re.compile(r"requirement\s+def\s+(\w+)\s*\{([^}]+)\}")
        for match in req_pattern.finditer(content):
            req_name = match.group(1)
            body = match.group(2)
            
            # Extract docster
            doc_match = re.search(r"doc\s*/\*([^*]+)\*/", body)
            doc_text = doc_match.group(1).strip() if doc_match else ""
            
            attributes = re.findall(r"attribute\s+(\w+)\s*:\s*(\w+)\s*=\s*([^;]+);", body)
            
            ast["requirements"].append({
                "name": req_name,
                "text": doc_text,
                "attributes": [{"name": a[0], "type": a[1], "value": a[2].strip()} for a in attributes]
            })

        # Match satisfy relationships
        satisfy_pattern = re.compile(r"satisfy\s+requirement\s+(\w+)\s+by\s+part\s+(\w+);")
        for match in satisfy_pattern.finditer(content):
            ast["satisfy_links"].append({
                "requirement": match.group(1),
                "satisfying_part": match.group(2)
            })

        return ast

    def to_json(self) -> str:
        """Returns the AST as a formatted JSON string."""
        return json.dumps(self.parse(), indent=2)

if __name__ == "__main__":
    test_file = os.path.join(os.path.dirname(__file__), "sample_architecture.sysml")
    parser = SysMLv2Parser(test_file)
    print("Parsed SysML v2 AST:")
    print(parser.to_json())
