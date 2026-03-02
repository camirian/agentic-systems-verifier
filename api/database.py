from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

DB_DIR = "data"
os.makedirs(DB_DIR, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_DIR}/project.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models
class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(String, primary_key=True, index=True)
    req_id = Column(String, index=True)
    req_name = Column(String)
    text = Column(String)
    section = Column(String)
    source_file = Column(String, index=True)
    status = Column(String, default="Pending")
    priority = Column(String, default="Medium")
    source_type = Column(String, default="Original")
    verification_method = Column(String, default="")
    rationale = Column(String, default="")
    generated_code = Column(String, default="")
    verification_status = Column(String, default="")
    execution_log = Column(String, default="")
    last_run_timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"

    filename = Column(String, primary_key=True, index=True)
    title = Column(String)
    req_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    level = Column(String, default="INFO")
    message = Column(String)

# Initialize database
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
