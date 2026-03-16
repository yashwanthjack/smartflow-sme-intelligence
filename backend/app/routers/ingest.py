from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
import tempfile
from app.db.session import get_db
from app.auth import get_current_active_user
from app.models.user import User
from app.services.ingestion_service import IngestionService

# 1. Create the Router
router = APIRouter()

# 2. Dependency: Get the Service
def get_ingestion_service(db: Session = Depends(get_db)):
    return IngestionService(db)

# 3. Helper to save uploaded file temporarily
def save_upload_file_tmp(upload_file: UploadFile) -> str:
    try:
        # Create a temp file with the same extension
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = tmp.name
        return tmp_path
    finally:
        upload_file.file.close()

# 4. Endpoints

@router.post("/bank")
def ingest_bank_statement(
    entity_id: str = Form(...),
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(get_current_active_user)
):
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this entity.")
        
    tmp_path = save_upload_file_tmp(file)
    try:
        count = service.ingest_bank_statement(tmp_path, entity_id)
        return {"status": "success", "transactions_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Step 5: Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/ledger")
def ingest_ledger(
    entity_id: str = Form(...),
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(get_current_active_user)
):
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this entity.")
        
    tmp_path = save_upload_file_tmp(file)
    try:
        count = service.ingest_ledger(tmp_path, entity_id)
        return {"status": "success", "entries_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/gst")
def ingest_gst(
    entity_id: str = Form(...),
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service),
    current_user: User = Depends(get_current_active_user)
):
    if str(current_user.entity_id) != str(entity_id):
        raise HTTPException(status_code=403, detail="Not authorized to access this entity.")
        
    tmp_path = save_upload_file_tmp(file)
    try:
        count = service.ingest_gst(tmp_path, entity_id)
        return {"status": "success", "summary_created": count > 0}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
