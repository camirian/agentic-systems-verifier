import sqlite3
import os

DB_PATH = os.path.join("data", "project.db")

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- PROJECTS TABLE ---")
    try:
        cursor.execute("SELECT filename, title, req_count FROM projects")
        projects = cursor.fetchall()
        print(f"Total Projects: {len(projects)}")
        for p in projects:
            print(f"- {p[0]} | Title: {p[1]} | Count: {p[2]}")
    except Exception as e:
        print(f"Error querying projects: {e}")

    print("\n--- REQUIREMENTS TABLE (Distinct Source Files) ---")
    try:
        cursor.execute("SELECT DISTINCT source_file FROM requirements")
        req_files = cursor.fetchall()
        print(f"Total Unique Source Files: {len(req_files)}")
        for r in req_files:
            print(f"- {r[0]}")
    except Exception as e:
        print(f"Error querying requirements: {e}")
        
    conn.close()
