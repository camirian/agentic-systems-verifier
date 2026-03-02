from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil

from api.database import get_db, DB_DIR
import api.database as models
from api import schemas
from core.ingestion import extract_requirements_from_pdf
from core.verification_engine import VerificationEngine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ASV Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Documentation directory - configurable for Docker vs local
DOCS_DIR = os.environ.get("DOCS_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "ASV Core API", "version": "2.0"}

@app.get("/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.last_updated.desc()).all()

@app.delete("/projects/{filename}")
def delete_project(filename: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.filename == filename).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Delete associated requirements
    db.query(models.Requirement).filter(models.Requirement.source_file == filename).delete()
    
    # Delete the project
    db.delete(project)
    db.commit()
    
    return {"status": "success", "message": f"Deleted project {filename}"}

@app.get("/requirements", response_model=List[schemas.RequirementResponse])
def get_requirements(source_file: Optional[str] = None, section: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Requirement)
    if source_file and source_file != "All Projects":
        query = query.filter(models.Requirement.source_file == source_file)
    if section:
        query = query.filter(models.Requirement.section == section)
    return query.all()

@app.put("/requirements/{req_id}", response_model=schemas.RequirementResponse)
def update_requirement(req_id: str, req_update: schemas.RequirementUpdate, db: Session = Depends(get_db)):
    req = db.query(models.Requirement).filter(models.Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    update_data = req_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(req, key, value)
    
    db.commit()
    db.refresh(req)
    return req

@app.post("/ingest")
async def ingest_pdf(
    file: UploadFile = File(...), 
    api_key: str = Form(...),
    target_section: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    safe_filename = file.filename
    save_path = os.path.join(DB_DIR, safe_filename)
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    extracted_data, doc_title = extract_requirements_from_pdf(
        save_path, 
        api_key, 
        target_section=target_section
    )
    
    if not extracted_data:
        raise HTTPException(status_code=400, detail="No requirements found in the PDF.")
        
    # Save to db
    for data in extracted_data:
        req = models.Requirement(
            id=data['ID'],
            req_id=data['ID'],
            req_name=data.get('Requirement Name', ''),
            text=data['Requirement'],
            section=target_section,
            source_file=safe_filename,
            status=data.get('Status', 'Pending'),
            priority=data.get('Priority', 'Medium'),
            source_type=data.get('Source', 'Original')
        )
        db.merge(req)
        
    # Update project metadata
    count = db.query(models.Requirement).filter(models.Requirement.source_file == safe_filename).count()
    proj = db.query(models.Project).filter(models.Project.filename == safe_filename).first()
    if proj:
        proj.title = doc_title
        proj.req_count = count
    else:
        new_proj = models.Project(filename=safe_filename, title=doc_title, req_count=count)
        db.add(new_proj)
        
    db.commit()
    
    return {"message": f"Successfully ingested {len(extracted_data)} requirements from '{doc_title}'!"}

@app.post("/analyze/{req_id}")
def analyze_requirement(req_id: str, api_key: str = Form(...), db: Session = Depends(get_db)):
    req = db.query(models.Requirement).filter(models.Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
        
    engine = VerificationEngine(api_key)
    # Convert SQLAlchemy model to dict for engine
    req_dict = {"ID": req.id, "Requirement": req.text}
    log_msg = engine._analyze_requirement(req_dict)
    
    # Engine uses old distinct DB module. For now, since engine triggers `update_verification_result`, 
    # we should ideally refactor it to work with SQLAlchemy. But for the sake of decoupling, 
    # we can just fetch the updated req from the old sqlite DB or better, update engines 
    # to use the new api.database. Let's just do a sync refresh here.
    # Actually, we should refactor `VerificationEngine` not to use old `core.db` 
    # but the new SQLAlchemy `db` session. Let's do that next.
    return {"message": log_msg}

@app.post("/generate/{req_id}")
def generate_code(req_id: str, api_key: str = Form(...), db: Session = Depends(get_db)):
    req = db.query(models.Requirement).filter(models.Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
        
    engine = VerificationEngine(api_key)
    code = engine.generate_test_code(req.text)
    
    req.generated_code = code
    db.commit()
    
    return {"code": code}

@app.post("/execute/{req_id}")
def execute_test(req_id: str, req_params: schemas.ExecuteRequest, db: Session = Depends(get_db)):
    req = db.query(models.Requirement).filter(models.Requirement.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
        
    # We don't necessarily need api_key to execute locally generated tests
    engine = VerificationEngine("DUMMY_KEY_NOT_USED_FOR_EXEC")
    result = engine.execute_test_code(req_params.code)
    
    req.verification_status = result['status']
    req.execution_log = result['log']
    from datetime import datetime
    req.last_run_timestamp = datetime.utcnow()
    db.commit()
    
    return result

@app.get("/logs", response_model=List[schemas.SystemLogResponse])
def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.SystemLog).order_by(models.SystemLog.timestamp.desc()).limit(limit).all()

@app.get("/api/docs", response_model=List[dict])
def list_docs():
    if not os.path.exists(DOCS_DIR):
        return []
    md_files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.md')]
    
    # Format for the frontend
    docs_list = []
    for f in md_files:
        docs_list.append({
            "id": f,
            "title": f
        })
    return docs_list

@app.get("/api/docs/{filename}")
def get_doc_content(filename: str):
    if not filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only markdown files allowed")
        
    file_path = os.path.join(DOCS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    return {"content": content}
