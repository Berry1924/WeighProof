import datetime
import json
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import User, AuditLog, Instrument, TestReport
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_roles,
    log_audit_event,
)
from app.engine.types import (
    AccuracyClass,
    DeviceType,
    WeighingDirection,
    Verdict,
    ReportStatus,
    InstrumentMasterData,
    PlausibilityEvaluation,
)
from app.engine.ruleset import ruleset_registry
from app.engine.plausibility import evaluate_instrument_plausibility
from app.engine.mpe import calculate_mpe, MpeCalculationResult
from app.engine.weighing_performance import (
    WeighingPointInput,
    evaluate_weighing_performance,
    WeighingPerformanceEvaluation,
)
from app.engine.eccentricity import (
    EccentricityPositionInput,
    calculate_recommended_eccentricity_load,
    evaluate_eccentricity,
    EccentricityEvaluation,
)
from app.engine.repeatability import (
    RepeatabilityRunInput,
    evaluate_repeatability_series,
    evaluate_repeatability,
    RepeatabilityEvaluation,
)
from app.engine.hasher import (
    compute_report_hash,
    verify_report_integrity,
    generate_verification_qr_code,
)
from app.reports.pdf_generator import build_pdf_report
from app.reports.docx_generator import build_docx_report


# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WeighProof Metrological Governance Engine",
    description="Non-Automatic Weighing Instruments (NAWI) Type Evaluation and Test Report Generator based on OIML R 76",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper for JSON decimal encoding
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, "value"):
        return obj.value
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# Startup event: seed initial users if not present
@app.on_event("startup")
def startup_seed_users():
    db = next(get_db())
    try:
        users = [
            ("tester", "tester123", "Priya Sharma (Test Officer)", "tester"),
            ("reviewer", "reviewer123", "Dr. Rajesh Verma (Senior Metrologist)", "reviewer"),
            ("admin", "admin123", "Amit Patel (Lab Director)", "admin"),
        ]
        for username, pwd, name, role in users:
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                u = User(
                    username=username,
                    hashed_password=hash_password(pwd),
                    full_name=name,
                    role=role
                )
                db.add(u)
        db.commit()
    finally:
        db.close()


# ─── AUTHENTICATION SCHEMAS & ENDPOINTS ───
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    full_name: str


@app.post("/api/auth/login", response_model=LoginResponse, tags=["Authentication"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token({"sub": user.username, "role": user.role})
    log_audit_event(db, user.username, user.role, "USER_LOGIN", "User", str(user.id))
    return LoginResponse(
        access_token=token,
        username=user.username,
        role=user.role,
        full_name=user.full_name
    )


@app.get("/api/auth/me", tags=["Authentication"])
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "full_name": current_user.full_name
    }


# ─── RULESET ENDPOINTS (INNOVATION A) ───
@app.get("/api/rulesets", tags=["Rulesets"])
def list_rulesets():
    return ruleset_registry.list_rulesets()


@app.get("/api/rulesets/{ruleset_id}", tags=["Rulesets"])
def get_ruleset_details(ruleset_id: str):
    try:
        return ruleset_registry.get_ruleset(ruleset_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/rulesets/reload", tags=["Rulesets"])
def reload_rulesets(
    current_user: User = Depends(require_roles(["admin", "reviewer", "tester"]))
):
    ruleset_registry.reload()
    return {
        "status": "success",
        "message": "Rulesets reloaded successfully from disk.",
        "loaded_rulesets": ruleset_registry.list_rulesets()
    }


@app.post("/api/rulesets", tags=["Rulesets"])
def register_ruleset(
    ruleset_data: Dict[str, Any],
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    try:
        r_id = ruleset_registry.register_ruleset(ruleset_data, save_to_disk=True)
        log_audit_event(db, current_user.username, current_user.role, "RULESET_REGISTERED", "Ruleset", r_id)
        return {"status": "success", "ruleset_id": r_id, "message": "Ruleset registered dynamically."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── METROLOGICAL EVALUATION ENDPOINTS (INNOVATION B) ───
class PlausibilityRequest(BaseModel):
    instrument: InstrumentMasterData
    ruleset_id: str = "oiml_r76_2006"


@app.post("/api/evaluate/plausibility", tags=["Evaluation Engine"])
def api_evaluate_plausibility(req: PlausibilityRequest):
    try:
        ruleset = ruleset_registry.get_ruleset(req.ruleset_id)
        res = evaluate_instrument_plausibility(req.instrument, ruleset)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class MpeRequest(BaseModel):
    load: Decimal
    instrument: InstrumentMasterData
    ruleset_id: str = "oiml_r76_2006"
    is_in_service: bool = False


@app.post("/api/evaluate/mpe", tags=["Evaluation Engine"])
def api_calculate_mpe(req: MpeRequest):
    try:
        ruleset = ruleset_registry.get_ruleset(req.ruleset_id)
        return calculate_mpe(req.load, req.instrument, ruleset, is_in_service=req.is_in_service)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class WeighingPerformanceRequest(BaseModel):
    instrument: InstrumentMasterData
    points: List[WeighingPointInput]
    ruleset_id: str = "oiml_r76_2006"
    initial_zero_error_e0: Optional[Decimal] = None
    is_in_service: bool = False


@app.post("/api/evaluate/weighing-performance", tags=["Evaluation Engine"])
def api_evaluate_weighing_performance(req: WeighingPerformanceRequest):
    try:
        ruleset = ruleset_registry.get_ruleset(req.ruleset_id)
        return evaluate_weighing_performance(
            req.instrument,
            req.points,
            ruleset,
            initial_zero_error_e0=req.initial_zero_error_e0,
            is_in_service=req.is_in_service
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class EccentricityRequest(BaseModel):
    instrument: InstrumentMasterData
    positions: List[EccentricityPositionInput]
    ruleset_id: str = "oiml_r76_2006"
    initial_zero_error_e0: Decimal = Decimal(0)
    is_in_service: bool = False


@app.post("/api/evaluate/eccentricity", tags=["Evaluation Engine"])
def api_evaluate_eccentricity(req: EccentricityRequest):
    try:
        ruleset = ruleset_registry.get_ruleset(req.ruleset_id)
        return evaluate_eccentricity(
            req.instrument,
            req.positions,
            ruleset,
            initial_zero_error_e0=req.initial_zero_error_e0,
            is_in_service=req.is_in_service
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class RepeatabilityRequest(BaseModel):
    instrument: InstrumentMasterData
    series: Dict[str, List[RepeatabilityRunInput]]
    ruleset_id: str = "oiml_r76_2006"
    is_in_service: bool = False


@app.post("/api/evaluate/repeatability", tags=["Evaluation Engine"])
def api_evaluate_repeatability(req: RepeatabilityRequest):
    try:
        ruleset = ruleset_registry.get_ruleset(req.ruleset_id)
        return evaluate_repeatability(
            req.instrument,
            req.series,
            ruleset,
            is_in_service=req.is_in_service
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── TEST REPORT MANAGEMENT & AUDIT TRAIL (INNOVATION C) ───
class CreateReportRequest(BaseModel):
    report_number: str
    ruleset_id: str = "oiml_r76_2006"
    instrument: InstrumentMasterData
    weighing_points: List[WeighingPointInput]
    eccentricity_positions: List[EccentricityPositionInput]
    repeatability_series: Dict[str, List[RepeatabilityRunInput]]
    notes: Optional[str] = None


@app.post("/api/reports", tags=["Reports"])
def create_report(
    req: CreateReportRequest,
    current_user: User = Depends(require_roles(["tester", "admin"])),
    db: Session = Depends(get_db)
):
    existing = db.query(TestReport).filter(TestReport.report_number == req.report_number).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Report number '{req.report_number}' already exists.")

    ruleset = ruleset_registry.get_ruleset(req.ruleset_id)

    # Run evaluations
    plaus = evaluate_instrument_plausibility(req.instrument, ruleset)
    wp = evaluate_weighing_performance(req.instrument, req.weighing_points, ruleset)
    ecc = evaluate_eccentricity(req.instrument, req.eccentricity_positions, ruleset)
    rep = evaluate_repeatability(req.instrument, req.repeatability_series, ruleset)

    overall_pass = (
        plaus.is_valid and
        wp.overall_verdict == Verdict.PASS and
        ecc.overall_verdict == Verdict.PASS and
        rep.overall_verdict == Verdict.PASS
    )
    overall_verdict = "PASS" if overall_pass else "FAIL"

    eval_results = {
        "plausibility": json.loads(plaus.model_dump_json()),
        "weighing_performance": json.loads(wp.model_dump_json()),
        "eccentricity": json.loads(ecc.model_dump_json()),
        "repeatability": json.loads(rep.model_dump_json()),
    }

    report = TestReport(
        report_number=req.report_number,
        version=1,
        status="DRAFT",
        overall_verdict=overall_verdict,
        ruleset_id=req.ruleset_id,
        ruleset_edition=ruleset.get("edition", "2006 (E)"),
        instrument_snapshot_json=req.instrument.model_dump_json(),
        evaluation_results_json=json.dumps(eval_results, default=decimal_default),
        notes=req.notes,
        created_by=current_user.username
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    log_audit_event(db, current_user.username, current_user.role, "REPORT_CREATED", "TestReport", str(report.id))
    return {"status": "success", "report_id": report.id, "report_number": report.report_number, "overall_verdict": overall_verdict}


class UpdateReportRequest(BaseModel):
    notes: Optional[str] = None


@app.put("/api/reports/{report_id}", tags=["Reports"])
def update_report(
    report_id: int,
    req: UpdateReportRequest,
    current_user: User = Depends(require_roles(["tester", "admin"])),
    db: Session = Depends(get_db)
):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.status == "SIGNED":
        raise HTTPException(status_code=409, detail="Signed reports are sealed and immutable. Branch a new version instead.")

    if req.notes is not None:
        report.notes = req.notes
    db.commit()
    log_audit_event(db, current_user.username, current_user.role, "REPORT_UPDATED", "TestReport", str(report.id))
    return {"status": "success", "message": "Report updated successfully."}


@app.get("/api/reports", tags=["Reports"])
def list_reports(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    accuracy_class: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(TestReport)
    if status_filter:
        query = query.filter(TestReport.status == status_filter)
    if search:
        query = query.filter(
            (TestReport.report_number.ilike(f"%{search}%")) |
            (TestReport.instrument_snapshot_json.ilike(f"%{search}%"))
        )
    reports = query.order_by(TestReport.id.desc()).all()

    output = []
    for r in reports:
        inst = json.loads(r.instrument_snapshot_json)
        if accuracy_class and inst.get("accuracy_class") != accuracy_class:
            continue
        output.append({
            "id": r.id,
            "report_number": r.report_number,
            "version": r.version,
            "status": r.status,
            "overall_verdict": r.overall_verdict,
            "ruleset_id": r.ruleset_id,
            "ruleset_edition": r.ruleset_edition,
            "created_by": r.created_by,
            "reviewer_username": r.reviewer_username,
            "signed_at": r.signed_at.isoformat() if r.signed_at else None,
            "canonical_hash": r.canonical_hash,
            "manufacturer": inst.get("manufacturer"),
            "model": inst.get("model"),
            "serial_number": inst.get("serial_number"),
            "accuracy_class": inst.get("accuracy_class"),
            "max_capacity": inst.get("max_capacity"),
            "unit": inst.get("unit"),
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return output


@app.get("/api/reports/{report_id}", tags=["Reports"])
def get_report_details(report_id: int, db: Session = Depends(get_db)):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Test report not found.")

    return {
        "id": report.id,
        "report_number": report.report_number,
        "version": report.version,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "ruleset_id": report.ruleset_id,
        "ruleset_edition": report.ruleset_edition,
        "instrument_snapshot": json.loads(report.instrument_snapshot_json),
        "evaluation_results": json.loads(report.evaluation_results_json),
        "notes": report.notes,
        "created_by": report.created_by,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "submitted_by": report.submitted_by,
        "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
        "reviewer_username": report.reviewer_username,
        "reviewer_comments": report.reviewer_comments,
        "signed_at": report.signed_at.isoformat() if report.signed_at else None,
        "canonical_hash": report.canonical_hash,
        "qr_data_uri": report.qr_data_uri
    }


@app.post("/api/reports/{report_id}/submit", tags=["Reports"])
def submit_report(
    report_id: int,
    current_user: User = Depends(require_roles(["tester", "admin"])),
    db: Session = Depends(get_db)
):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.status == "SIGNED":
        raise HTTPException(status_code=409, detail="Signed reports are locked and cannot be resubmitted.")

    report.status = "SUBMITTED"
    report.submitted_by = current_user.username
    report.submitted_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()

    log_audit_event(db, current_user.username, current_user.role, "REPORT_SUBMITTED", "TestReport", str(report.id))
    return {"status": "success", "message": "Report submitted for reviewer sign-off."}


class SignReportRequest(BaseModel):
    comments: Optional[str] = None


@app.post("/api/reports/{report_id}/sign", tags=["Reports"])
def sign_report(
    report_id: int,
    req: SignReportRequest,
    current_user: User = Depends(require_roles(["reviewer", "admin"])),
    db: Session = Depends(get_db)
):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.status == "SIGNED":
        raise HTTPException(status_code=409, detail="Report is already signed and locked.")

    signed_timestamp = datetime.datetime.now(datetime.timezone.utc)
    signed_at_str = signed_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    report.status = "SIGNED"
    report.reviewer_username = current_user.username
    report.reviewer_comments = req.comments
    report.signed_at = signed_timestamp

    # Compute canonical SHA-256 hash (INNOVATION C)
    report_dict = {
        "report_number": report.report_number,
        "version": report.version,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "ruleset_id": report.ruleset_id,
        "ruleset_edition": report.ruleset_edition,
        "instrument_snapshot": json.loads(report.instrument_snapshot_json),
        "evaluation_results": json.loads(report.evaluation_results_json),
        "created_by": report.created_by,
        "reviewer_username": report.reviewer_username,
        "signed_at": signed_at_str
    }
    sha256_hash = compute_report_hash(report_dict)
    qr_uri, _ = generate_verification_qr_code(report.report_number, sha256_hash)

    report.canonical_hash = sha256_hash
    report.qr_data_uri = qr_uri
    db.commit()

    log_audit_event(
        db, current_user.username, current_user.role, "REPORT_SIGNED", "TestReport",
        str(report.id), json.dumps({"sha256": sha256_hash})
    )
    return {
        "status": "success",
        "message": "Report signed, locked, and cryptographically sealed.",
        "canonical_hash": sha256_hash,
        "qr_data_uri": qr_uri
    }


@app.post("/api/reports/{report_id}/reject", tags=["Reports"])
def reject_report(
    report_id: int,
    req: SignReportRequest,
    current_user: User = Depends(require_roles(["reviewer", "admin"])),
    db: Session = Depends(get_db)
):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.status == "SIGNED":
        raise HTTPException(status_code=409, detail="Signed reports cannot be rejected.")

    report.status = "REJECTED"
    report.reviewer_username = current_user.username
    report.reviewer_comments = req.comments
    db.commit()

    log_audit_event(db, current_user.username, current_user.role, "REPORT_REJECTED", "TestReport", str(report.id))
    return {"status": "success", "message": "Report marked as REJECTED."}


@app.post("/api/reports/{report_id}/branch-version", tags=["Reports"])
def branch_version(
    report_id: int,
    current_user: User = Depends(require_roles(["tester", "admin"])),
    db: Session = Depends(get_db)
):
    orig = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="Original report not found.")

    new_version_num = orig.version + 1
    new_report_number = f"{orig.report_number.split('-v')[0]}-v{new_version_num}"

    new_report = TestReport(
        report_number=new_report_number,
        version=new_version_num,
        status="DRAFT",
        overall_verdict=orig.overall_verdict,
        ruleset_id=orig.ruleset_id,
        ruleset_edition=orig.ruleset_edition,
        instrument_id=orig.instrument_id,
        instrument_snapshot_json=orig.instrument_snapshot_json,
        evaluation_results_json=orig.evaluation_results_json,
        notes=f"Branched from {orig.report_number} (v{orig.version}).",
        created_by=current_user.username
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    log_audit_event(
        db, current_user.username, current_user.role, "REPORT_VERSION_BRANCHED", "TestReport",
        str(new_report.id), json.dumps({"parent_id": orig.id, "new_version": new_version_num})
    )
    return {
        "status": "success",
        "new_report_id": new_report.id,
        "new_report_number": new_report.report_number,
        "version": new_version_num
    }


# ─── VERIFICATION & EXPORT ENDPOINTS ───
@app.get("/api/reports/verify/{report_number}", tags=["Verification"])
def public_verify_report(report_number: str, hash: str = Query(...), db: Session = Depends(get_db)):
    report = db.query(TestReport).filter(TestReport.report_number == report_number).first()
    if not report:
        return {"valid": False, "reason": "Report number not found in official registry."}

    if report.status != "SIGNED":
        return {"valid": False, "reason": "Report has not been signed by an authorized reviewer."}

    report_dict = {
        "report_number": report.report_number,
        "version": report.version,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "ruleset_id": report.ruleset_id,
        "ruleset_edition": report.ruleset_edition,
        "instrument_snapshot": json.loads(report.instrument_snapshot_json),
        "evaluation_results": json.loads(report.evaluation_results_json),
        "created_by": report.created_by,
        "reviewer_username": report.reviewer_username,
        "signed_at": report.signed_at.strftime("%Y-%m-%dT%H:%M:%SZ") if report.signed_at else None
    }
    is_valid = verify_report_integrity(report_dict, hash)
    return {
        "valid": is_valid,
        "report_number": report.report_number,
        "version": report.version,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "reviewer": report.reviewer_username,
        "signed_at": report.signed_at.strftime("%Y-%m-%dT%H:%M:%SZ") if report.signed_at else None,
        "canonical_hash": report.canonical_hash,
        "tamper_detected": not is_valid
    }


@app.get("/api/reports/{report_id}/export/pdf", tags=["Export"])
def export_pdf(report_id: int, db: Session = Depends(get_db)):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    report_data = {
        "report_number": report.report_number,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "ruleset_id": report.ruleset_id,
        "ruleset_edition": report.ruleset_edition,
        "instrument_snapshot": json.loads(report.instrument_snapshot_json),
        "evaluation_results": json.loads(report.evaluation_results_json),
        "created_by": report.created_by,
        "reviewer_username": report.reviewer_username,
        "signed_at": report.signed_at.strftime("%Y-%m-%d %H:%M:%S UTC") if report.signed_at else "DRAFT (Unsigned)",
        "canonical_hash": report.canonical_hash or "DRAFT_UNSIGNED_REPORT"
    }
    pdf_bytes = build_pdf_report(report_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={report.report_number}.pdf"}
    )


@app.get("/api/reports/{report_id}/export/docx", tags=["Export"])
def export_docx(report_id: int, db: Session = Depends(get_db)):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    report_data = {
        "report_number": report.report_number,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "ruleset_id": report.ruleset_id,
        "ruleset_edition": report.ruleset_edition,
        "instrument_snapshot": json.loads(report.instrument_snapshot_json),
        "evaluation_results": json.loads(report.evaluation_results_json),
        "created_by": report.created_by,
        "reviewer_username": report.reviewer_username,
        "signed_at": report.signed_at.strftime("%Y-%m-%d %H:%M:%S UTC") if report.signed_at else "DRAFT (Unsigned)",
        "canonical_hash": report.canonical_hash or "DRAFT_UNSIGNED_REPORT"
    }
    docx_bytes = build_docx_report(report_data)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={report.report_number}.docx"}
    )


@app.get("/api/reports/{report_id}/export/json", tags=["Export"])
def export_json(report_id: int, db: Session = Depends(get_db)):
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    payload = {
        "standard": "OIML R 76-2:2007",
        "dcc_profile": "EURAMET/CG-18 & PTB IMEKO TC6",
        "report_number": report.report_number,
        "version": report.version,
        "status": report.status,
        "overall_verdict": report.overall_verdict,
        "ruleset_id": report.ruleset_id,
        "ruleset_edition": report.ruleset_edition,
        "instrument_snapshot": json.loads(report.instrument_snapshot_json),
        "evaluation_results": json.loads(report.evaluation_results_json),
        "canonical_sha256": report.canonical_hash,
        "signed_at": report.signed_at.isoformat() if report.signed_at else None,
        "reviewer": report.reviewer_username
    }
    return JSONResponse(content=payload)


# ─── AUDIT & DASHBOARD METRICS ───
@app.get("/api/audit-logs", tags=["Audit"])
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_roles(["admin", "reviewer"])),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "username": l.username,
            "role": l.role,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": json.loads(l.details_json) if l.details_json else None
        }
        for l in logs
    ]


@app.get("/api/dashboard/stats", tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_reports = db.query(TestReport).count()
    signed_reports = db.query(TestReport).filter(TestReport.status == "SIGNED").count()
    draft_reports = db.query(TestReport).filter(TestReport.status == "DRAFT").count()
    submitted_reports = db.query(TestReport).filter(TestReport.status == "SUBMITTED").count()
    rejected_reports = db.query(TestReport).filter(TestReport.status == "REJECTED").count()
    pass_count = db.query(TestReport).filter(TestReport.overall_verdict == "PASS").count()
    fail_count = db.query(TestReport).filter(TestReport.overall_verdict == "FAIL").count()

    return {
        "total_reports": total_reports,
        "signed_reports": signed_reports,
        "draft_reports": draft_reports,
        "submitted_reports": submitted_reports,
        "rejected_reports": rejected_reports,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "rulesets_available": len(ruleset_registry.list_rulesets()),
        "integrity_standard": "SHA-256 / OIML R 76-2"
    }


# ─── SYNTHETIC DATA SEED ENDPOINT ───
@app.post("/api/synthetic/seed", tags=["Synthetic Data"])
def seed_synthetic_data(db: Session = Depends(get_db)):
    """Seeds the 3 verified synthetic instruments and failing test case."""
    oracle_path = Path(__file__).resolve().parents[2] / "docs" / "oracle" / "oracle_class_iii_6kg.json"
    with open(oracle_path, "r", encoding="utf-8") as f:
        oracle_data = json.load(f)

    # 1. 6kg Class III scale (PASS)
    rep1_exists = db.query(TestReport).filter(TestReport.report_number == "REP-2026-6KG-001").first()
    if not rep1_exists:
        inst1_data = InstrumentMasterData(**oracle_data["instrument"])
        ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
        plaus = evaluate_instrument_plausibility(inst1_data, ruleset)
        wp_pts = [WeighingPointInput(**p) for p in oracle_data["tests"]["weighing_performance"]["points"]]
        wp = evaluate_weighing_performance(inst1_data, wp_pts, ruleset, initial_zero_error_e0=Decimal("0.2"))
        ecc_pos = [EccentricityPositionInput(**p) for p in oracle_data["tests"]["eccentricity"]["positions"]]
        ecc = evaluate_eccentricity(inst1_data, ecc_pos, ruleset, initial_zero_error_e0=Decimal("0.2"))
        rep_runs = [RepeatabilityRunInput(run_number=r["run"], load=Decimal(str(r["load"])), indicated=Decimal(str(r["indicated"])), delta_load=Decimal(str(r["delta_load"]))) for r in oracle_data["tests"]["repeatability"]["series_1"]["runs"]]
        rep = evaluate_repeatability(inst1_data, {"Series 1 (50% Max)": rep_runs}, ruleset)

        eval_res1 = {
            "plausibility": json.loads(plaus.model_dump_json()),
            "weighing_performance": json.loads(wp.model_dump_json()),
            "eccentricity": json.loads(ecc.model_dump_json()),
            "repeatability": json.loads(rep.model_dump_json()),
        }
        rep1 = TestReport(
            report_number="REP-2026-6KG-001",
            version=1,
            status="SIGNED",
            overall_verdict="PASS",
            ruleset_id="oiml_r76_2006",
            ruleset_edition="2006 (E)",
            instrument_snapshot_json=inst1_data.model_dump_json(),
            evaluation_results_json=json.dumps(eval_res1, default=decimal_default),
            notes="Synthetic Benchmark Scale 6kg / 2g Class III (Full PASS)",
            created_by="tester",
            reviewer_username="reviewer",
            signed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        # Compute hash
        rep1_dict = {
            "report_number": rep1.report_number,
            "version": rep1.version,
            "status": rep1.status,
            "overall_verdict": rep1.overall_verdict,
            "ruleset_id": rep1.ruleset_id,
            "ruleset_edition": rep1.ruleset_edition,
            "instrument_snapshot": json.loads(rep1.instrument_snapshot_json),
            "evaluation_results": json.loads(rep1.evaluation_results_json),
            "created_by": rep1.created_by,
            "reviewer_username": rep1.reviewer_username,
            "signed_at": rep1.signed_at.isoformat()
        }
        h1 = compute_report_hash(rep1_dict)
        qr1, _ = generate_verification_qr_code(rep1.report_number, h1)
        rep1.canonical_hash = h1
        rep1.qr_data_uri = qr1
        db.add(rep1)

    # 2. 600g Class II Lab Balance (PASS)
    rep2_exists = db.query(TestReport).filter(TestReport.report_number == "REP-2026-LAB-002").first()
    if not rep2_exists:
        inst2 = InstrumentMasterData(
            manufacturer="Mettler Toledo",
            model="ME204",
            serial_number="SN-ME-9912",
            accuracy_class=AccuracyClass.CLASS_II,
            max_capacity=Decimal("600"),
            min_capacity=Decimal("2"),
            verification_scale_interval_e=Decimal("0.1"),
            actual_scale_interval_d=Decimal("0.01"),
            unit="g",
            device_type=DeviceType.GRADUATED_WITH_AUX
        )
        ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
        plaus2 = evaluate_instrument_plausibility(inst2, ruleset)
        wp2_pts = [
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("0"), indicated=Decimal("0.00"), delta_load=None),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("2"), indicated=Decimal("2.00"), delta_load=None),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("200"), indicated=Decimal("200.01"), delta_load=None),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("400"), indicated=Decimal("400.02"), delta_load=None),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("600"), indicated=Decimal("600.02"), delta_load=None),
        ]
        wp2 = evaluate_weighing_performance(inst2, wp2_pts, ruleset)
        ecc2_pos = [
            EccentricityPositionInput(position_id="center", description="Center", load=Decimal("200"), indicated=Decimal("200.00")),
            EccentricityPositionInput(position_id="pos_1", description="Quadrant 1", load=Decimal("200"), indicated=Decimal("200.02")),
            EccentricityPositionInput(position_id="pos_2", description="Quadrant 2", load=Decimal("200"), indicated=Decimal("200.01")),
        ]
        ecc2 = evaluate_eccentricity(inst2, ecc2_pos, ruleset)
        rep2_runs = [RepeatabilityRunInput(run_number=i+1, load=Decimal("300"), indicated=Decimal("300.01")) for i in range(10)]
        rep2 = evaluate_repeatability(inst2, {"50% Max": rep2_runs}, ruleset)

        eval_res2 = {
            "plausibility": json.loads(plaus2.model_dump_json()),
            "weighing_performance": json.loads(wp2.model_dump_json()),
            "eccentricity": json.loads(ecc2.model_dump_json()),
            "repeatability": json.loads(rep2.model_dump_json()),
        }
        rep2 = TestReport(
            report_number="REP-2026-LAB-002",
            version=1,
            status="SUBMITTED",
            overall_verdict="PASS",
            ruleset_id="oiml_r76_2006",
            ruleset_edition="2006 (E)",
            instrument_snapshot_json=inst2.model_dump_json(),
            evaluation_results_json=json.dumps(eval_res2, default=decimal_default),
            notes="Precision Class II Balance 600g / 0.01g with auxiliary reading",
            created_by="tester",
            submitted_by="tester",
            submitted_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(rep2)

    # 3. 30t Weighbridge (PASS)
    rep3_exists = db.query(TestReport).filter(TestReport.report_number == "REP-2026-WB-003").first()
    if not rep3_exists:
        inst3 = InstrumentMasterData(
            manufacturer="Avery Weigh-Tronix",
            model="BridgeMaster 30T",
            serial_number="SN-BM-3001",
            accuracy_class=AccuracyClass.CLASS_III,
            max_capacity=Decimal("30000"),
            min_capacity=Decimal("200"),
            verification_scale_interval_e=Decimal("10"),
            actual_scale_interval_d=Decimal("10"),
            unit="kg",
            points_of_support=6
        )
        ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
        plaus3 = evaluate_instrument_plausibility(inst3, ruleset)
        wp3_pts = [
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("0"), indicated=Decimal("0")),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("200"), indicated=Decimal("200")),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("10000"), indicated=Decimal("10000")),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("20000"), indicated=Decimal("20000")),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("30000"), indicated=Decimal("30000")),
        ]
        wp3 = evaluate_weighing_performance(inst3, wp3_pts, ruleset)
        ecc3_pos = [
            EccentricityPositionInput(position_id=f"support_{i+1}", description=f"Load cell {i+1}", load=Decimal("6000"), indicated=Decimal("6000"))
            for i in range(6)
        ]
        ecc3 = evaluate_eccentricity(inst3, ecc3_pos, ruleset)
        rep3_runs = [RepeatabilityRunInput(run_number=i+1, load=Decimal("15000"), indicated=Decimal("15000")) for i in range(3)]
        rep3 = evaluate_repeatability(inst3, {"50% Max": rep3_runs}, ruleset)

        eval_res3 = {
            "plausibility": json.loads(plaus3.model_dump_json()),
            "weighing_performance": json.loads(wp3.model_dump_json()),
            "eccentricity": json.loads(ecc3.model_dump_json()),
            "repeatability": json.loads(rep3.model_dump_json()),
        }
        rep3 = TestReport(
            report_number="REP-2026-WB-003",
            version=1,
            status="DRAFT",
            overall_verdict="PASS",
            ruleset_id="oiml_r76_2006",
            ruleset_edition="2006 (E)",
            instrument_snapshot_json=inst3.model_dump_json(),
            evaluation_results_json=json.dumps(eval_res3, default=decimal_default),
            notes="Heavy Industrial 30t Vehicle Weighbridge",
            created_by="tester"
        )
        db.add(rep3)

    # 4. Deliberate FAILING case (MPE violation on corner 3 and high load)
    rep4_exists = db.query(TestReport).filter(TestReport.report_number == "REP-2026-FAIL-004").first()
    if not rep4_exists:
        inst4 = InstrumentMasterData(
            manufacturer="Defective Scales Co.",
            model="FaultyCounter",
            serial_number="SN-DEFECT-01",
            accuracy_class=AccuracyClass.CLASS_III,
            max_capacity=Decimal("6000"),
            min_capacity=Decimal("40"),
            verification_scale_interval_e=Decimal("2"),
            actual_scale_interval_d=Decimal("2"),
            unit="g"
        )
        ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
        plaus4 = evaluate_instrument_plausibility(inst4, ruleset)
        wp4_pts = [
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("0"), indicated=Decimal("0")),
            WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("4000"), indicated=Decimal("4004")), # error 4g > MPE (2g) -> FAIL!
        ]
        wp4 = evaluate_weighing_performance(inst4, wp4_pts, ruleset)
        ecc4_pos = [
            EccentricityPositionInput(position_id="pos_1", description="Corner 1", load=Decimal("2000"), indicated=Decimal("2000")),
            EccentricityPositionInput(position_id="pos_3", description="Corner 3 (Defective Bearing)", load=Decimal("2000"), indicated=Decimal("2004")), # FAIL
        ]
        ecc4 = evaluate_eccentricity(inst4, ecc4_pos, ruleset)
        rep4_runs = [
            RepeatabilityRunInput(run_number=1, load=Decimal("3000"), indicated=Decimal("2998")),
            RepeatabilityRunInput(run_number=2, load=Decimal("3000"), indicated=Decimal("3003")), # spread 5g > MPE (2g) -> FAIL
        ]
        rep4 = evaluate_repeatability(inst4, {"Series Fail": rep4_runs}, ruleset)

        eval_res4 = {
            "plausibility": json.loads(plaus4.model_dump_json()),
            "weighing_performance": json.loads(wp4.model_dump_json()),
            "eccentricity": json.loads(ecc4.model_dump_json()),
            "repeatability": json.loads(rep4.model_dump_json()),
        }
        rep4 = TestReport(
            report_number="REP-2026-FAIL-004",
            version=1,
            status="REJECTED",
            overall_verdict="FAIL",
            ruleset_id="oiml_r76_2006",
            ruleset_edition="2006 (E)",
            instrument_snapshot_json=inst4.model_dump_json(),
            evaluation_results_json=json.dumps(eval_res4, default=decimal_default),
            notes="Benchmark Defective Instrument (Deliberate Multiple Failure Modes for QA Verification)",
            created_by="tester",
            reviewer_username="reviewer",
            reviewer_comments="REJECTED: Severe eccentricity failure on position 3 and weighing linearity failure beyond 4000g.",
            signed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(rep4)

    db.commit()
    return {"status": "success", "message": "Synthetic datasets seeded successfully."}


# Mount compiled frontend static files if present
dist_path = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if dist_path.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")

