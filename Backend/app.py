# backend/app.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import uuid
import os

from .omr.processor import OMRProcessor
from .db.database import engine, Base
from .db import models

app = FastAPI(title="Automated OMR Evaluation API with Sample Data Support")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# define paths
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# assume sample_data folder is at project_root/sample_data
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
SAMPLE_DATA_DIR = os.path.join(PROJECT_ROOT, "sample_data")
ANSWER_KEYS_PATH = os.path.join(SAMPLE_DATA_DIR, "answer_keys.json")

processor = OMRProcessor(answer_key_path=ANSWER_KEYS_PATH)

@app.post("/evaluate")
async def evaluate_sheet(
    file: UploadFile = File(...),
    version: str = Form(...),
    student_id: str = Form(None),
):
    # save upload
    file_ext = os.path.splitext(file.filename)[1].lower()
    uid = str(uuid.uuid4())
    saved_filename = f"{uid}{file_ext}"
    out_path = os.path.join(UPLOAD_DIR, saved_filename)
    with open(out_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = processor.process(out_path, version=version, student_id=student_id)
    except Exception as e:
        # optionally log the exception
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    # save to database
    db = database.SessionLocal()
    created = crud.create_result(db, {
        "student_id": result.get("student_id") or uid,
        "sheet_path": out_path,
        "version": version,
        "total_score": result["total_score"],
        "section_scores": result["section_scores"],
        "raw_answers": result["answers"],
    })
    db.close()

    # Return also overlay image path so client (UI) can fetch or display; you may want to serve static files
    return JSONResponse(status_code=200, content={
        "student_id": result.get("student_id") or uid,
        "version": version,
        "total_score": result["total_score"],
        "section_scores": result["section_scores"],
        "answers": result["answers"],
        "overlay_path": result["overlay_path"],
    })

@app.get("/result/{student_id}")
def get_result(student_id: str):
    db = database.SessionLocal()
    res = crud.get_result_by_student(db, student_id)
    db.close()
    if not res:
        raise HTTPException(status_code=404, detail="Result not found")
    return res

@app.get("/overlay/{filename}")
def get_overlay_image(filename: str):
    """
    If you want to serve overlay images via API (for frontend to fetch),
    you can map URL -> file in uploads folder.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Overlay not found")
    return FileResponse(file_path, media_type="image/png")

@app.get("/health")
def health():
    return {"status": "ok"}
