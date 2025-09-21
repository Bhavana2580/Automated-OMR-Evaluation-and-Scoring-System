# backend/db/models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from .database import Base

class Student(Base):
    __tablename__ = "students"  # Fixed: double underscores
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sheets = relationship("Result", back_populates="student")

class Exam(Base):
    __tablename__ = "exams"  # Fixed: double underscores
    id = Column(Integer, primary_key=True, index=True)
    exam_code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    version_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    answer_keys = relationship("AnswerKey", back_populates="exam")

class AnswerKey(Base):
    __tablename__ = "answer_keys"  # Fixed: double underscores
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    version = Column(String, nullable=False)
    key = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    exam = relationship("Exam", back_populates="answer_keys")

class Result(Base):
    __tablename__ = "results"  # Fixed: double underscores
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    uploaded_filename = Column(String, nullable=False)
    uploaded_path = Column(String, nullable=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    version = Column(String, nullable=True)
    total_score = Column(Integer, nullable=True)
    section_scores = Column(JSON, nullable=True)
    raw_answers = Column(JSON, nullable=True)
    overlay_path = Column(String, nullable=True)
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    student = relationship("Student", back_populates="sheets")
    exam = relationship("Exam")

class AuditLog(Base):
    __tablename__ = "audit_logs"  # Fixed: double underscores
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("results.id", ondelete="CASCADE"), nullable=True)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())