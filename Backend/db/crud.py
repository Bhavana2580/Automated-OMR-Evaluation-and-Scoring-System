# backend/db/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional, List, Dict

# -------- Student --------
def get_or_create_student(db: Session, student_identifier: str, name: Optional[str] = None):
    student = db.query(models.Student).filter(models.Student.student_id == student_identifier).first()
    if student:
        return student
    student = models.Student(student_id=student_identifier, name=name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def get_student_by_id(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

# -------- Exam & AnswerKey --------
def create_exam(db: Session, exam: Dict):
    obj = models.Exam(
        exam_code=exam.get("exam_code"),
        title=exam.get("title"),
        version_count=exam.get("version_count", 1)
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_exam_by_code(db: Session, code: str):
    return db.query(models.Exam).filter(models.Exam.exam_code == code).first()

def create_answer_key(db: Session, exam_id: int, version: str, key: Dict):
    ak = models.AnswerKey(exam_id=exam_id, version=version, key=key)
    db.add(ak)
    db.commit()
    db.refresh(ak)
    return ak

def get_answer_key(db: Session, exam_id: int, version: str):
    return db.query(models.AnswerKey).filter(models.AnswerKey.exam_id == exam_id, models.AnswerKey.version == version).first()

# -------- Results --------
def create_result(db: Session, payload: Dict):
    """
    payload keys expected (some optional):
    - student_id (int) or 'student_identifier' (str)
    - uploaded_filename
    - uploaded_path
    - exam_id
    - version
    - total_score
    - section_scores
    - raw_answers
    - overlay_path
    """
    # accept student identifier string to create student
    student_ref = None
    if payload.get("student_identifier"):
        student = get_or_create_student(db, payload["student_identifier"], payload.get("student_name"))
        student_ref = student.id
    elif payload.get("student_id"):
        student_ref = payload.get("student_id")

    res = models.Result(
        student_id=student_ref,
        uploaded_filename=payload.get("uploaded_filename") or payload.get("uploaded_path", "").split("/")[-1],
        uploaded_path=payload.get("uploaded_path"),
        exam_id=payload.get("exam_id"),
        version=payload.get("version"),
        total_score=payload.get("total_score"),
        section_scores=payload.get("section_scores"),
        raw_answers=payload.get("raw_answers"),
        overlay_path=payload.get("overlay_path"),
    )
    db.add(res)
    db.commit()
    db.refresh(res)

    # create audit log
    create_audit_log(db, res.id, action="evaluated", actor=payload.get("actor", "system"), note="Auto-evaluated by OMRProcessor")
    return res

def get_result_by_student(db: Session, student_identifier: str):
    # try to find student then return most recent result
    student = db.query(models.Student).filter(models.Student.student_id == student_identifier).first()
    if not student:
        return None
    return db.query(models.Result).filter(models.Result.student_id == student.id).order_by(models.Result.created_at.desc()).first()

def get_result_by_id(db: Session, result_id: int):
    return db.query(models.Result).filter(models.Result.id == result_id).first()

def list_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Result).order_by(models.Result.created_at.desc()).offset(skip).limit(limit).all()

def mark_result_reviewed(db: Session, result_id: int, reviewer: Optional[str] = None, note: Optional[str] = None):
    res = get_result_by_id(db, result_id)
    if not res:
        return None
    res.reviewed = True
    db.add(res)
    db.commit()
    db.refresh(res)
    create_audit_log(db, result_id, action="marked_reviewed", actor=reviewer, note=note)
    return res

# -------- Audit log --------
def create_audit_log(db: Session, result_id: Optional[int], action: str, actor: Optional[str] = None, note: Optional[str] = None):
    log = models.AuditLog(result_id=result_id, action=action, actor=actor, note=note)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_audit_logs_for_result(db: Session, result_id: int):
    return db.query(models.AuditLog).filter(models.AuditLog.result_id == result_id).order_by(models.AuditLog.timestamp.desc()).all()
