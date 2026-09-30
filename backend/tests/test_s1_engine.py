import pytest
from decimal import Decimal
import json
from pathlib import Path

from app.engine.types import (
    AccuracyClass,
    DeviceType,
    InstrumentMasterData,
    WeighingDirection,
    Verdict,
)
from app.engine.ruleset import ruleset_registry
from app.engine.plausibility import evaluate_instrument_plausibility
from app.engine.mpe import calculate_mpe
from app.engine.weighing_performance import (
    WeighingPointInput,
    evaluate_weighing_performance,
)


@pytest.fixture
def ruleset_2006():
    return ruleset_registry.get_ruleset("oiml_r76_2006")


@pytest.fixture
def ruleset_1992():
    return ruleset_registry.get_ruleset("oiml_r76_1992")


@pytest.fixture
def oracle_6kg_data():
    oracle_path = Path(__file__).resolve().parents[2] / "docs" / "oracle" / "oracle_class_iii_6kg.json"
    with open(oracle_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ruleset_registry_loads_both_editions(ruleset_2006, ruleset_1992):
    assert ruleset_2006["ruleset_id"] == "oiml_r76_2006"
    assert ruleset_2006["edition"] == "2006 (E)"
    assert ruleset_1992["ruleset_id"] == "oiml_r76_1992"
    assert ruleset_1992["edition"] == "1992 (E)"
    classes = ["I", "II", "III", "IIII"]
    for c in classes:
        assert c in ruleset_2006["accuracy_classes"]
        assert c in ruleset_1992["accuracy_classes"]


def test_plausibility_oracle_class_iii_6kg(ruleset_2006, oracle_6kg_data):
    inst_data = oracle_6kg_data["instrument"]
    instrument = InstrumentMasterData(
        manufacturer=inst_data["manufacturer"],
        model=inst_data["model"],
        serial_number=inst_data["serial_number"],
        accuracy_class=AccuracyClass(inst_data["accuracy_class"]),
        max_capacity=Decimal(str(inst_data["max_capacity"])),
        min_capacity=Decimal(str(inst_data["min_capacity"])),
        verification_scale_interval_e=Decimal(str(inst_data["verification_scale_interval_e"])),
        actual_scale_interval_d=Decimal(str(inst_data["actual_scale_interval_d"])),
        unit=inst_data["unit"],
        device_type=DeviceType(inst_data["device_type"]),
        points_of_support=inst_data["points_of_support"],
        is_multi_interval=inst_data["is_multi_interval"],
    )

    result = evaluate_instrument_plausibility(instrument, ruleset_2006)
    assert result.is_valid is True
    assert result.summary_verdict == Verdict.PASS
    assert result.calculated_n == Decimal("3000")
    assert result.allowed_min_capacity == Decimal("40.0")
    assert result.allowed_n_min == Decimal("100")
    assert result.allowed_n_max == Decimal("10000")


def test_plausibility_rejections(ruleset_2006):
    # Test 1: Invalid scale division step e = 3 g
    bad_step_inst = InstrumentMasterData(
        manufacturer="Acme",
        model="BadStep",
        serial_number="SN-01",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("60"),
        verification_scale_interval_e=Decimal("3"),  # invalid!
        actual_scale_interval_d=Decimal("3"),
        unit="g"
    )
    res1 = evaluate_instrument_plausibility(bad_step_inst, ruleset_2006)
    assert res1.is_valid is False
    assert any(c.check_name == "Scale Division Step (e)" and not c.passed for c in res1.checks)

    # Test 2: n exceeds limit (Class III n > 10,000)
    over_n_inst = InstrumentMasterData(
        manufacturer="Acme",
        model="OverN",
        serial_number="SN-02",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("15000"),
        min_capacity=Decimal("20"),
        verification_scale_interval_e=Decimal("1"),
        actual_scale_interval_d=Decimal("1"),
        unit="g"
    )
    res2 = evaluate_instrument_plausibility(over_n_inst, ruleset_2006)
    assert res2.is_valid is False
    assert any("exceeds maximum" in c.message for c in res2.checks if not c.passed)

    # Test 3: Min below 20e
    low_min_inst = InstrumentMasterData(
        manufacturer="Acme",
        model="LowMin",
        serial_number="SN-03",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("10"),  # min is 40g (20e)
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g"
    )
    res3 = evaluate_instrument_plausibility(low_min_inst, ruleset_2006)
    assert res3.is_valid is False
    assert any(c.check_name.startswith("Minimum Capacity") and not c.passed for c in res3.checks)


def test_mpe_calculation_across_bands(ruleset_2006):
    inst = InstrumentMasterData(
        manufacturer="Test",
        model="T1",
        serial_number="1",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g"
    )

    # Band 1: 0 to 500e (0 to 1000g) -> MPE = 0.5e = 1.0g
    mpe_40 = calculate_mpe(Decimal("40"), inst, ruleset_2006)
    assert mpe_40.mpe_multiplier_e == Decimal("0.5")
    assert mpe_40.mpe_value == Decimal("1.0")

    mpe_1000 = calculate_mpe(Decimal("1000"), inst, ruleset_2006)
    assert mpe_1000.mpe_multiplier_e == Decimal("0.5")
    assert mpe_1000.mpe_value == Decimal("1.0")

    # Band 2: 500e < m <= 2000e (1000g < m <= 4000g) -> MPE = 1.0e = 2.0g
    mpe_2000 = calculate_mpe(Decimal("2000"), inst, ruleset_2006)
    assert mpe_2000.mpe_multiplier_e == Decimal("1.0")
    assert mpe_2000.mpe_value == Decimal("2.0")

    mpe_4000 = calculate_mpe(Decimal("4000"), inst, ruleset_2006)
    assert mpe_4000.mpe_multiplier_e == Decimal("1.0")
    assert mpe_4000.mpe_value == Decimal("2.0")

    # Band 3: 2000e < m <= 10000e (4000g < m <= 6000g) -> MPE = 1.5e = 3.0g
    mpe_5000 = calculate_mpe(Decimal("5000"), inst, ruleset_2006)
    assert mpe_5000.mpe_multiplier_e == Decimal("1.5")
    assert mpe_5000.mpe_value == Decimal("3.0")

    mpe_6000 = calculate_mpe(Decimal("6000"), inst, ruleset_2006)
    assert mpe_6000.mpe_multiplier_e == Decimal("1.5")
    assert mpe_6000.mpe_value == Decimal("3.0")


def test_weighing_performance_oracle_exact_match(ruleset_2006, oracle_6kg_data):
    inst_data = oracle_6kg_data["instrument"]
    instrument = InstrumentMasterData(
        manufacturer=inst_data["manufacturer"],
        model=inst_data["model"],
        serial_number=inst_data["serial_number"],
        accuracy_class=AccuracyClass(inst_data["accuracy_class"]),
        max_capacity=Decimal(str(inst_data["max_capacity"])),
        min_capacity=Decimal(str(inst_data["min_capacity"])),
        verification_scale_interval_e=Decimal(str(inst_data["verification_scale_interval_e"])),
        actual_scale_interval_d=Decimal(str(inst_data["actual_scale_interval_d"])),
        unit=inst_data["unit"],
    )

    oracle_pts = oracle_6kg_data["tests"]["weighing_performance"]["points"]
    pts_input = [
        WeighingPointInput(
            direction=WeighingDirection(p["direction"]),
            load=Decimal(str(p["load"])),
            indicated=Decimal(str(p["indicated"])),
            delta_load=Decimal(str(p["delta_load"])) if p.get("delta_load") is not None else None
        )
        for p in oracle_pts
    ]

    result = evaluate_weighing_performance(
        instrument=instrument,
        points_input=pts_input,
        ruleset=ruleset_2006,
        initial_zero_error_e0=Decimal("0.2")
    )

    assert result.overall_verdict == Verdict.PASS
    assert len(result.points) == len(oracle_pts)

    for evaluated, expected in zip(result.points, oracle_pts):
        assert evaluated.turning_indication_p == Decimal(str(expected["expected_p"]))
        assert evaluated.uncorrected_error_e == Decimal(str(expected["expected_error"]))
        assert evaluated.corrected_error_ec == Decimal(str(expected["expected_corrected_error"]))
        assert evaluated.mpe == Decimal(str(expected["expected_mpe"]))
        assert evaluated.verdict.value == expected["expected_verdict"]


def test_weighing_performance_deliberate_failure(ruleset_2006):
    instrument = InstrumentMasterData(
        manufacturer="Dibal S.A.",
        model="CS-6000",
        serial_number="SN-FAIL-01",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g",
    )

    pts = [
        WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("0"), indicated=Decimal("0"), delta_load=Decimal("1.0")),
        # At 4000g, indicated = 4002g, delta_load = 0.6g -> P = 4002.4, E = +2.4, Ec = +2.4g > MPE (2.0g) -> FAIL!
        WeighingPointInput(direction=WeighingDirection.INCREASING, load=Decimal("4000"), indicated=Decimal("4002"), delta_load=Decimal("0.6")),
    ]

    res = evaluate_weighing_performance(instrument, pts, ruleset_2006)
    assert res.overall_verdict == Verdict.FAIL
    assert res.points[1].verdict == Verdict.FAIL
    assert res.points[1].corrected_error_ec == Decimal("2.4")
    assert res.points[1].mpe == Decimal("2.0")
    assert "FAIL" in res.points[1].explanation
