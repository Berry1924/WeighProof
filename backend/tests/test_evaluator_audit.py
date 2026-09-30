import json
import uuid
import copy
from decimal import Decimal
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app, startup_seed_users
from app.db import Base, engine, get_db, SessionLocal
from app.models import TestReport, User
from app.engine.ruleset import ruleset_registry, DEFAULT_RULESETS_DIR
from app.engine.hasher import compute_report_hash


@pytest.fixture(scope="module", autouse=True)
def setup_audit_env():
    Base.metadata.create_all(bind=engine)
    startup_seed_users()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def get_token(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


SAMPLE_WEIGHING_POINTS = [
    {"direction": "increasing", "load": 0.0, "indicated": 0.0, "delta_load": 0.8},
    {"direction": "increasing", "load": 40.0, "indicated": 40.0, "delta_load": 0.9},
    {"direction": "increasing", "load": 2000.0, "indicated": 2000.0, "delta_load": 0.6},
    {"direction": "increasing", "load": 6000.0, "indicated": 6000.0, "delta_load": 0.4}
]

SAMPLE_ECCENTRICITY_POSITIONS = [
    {"position_id": "center", "description": "Center", "load": 2000.0, "indicated": 2000.0, "delta_load": 0.8},
    {"position_id": "pos_1", "description": "Corner 1", "load": 2000.0, "indicated": 2000.0, "delta_load": 0.5}
]

SAMPLE_REPEATABILITY_SERIES = {
    "50% Max": [
        {"run_number": 1, "load": 3000.0, "indicated": 3000.0, "delta_load": 0.8},
        {"run_number": 2, "load": 3000.0, "indicated": 3000.0, "delta_load": 0.7}
    ]
}


def test_oracle_exact_numbers(client):
    """SIH Audit Check: Verify exact numbers from docs/oracle/oracle_class_iii_6kg.json."""
    oracle_path = Path(__file__).resolve().parents[2] / "docs" / "oracle" / "oracle_class_iii_6kg.json"
    with open(oracle_path, "r", encoding="utf-8") as f:
        oracle = json.load(f)

    # 1. Plausibility check
    resp_plaus = client.post("/api/evaluate/plausibility", json={
        "instrument": oracle["instrument"],
        "ruleset_id": "oiml_r76_2006"
    })
    assert resp_plaus.status_code == 200
    plaus_res = resp_plaus.json()
    assert plaus_res["is_valid"] is True
    assert int(float(plaus_res["calculated_n"])) == oracle["plausibility_expected"]["n_calculated"]
    assert int(float(plaus_res["allowed_n_min"])) == oracle["plausibility_expected"]["n_min_allowed"]
    assert int(float(plaus_res["allowed_n_max"])) == oracle["plausibility_expected"]["n_max_allowed"]

    # 2. Weighing Performance
    resp_wp = client.post("/api/evaluate/weighing-performance", json={
        "instrument": oracle["instrument"],
        "points": [
            {"direction": p["direction"], "load": p["load"], "indicated": p["indicated"], "delta_load": p["delta_load"]}
            for p in oracle["tests"]["weighing_performance"]["points"]
        ],
        "initial_zero_error_e0": oracle["tests"]["weighing_performance"]["initial_zero_error_e0"],
        "ruleset_id": "oiml_r76_2006"
    })
    assert resp_wp.status_code == 200
    wp_res = resp_wp.json()
    assert wp_res["overall_verdict"] == "PASS"

    for idx, expected in enumerate(oracle["tests"]["weighing_performance"]["points"]):
        actual = wp_res["points"][idx]
        assert float(actual["corrected_error_ec"]) == pytest.approx(expected["expected_corrected_error"], abs=1e-4)
        assert float(actual["mpe"]) == pytest.approx(expected["expected_mpe"], abs=1e-4)
        assert actual["verdict"] == expected["expected_verdict"]


def test_breaking_input_plausibility_rejections(client):
    """SIH Audit Check: Reject invalid instruments according to OIML R 76-1 Table 3 & Clauses."""
    base_inst = {
        "manufacturer": "FaultyScales Inc",
        "model": "Bad-1",
        "serial_number": "SN-BAD",
        "accuracy_class": "III",
        "max_capacity": 6000.0,
        "min_capacity": 40.0,
        "verification_scale_interval_e": 2.0,
        "actual_scale_interval_d": 2.0,
        "unit": "g"
    }

    # 1. n < n_min: for e=2g, n_min=100. Let Max=100g, e=2g => n=50 < 100
    inst_low_n = copy.deepcopy(base_inst)
    inst_low_n["max_capacity"] = 100.0
    inst_low_n["min_capacity"] = 40.0
    res = client.post("/api/evaluate/plausibility", json={"instrument": inst_low_n, "ruleset_id": "oiml_r76_2006"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is False
    failed_msgs = [c["message"] for c in data["checks"] if not c["passed"]]
    assert any("below minimum 100" in m for m in failed_msgs)

    # 2. n > n_max (e.g. Max = 30000, e = 2 => n = 15000 > 10000)
    inst_high_n = copy.deepcopy(base_inst)
    inst_high_n["max_capacity"] = 30000.0
    res = client.post("/api/evaluate/plausibility", json={"instrument": inst_high_n, "ruleset_id": "oiml_r76_2006"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is False
    failed_msgs = [c["message"] for c in data["checks"] if not c["passed"]]
    assert any("exceeds maximum 10000" in m for m in failed_msgs)

    # 3. Min < 20e (Min = 20g, e = 2g => 10e < 20e)
    inst_low_min = copy.deepcopy(base_inst)
    inst_low_min["min_capacity"] = 20.0
    res = client.post("/api/evaluate/plausibility", json={"instrument": inst_low_min, "ruleset_id": "oiml_r76_2006"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is False
    failed_msgs = [c["message"] for c in data["checks"] if not c["passed"]]
    assert any("below required minimum 40.0 g" in m for m in failed_msgs)

    # 4. Invalid e not in {1, 2, 5} * 10^k (e = 3g)
    inst_bad_e = copy.deepcopy(base_inst)
    inst_bad_e["verification_scale_interval_e"] = 3.0
    inst_bad_e["actual_scale_interval_d"] = 3.0
    res = client.post("/api/evaluate/plausibility", json={"instrument": inst_bad_e, "ruleset_id": "oiml_r76_2006"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is False
    failed_msgs = [c["message"] for c in data["checks"] if not c["passed"]]
    assert any("violates sequence {1, 2, 5} x 10^k" in m for m in failed_msgs)


def test_breaking_rbac_and_immutability(client):
    """SIH Audit Check: Enforce strict role boundaries and report immutability."""
    tester_tok = get_token(client, "tester", "tester123")
    reviewer_tok = get_token(client, "reviewer", "reviewer123")
    admin_tok = get_token(client, "admin", "admin123")

    # 1. Unauthenticated request
    unauth_res = client.post("/api/reports", json={})
    assert unauth_res.status_code == 401

    # 2. Reviewer cannot register ruleset (Admin only)
    ruleset_bad_role = client.post(
        "/api/rulesets",
        json={"ruleset_id": "forbidden"},
        headers={"Authorization": f"Bearer {reviewer_tok}"}
    )
    assert ruleset_bad_role.status_code == 403

    # 3. Create report as Tester
    rep_num = f"REP-AUDIT-{uuid.uuid4().hex[:6].upper()}"
    create_res = client.post(
        "/api/reports",
        json={
            "report_number": rep_num,
            "ruleset_id": "oiml_r76_2006",
            "instrument": {
                "manufacturer": "Kern",
                "model": "PCB-3000",
                "serial_number": "SN-KERN-1",
                "accuracy_class": "II",
                "max_capacity": 3000.0,
                "min_capacity": 5.0,
                "verification_scale_interval_e": 0.1,
                "actual_scale_interval_d": 0.01,
                "unit": "g"
            },
            "weighing_points": [
                {"direction": "increasing", "load": 0.0, "indicated": 0.0, "delta_load": 0.05},
                {"direction": "increasing", "load": 1000.0, "indicated": 1000.0, "delta_load": 0.04}
            ],
            "eccentricity_positions": [
                {"position_id": "center", "description": "Center", "load": 1000.0, "indicated": 1000.0, "delta_load": 0.05}
            ],
            "repeatability_series": {
                "50% Max": [
                    {"run_number": 1, "load": 1500.0, "indicated": 1500.0, "delta_load": 0.05},
                    {"run_number": 2, "load": 1500.0, "indicated": 1500.0, "delta_load": 0.04}
                ]
            }
        },
        headers={"Authorization": f"Bearer {tester_tok}"}
    )
    assert create_res.status_code == 200
    rep_id = create_res.json()["report_id"]

    # 4. Tester cannot sign (Reviewer only) -> 403
    sign_tester = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Tester attempting sign"},
        headers={"Authorization": f"Bearer {tester_tok}"}
    )
    assert sign_tester.status_code == 403

    # 5. Tester submits report
    client.post(f"/api/reports/{rep_id}/submit", headers={"Authorization": f"Bearer {tester_tok}"})

    # 6. Reviewer signs report -> Locks report permanently
    sign_rev = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Audit approval verified"},
        headers={"Authorization": f"Bearer {reviewer_tok}"}
    )
    assert sign_rev.status_code == 200

    # 7. Immutability: Attempting to edit or submit again -> 409 Conflict
    edit_again = client.put(
        f"/api/reports/{rep_id}",
        json={"notes": "Illegal edit after sign"},
        headers={"Authorization": f"Bearer {tester_tok}"}
    )
    assert edit_again.status_code == 409

    sign_again = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Duplicate sign"},
        headers={"Authorization": f"Bearer {reviewer_tok}"}
    )
    assert sign_again.status_code == 409


def test_tamper_detection_in_verification(client):
    """SIH Audit Check: Verify that altering database records triggers tamper detection."""
    tester_tok = get_token(client, "tester", "tester123")
    reviewer_tok = get_token(client, "reviewer", "reviewer123")

    rep_num = f"REP-TAMPER-{uuid.uuid4().hex[:6].upper()}"
    create_res = client.post(
        "/api/reports",
        json={
            "report_number": rep_num,
            "ruleset_id": "oiml_r76_2006",
            "instrument": {
                "manufacturer": "Avery",
                "model": "Weight-Tronix",
                "serial_number": "SN-TAMP",
                "accuracy_class": "III",
                "max_capacity": 6000.0,
                "min_capacity": 40.0,
                "verification_scale_interval_e": 2.0,
                "actual_scale_interval_d": 2.0,
                "unit": "g"
            },
            "weighing_points": SAMPLE_WEIGHING_POINTS,
            "eccentricity_positions": SAMPLE_ECCENTRICITY_POSITIONS,
            "repeatability_series": SAMPLE_REPEATABILITY_SERIES
        },
        headers={"Authorization": f"Bearer {tester_tok}"}
    )
    assert create_res.status_code == 200
    rep_id = create_res.json()["report_id"]

    client.post(f"/api/reports/{rep_id}/submit", headers={"Authorization": f"Bearer {tester_tok}"})
    sign_res = client.post(
        f"/api/reports/{rep_id}/sign",
        json={"comments": "Original pristine signature"},
        headers={"Authorization": f"Bearer {reviewer_tok}"}
    )
    assert sign_res.status_code == 200
    valid_hash = sign_res.json()["canonical_hash"]

    # Public verification should initially be valid and not tampered
    verify_res1 = client.get(f"/api/reports/verify/{rep_num}?hash={valid_hash}")
    assert verify_res1.status_code == 200
    assert verify_res1.json()["valid"] is True
    assert verify_res1.json()["tamper_detected"] is False

    # Simulate malicious tamper in database directly (bypassing API)
    db = SessionLocal()
    try:
        report_row = db.query(TestReport).filter(TestReport.id == rep_id).first()
        inst_data = json.loads(report_row.instrument_snapshot_json)
        # Maliciously change max capacity from 6000 to 9999
        inst_data["max_capacity"] = 9999.0
        report_row.instrument_snapshot_json = json.dumps(inst_data)
        db.commit()
    finally:
        db.close()

    # Re-verify: the database content no longer hashes to the signed hash!
    verify_res2 = client.get(f"/api/reports/verify/{rep_num}?hash={valid_hash}")
    assert verify_res2.status_code == 200
    v2_data = verify_res2.json()
    assert v2_data["valid"] is False
    assert v2_data["tamper_detected"] is True


def test_dynamic_ruleset_hot_reload_without_server_restart(client):
    """SIH Audit Check: Dropping a valid ruleset file into rulesets/ is detected live."""
    tester_tok = get_token(client, "tester", "tester123")
    custom_ruleset_path = DEFAULT_RULESETS_DIR / "custom_audit_test.json"

    # Base valid ruleset loaded from 2006 edition
    source_ruleset_path = DEFAULT_RULESETS_DIR / "oiml_r76_2006.json"
    with open(source_ruleset_path, "r", encoding="utf-8") as f:
        custom_ruleset_data = json.load(f)

    custom_ruleset_data["ruleset_id"] = "custom_audit_test"
    custom_ruleset_data["edition"] = "Custom Audit Edition 2026"
    custom_ruleset_data["accuracy_classes"]["III"]["classification_intervals"][0]["n_max"] = 8000

    try:
        # Write file directly to filesystem (simulating external file drop)
        with open(custom_ruleset_path, "w", encoding="utf-8") as f:
            json.dump(custom_ruleset_data, f, indent=2)

        # Trigger reload endpoint
        reload_res = client.post(
            "/api/rulesets/reload",
            headers={"Authorization": f"Bearer {tester_tok}"}
        )
        assert reload_res.status_code == 200
        loaded_ids = [r["ruleset_id"] for r in reload_res.json()["loaded_rulesets"]]
        assert "custom_audit_test" in loaded_ids

        # Immediately execute an evaluation with the dropped ruleset
        eval_res = client.post("/api/evaluate/plausibility", json={
            "instrument": {
                "manufacturer": "LiveDrop Test",
                "model": "LD-1",
                "serial_number": "SN-LD1",
                "accuracy_class": "III",
                "max_capacity": 4000.0,
                "min_capacity": 40.0,
                "verification_scale_interval_e": 2.0,
                "actual_scale_interval_d": 2.0,
                "unit": "g"
            },
            "ruleset_id": "custom_audit_test"
        })
        assert eval_res.status_code == 200
        assert eval_res.json()["is_valid"] is True
        assert int(float(eval_res.json()["allowed_n_max"])) == 8000
    finally:
        # Clean up dropped file
        if custom_ruleset_path.exists():
            custom_ruleset_path.unlink()
        # Reset registry
        ruleset_registry.reload()
