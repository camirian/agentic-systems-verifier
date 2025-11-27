import sqlite3
import os
import datetime
from typing import List, Dict, Optional

DB_PATH = os.path.join("data", "project.db")

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Added req_name column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requirements (
            id TEXT PRIMARY KEY,
            req_id TEXT,
            req_name TEXT, 
            text TEXT,
            section TEXT,
            source_file TEXT,
            status TEXT,
            priority TEXT,
            source_type TEXT,
            verification_method TEXT,
            rationale TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migration: Add columns if they don't exist (Safe for existing DBs)
    try:
        cursor.execute("ALTER TABLE requirements ADD COLUMN verification_method TEXT")
    except sqlite3.OperationalError:
        pass # Column exists
        
    try:
        cursor.execute("ALTER TABLE requirements ADD COLUMN rationale TEXT")
    except sqlite3.OperationalError:
        pass # Column exists

    try:
        cursor.execute("ALTER TABLE requirements ADD COLUMN generated_code TEXT")
    except sqlite3.OperationalError:
        pass # Column exists

    # Added system_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT,
            message TEXT
        )
    ''')
    
    # Added projects table for metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            filename TEXT PRIMARY KEY,
            title TEXT,
            req_count INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Run Migration
    migrate_projects_metadata()

def migrate_projects_metadata():
    """Backfill projects table from existing requirements."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find projects that are in requirements but NOT in projects table
    cursor.execute('''
        SELECT DISTINCT source_file 
        FROM requirements 
        WHERE source_file IS NOT NULL 
        AND source_file != ""
        AND source_file NOT IN (SELECT filename FROM projects)
    ''')
    
    missing_projects = [row[0] for row in cursor.fetchall()]
    
    for filename in missing_projects:
        # Get count
        cursor.execute('SELECT COUNT(*) FROM requirements WHERE source_file = ?', (filename,))
        count = cursor.fetchone()[0]
        
        # Insert with default title
        cursor.execute('''
            INSERT INTO projects (filename, title, req_count, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (filename, filename, count)) # Use filename as title for legacy data
        
    if missing_projects:
        print(f"Migrated {len(missing_projects)} projects to metadata table.")
        
    conn.commit()
    conn.close()

def upsert_project_metadata(filename: str, title: str, req_count: int):
    """Update project metadata."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO projects (filename, title, req_count, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (filename, title, req_count))
    
    conn.commit()
    conn.close()

def get_all_projects() -> List[Dict]:
    """Retrieve all projects with metadata."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ensure table exists (migration for existing DBs)
    try:
        cursor.execute('SELECT * FROM projects')
    except sqlite3.OperationalError:
        return []

    cursor.execute('SELECT * FROM projects ORDER BY last_updated DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def save_requirements(requirements: List[Dict], source_file: str, section: str, doc_title: str = None):
    """
    Save a list of requirements to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for req in requirements:
        cursor.execute('''
            INSERT OR REPLACE INTO requirements (id, req_id, req_name, text, section, source_file, status, priority, source_type, verification_method, rationale, generated_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            req['ID'], 
            req['ID'],
            req.get('Requirement Name', ''), 
            req['Requirement'], 
            section, 
            source_file, 
            req.get('Status', 'Pending'), 
            req.get('Priority', 'Medium'),
            req.get('Source', 'Original'),
            req.get('Verification Method', ''),
            req.get('Rationale', ''),
            req.get('Generated Code', '')
        ))
        
    conn.commit()
    conn.close()
    
    # Update Project Metadata
    if doc_title:
        # Get total count for this file
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM requirements WHERE source_file = ?', (source_file,))
        count = cursor.fetchone()[0]
        conn.close()
        
        upsert_project_metadata(source_file, doc_title, count)

def get_available_specs() -> List[str]:
    """Retrieve a list of unique specification files (projects)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT source_file FROM requirements WHERE source_file IS NOT NULL AND source_file != ""')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_requirements(section: Optional[str] = None, source_file: Optional[str] = None) -> List[Dict]:
    """
    Retrieve requirements from the database, optionally filtered by section and source file.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM requirements WHERE 1=1'
    params = []
    
    if section and section.strip():
        query += ' AND section = ?'
        params.append(section)
        
    if source_file and source_file.strip() and source_file != "All Projects":
        query += ' AND source_file = ?'
        params.append(source_file)
        
    cursor.execute(query, tuple(params))
        
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "ID": row['id'],
            "Requirement Name": row['req_name'], 
            "Requirement": row['text'],
            "Status": row['status'],
            "Priority": row['priority'],
            "Source": row['source_type'],
            "Verification Method": row['verification_method'] if 'verification_method' in row.keys() else '',
            "Rationale": row['rationale'] if 'rationale' in row.keys() else '',
            "Generated Code": row['generated_code'] if 'generated_code' in row.keys() else ''
        })
        
    return results

def update_requirement(req_id: str, text: str, status: str, priority: str, source_type: str, verification_method: Optional[str] = None):
    """Update a single requirement's fields."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if verification_method is not None:
        cursor.execute('''
            UPDATE requirements 
            SET text = ?, status = ?, priority = ?, source_type = ?, verification_method = ?
            WHERE id = ?
        ''', (text, status, priority, source_type, verification_method, req_id))
    else:
        cursor.execute('''
            UPDATE requirements 
            SET text = ?, status = ?, priority = ?, source_type = ?
            WHERE id = ?
        ''', (text, status, priority, source_type, req_id))
    
    conn.commit()
    conn.close()

def get_requirement_by_id(req_id: str) -> Optional[Dict]:
    """Retrieve a single requirement by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM requirements WHERE id = ?', (req_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "ID": row['id'],
            "Requirement Name": row['req_name'], 
            "Requirement": row['text'],
            "Status": row['status'],
            "Priority": row['priority'],
            "Source": row['source_type'],
            "Verification Method": row['verification_method'] if 'verification_method' in row.keys() else '',
            "Rationale": row['rationale'] if 'rationale' in row.keys() else '',
            "Generated Code": row['generated_code'] if 'generated_code' in row.keys() else ''
        }
    return None

def update_verification_result(req_id: str, status: str, verification_method: str, rationale: str):
    """Update requirement with verification results."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE requirements 
        SET status = ?, verification_method = ?, rationale = ?
        WHERE id = ?
    ''', (status, verification_method, rationale, req_id))
    
    conn.commit()
    conn.close()

def update_generated_code(req_id: str, code: str):
    """Update requirement with generated test code."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE requirements 
        SET generated_code = ?
        WHERE id = ?
    ''', (code, req_id))
    
    conn.commit()
    conn.close()

def clear_database():
    """
    Clear all data from the requirements table and system logs.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM requirements')
    cursor.execute('DELETE FROM projects')
    
    conn.commit()
    conn.close()
    
    # Also delete physical files in data/ directory
    if os.path.exists("data"):
        for filename in os.listdir("data"):
            file_path = os.path.join("data", filename)
            try:
                if os.path.isfile(file_path) and filename.endswith(".pdf"):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

def log_event(message: str, level: str = "INFO"):
    """Log a system event to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    cursor.execute('INSERT INTO system_logs (timestamp, level, message) VALUES (?, ?, ?)', (timestamp, level, message))
    
    conn.commit()
    conn.close()

def get_system_logs(limit: int = 50) -> List[Dict]:
    """Retrieve the latest system logs."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM system_logs ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
