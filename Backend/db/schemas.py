# backend/db/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class StudentCreate(BaseModel):
    student_id: str
    name: Optional[str] = None

class Student(BaseModel):
    id: int
    student_id: str
    name: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ExamCreate(BaseModel):
    exam_code: str
    title: Optional[str] = None
    version_count: Optional[int] = 1

class Exam(BaseModel):
    id: int
    exam_code: str
    title: Optional[str]
    version_count: int
    created_at: datetime

    class Config:
        orm_mode = True

class AnswerKeyCreate(BaseModel):
    exam_id: int
    version: str
    key: Dict[str, Any]  # question -> option(s)

class AnswerKey(BaseModel):
    id: int
    exam_id: int
    version: str
    key: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True

class ResultCreate(BaseModel):
    student_id: Optional[int] = None
    uploaded_filename: str
    uploaded_path: Optional[str] = None
    exam_id: Optional[int] = None
    version: Optional[str] = None
    total_score: Optional[int] = None
    section_scores: Optional[Dict[str,int]] = None
    raw_answers: Optional[Dict[str,str]] = None
    overlay_path: Optional[str] = None

class Result(BaseModel):
    id: int
    student_id: Optional[int]
    uploaded_filename: str
    uploaded_path: Optional[str]
    exam_id: Optional[int]
    version: Optional[str]
    total_score: Optional[int]
    section_scores: Optional[Dict[str,int]]
    raw_answers: Optional[Dict[str,str]]
    overlay_path: Optional[str]
    reviewed: bool
    created_at: datetime

    class Config:
        orm_mode = True

class AuditLogCreate(BaseModel):
    result_id: Optional[int]
    action: str
    actor: Optional[str] = None
    note: Optional[str] = None

class AuditLog(BaseModel):
    id: int
    result_id: Optional[int]
    action: str
    actor: Optional[str]
    note: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True