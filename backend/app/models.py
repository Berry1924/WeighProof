import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # tester, reviewer, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    username = Column(String(50), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details_json = Column(Text, nullable=True)


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    manufacturer = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    accuracy_class = Column(String(10), nullable=False)
    max_capacity = Column(String(50), nullable=False)
    min_capacity = Column(String(50), nullable=False)
    verification_scale_interval_e = Column(String(50), nullable=False)
    actual_scale_interval_d = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False)
    data_json = Column(Text, nullable=False)
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TestReport(Base):
    __test__ = False
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="DRAFT", index=True, nullable=False)  # DRAFT, SUBMITTED, SIGNED, REJECTED
    overall_verdict = Column(String(20), default="FAIL", nullable=False)
    ruleset_id = Column(String(50), nullable=False)
    ruleset_edition = Column(String(50), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    instrument_snapshot_json = Column(Text, nullable=False)
    evaluation_results_json = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Audit & Security
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    submitted_by = Column(String(50), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    
    reviewer_username = Column(String(50), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    reviewer_comments = Column(Text, nullable=True)
    
    # Cryptographic integrity
    canonical_hash = Column(String(64), nullable=True, index=True)
    qr_data_uri = Column(Text, nullable=True)
