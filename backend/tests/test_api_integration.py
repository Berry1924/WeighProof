import pytest
from decimal import Decimal
import json
import uuid
from fastapi.testclient import TestClient

from app.main import app, startup_seed_users
from app.db import Base, engine, get_db
from app.models import TestReport, User


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    startup_seed_users()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def get_token_for(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_auth_login_success_and_failure(client):
    # Good login
    resp = client.post("/api/auth/login", json={"username": "tester", "password": "tester123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "tester"

    # Bad login
    resp_bad = client.post("/api/auth/login", json={"username": "tester", "password": "wrongpassword"})
    assert resp_bad.status_code == 401


def test_ruleset_endpoints(client):
    resp = client.get("/api/rulesets")
    assert resp.status_code == 200
    rulesets = resp.json()
    assert any(r["ruleset_id"] == "oiml_r76_2006" for r in rulesets)

    resp_det = client.get("/api/rulesets/oiml_r76_2006")
    assert resp_det.status_code == 200
    assert resp_det.json()["edition"] == "2006 (E)"


def test_full_report_lifecycle_and_immutability(client):
    tester_token = get_token_for(client, "tester", "tester123")
    reviewer_token = get_token_for(client, "reviewer", "reviewer123")

    unique_num = f"REP-INT-{uuid.uuid4().hex[:6].upper()}"

    report_payload = {
        "report_number": unique_num,
        "ruleset_id": "oiml_r76_2006",
        "instrument": {
            "manufacturer": "Dibal",
            "model": "CS-6000",
            "serial_number": f"SN-{unique_num}",
            "accuracy_class": "III",
            "max_capacity": 6000.0,
            "min_capacity": 40.0,
            "verification_scale_interval_e": 2.0,
            "actual_scale_interval_d": 2.0,
            "unit": "g"
        },
        "weighing_points": [
            {"direction": "increasing", "load": 0.0, "indicated": 0.0, "delta_load": 0.8},
            {"direction": "increasing", "load": 40.0, "indicated": 40.0, "delta_load": 0.9},
            {"direction": "increasing", "load": 2000.0, "indicated": 2000.0, "delta_load": 0.6},
            {"direction": "increasing", "load": 6000.0, "indicated": 6000.0, "delta_load": 0.4}
        ],
        "eccentricity_positions": [
            {"position_id": "center", "description": "Center", "load": 2000.0, "indicated": 2000.0, "delta_load": 0.8},
            {"position_id": "pos_1", "description": "Corner 1", "load": 2000.0, "indicated": 2000.0, "delta_load": 0.5}
        ],
        "repeatability_series": {
            "50% Max": [
                {"run_number": 1, "load": 3000.0, "indicated": 3000.0, "delta_load": 0.8},
                {"run_number": 2, "load": 3000.0, "indicated": 3000.0, "delta_load": 0.7}
            ]
        },
        "notes": "Integration test report"
    }

    # 1. Tester creates report (DRAFT)
    res_create = client.post(
        "/api/reports",
        json=report_payload,
        headers={"Authorization": f"Bearer {tester_token}"}
    )
    assert res_create.status_code == 200, res_create.text
    rep_id = res_create.json()["report_id"]

    # 2. RBAC check: Tester cannot sign
    res_sign_bad = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Should fail"},
        headers={"Authorization": f"Bearer {tester_token}"}
    )
    assert res_sign_bad.status_code == 403

    # 3. Tester submits report
    res_sub = client.post(
        f"/api/reports/{rep_id}/submit",
        headers={"Authorization": f"Bearer {tester_token}"}
    )
    assert res_sub.status_code == 200

    # 4. Reviewer signs report
    res_sign = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Approved for Type Examination Certificate"},
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert res_sign.status_code == 200
    sign_data = res_sign.json()
    assert "canonical_hash" in sign_data
    assert "qr_data_uri" in sign_data
    sha256 = sign_data["canonical_hash"]

    # 5. Immutability check: cannot sign again or submit again
    res_sign_again = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Second sign"},
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert res_sign_again.status_code == 409

    # 6. Verify public verification endpoint
    res_verify = client.get(f"/api/reports/verify/{unique_num}?hash={sha256}")
    assert res_verify.status_code == 200
    v_data = res_verify.json()
    assert v_data["valid"] is True
    assert v_data["tamper_detected"] is False

    # Bad hash check
    res_verify_bad = client.get(f"/api/reports/verify/{unique_num}?hash=wronghash123")
    assert res_verify_bad.status_code == 200
    assert res_verify_bad.json()["valid"] is False

    # 7. Branch to a new version (v2)
    res_branch = client.post(
        f"/api/reports/{rep_id}/branch-version",
        headers={"Authorization": f"Bearer {tester_token}"}
    )
    assert res_branch.status_code == 200
    branch_data = res_branch.json()
    assert branch_data["version"] == 2
    assert branch_data["new_report_number"] == f"{unique_num}-v2"


def test_export_pdf_docx_json(client):
    # Seed synthetic data first
    res_seed = client.post("/api/synthetic/seed")
    assert res_seed.status_code == 200

    # Get report ID for REP-2026-6KG-001
    rep_list = client.get("/api/reports?search=REP-2026-6KG-001").json()
    assert len(rep_list) > 0
    target_id = rep_list[0]["id"]

    # Test PDF Export
    pdf_resp = client.get(f"/api/reports/{target_id}/export/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-")

    # Test DOCX Export
    docx_resp = client.get(f"/api/reports/{target_id}/export/docx")
    assert docx_resp.status_code == 200
    assert "wordprocessingml" in docx_resp.headers["content-type"]
    assert docx_resp.content.startswith(b"PK")  # ZIP header for DOCX

    # Test JSON Export
    json_resp = client.get(f"/api/reports/{target_id}/export/json")
    assert json_resp.status_code == 200
    data = json_resp.json()
    assert data["report_number"] == "REP-2026-6KG-001"
    assert data["standard"] == "OIML R 76-2:2007"
    assert "canonical_sha256" in data


def test_audit_logs_and_dashboard_stats(client):
    admin_token = get_token_for(client, "admin", "admin123")

    # Query audit logs
    logs_resp = client.get(
        "/api/audit-logs?limit=20",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "USER_LOGIN" in actions

    # Query dashboard stats
    stats_resp = client.get("/api/dashboard/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_reports"] >= 1
    assert stats["rulesets_available"] >= 2
