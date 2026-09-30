import pytest
from decimal import Decimal
import json
from pathlib import Path

from app.engine.types import (
    AccuracyClass,
    InstrumentMasterData,
    Verdict,
)
from app.engine.ruleset import ruleset_registry
from app.engine.eccentricity import (
    EccentricityPositionInput,
    calculate_recommended_eccentricity_load,
    evaluate_eccentricity,
)
from app.engine.repeatability import (
    RepeatabilityRunInput,
    evaluate_repeatability_series,
    evaluate_repeatability,
)
from app.engine.pluggable_tests import (
    DiscriminationPointInput,
    evaluate_discrimination,
    ZeroReturnInput,
    evaluate_zero_return,
)


@pytest.fixture
def ruleset_2006():
    return ruleset_registry.get_ruleset("oiml_r76_2006")


@pytest.fixture
def oracle_6kg_data():
    oracle_path = Path(__file__).resolve().parents[2] / "docs" / "oracle" / "oracle_class_iii_6kg.json"
    with open(oracle_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_eccentricity_oracle_exact_match(ruleset_2006, oracle_6kg_data):
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
        points_of_support=inst_data["points_of_support"]
    )

    # Check recommended load
    rec_load = calculate_recommended_eccentricity_load(instrument)
    assert rec_load == Decimal("2000.0")

    ecc_oracle = oracle_6kg_data["tests"]["eccentricity"]
    pos_inputs = [
        EccentricityPositionInput(
            position_id=p["position_id"],
            description=p["description"],
            load=Decimal(str(p["load"])),
            indicated=Decimal(str(p["indicated"])),
            delta_load=Decimal(str(p["delta_load"])) if p.get("delta_load") is not None else None
        )
        for p in ecc_oracle["positions"]
    ]

    result = evaluate_eccentricity(
        instrument=instrument,
        positions_input=pos_inputs,
        ruleset=ruleset_2006,
        initial_zero_error_e0=Decimal("0.2")
    )

    assert result.overall_verdict == Verdict.PASS
    assert len(result.positions) == 5

    for evaluated, expected in zip(result.positions, ecc_oracle["positions"]):
        assert evaluated.turning_indication_p == Decimal(str(expected["expected_p"]))
        assert evaluated.uncorrected_error_e == Decimal(str(expected["expected_error"]))
        assert evaluated.corrected_error_ec == Decimal(str(expected["expected_corrected_error"]))
        assert evaluated.mpe == Decimal(str(expected["expected_mpe"]))
        assert evaluated.verdict.value == expected["expected_verdict"]


def test_eccentricity_deliberate_failure(ruleset_2006):
    instrument = InstrumentMasterData(
        manufacturer="Acme",
        model="EccFail",
        serial_number="SN-ECC-FAIL",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g",
        points_of_support=4
    )

    # Position 3 exceeds MPE (2.0g) with Ec = +2.3g
    pos = [
        EccentricityPositionInput(position_id="pos_1", description="Corner 1", load=Decimal("2000"), indicated=Decimal("2000"), delta_load=Decimal("1.0")),
        EccentricityPositionInput(position_id="pos_3", description="Corner 3", load=Decimal("2000"), indicated=Decimal("2002"), delta_load=Decimal("0.7")),
    ]

    res = evaluate_eccentricity(instrument, pos, ruleset_2006, initial_zero_error_e0=Decimal("0"))
    assert res.overall_verdict == Verdict.FAIL
    assert res.positions[1].verdict == Verdict.FAIL
    assert res.positions[1].corrected_error_ec == Decimal("2.3")
    assert res.positions[1].mpe == Decimal("2.0")


def test_repeatability_oracle_exact_match(ruleset_2006, oracle_6kg_data):
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

    series_data = oracle_6kg_data["tests"]["repeatability"]["series_1"]
    runs = [
        RepeatabilityRunInput(
            run_number=r["run"],
            load=Decimal(str(r["load"])),
            indicated=Decimal(str(r["indicated"])),
            delta_load=Decimal(str(r["delta_load"])) if r.get("delta_load") is not None else None
        )
        for r in series_data["runs"]
    ]

    res = evaluate_repeatability_series("Series 1 (50% Max)", runs, instrument, ruleset_2006)
    assert res.overall_series_verdict == Verdict.PASS
    assert res.individual_errors_verdict == Verdict.PASS
    assert res.spread_verdict == Verdict.PASS
    assert res.e_max == Decimal(str(series_data["expected_e_max"]))
    assert res.e_min == Decimal(str(series_data["expected_e_min"]))
    assert res.spread_delta_e == Decimal(str(series_data["expected_range"]))


def test_repeatability_deliberate_spread_failure(ruleset_2006):
    instrument = InstrumentMasterData(
        manufacturer="Acme",
        model="RepFail",
        serial_number="SN-REP-FAIL",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g"
    )

    # Errors range from -0.8 to +1.7 -> spread = 2.5g > MPE (2.0g) -> FAIL
    errors = [Decimal("0.2"), Decimal("0.5"), Decimal("-0.8"), Decimal("1.2"), Decimal("1.7")]
    runs = [
        # To get error e, P = 3000 + e. delta_load = 0.5e - e = 1.0 - err
        RepeatabilityRunInput(
            run_number=i+1,
            load=Decimal("3000"),
            indicated=Decimal("3000"),
            delta_load=Decimal("1.0") - err
        )
        for i, err in enumerate(errors)
    ]

    res = evaluate_repeatability_series("Spread Test", runs, instrument, ruleset_2006)
    assert res.spread_delta_e == Decimal("2.5")
    assert res.mpe == Decimal("2.0")
    assert res.spread_verdict == Verdict.FAIL
    assert res.overall_series_verdict == Verdict.FAIL


def test_discrimination_evaluation(ruleset_2006):
    instrument = InstrumentMasterData(
        manufacturer="Acme",
        model="Discrim",
        serial_number="SN-DISC",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g"
    )

    # With d = 2g, 1.4d = 2.8g. Indication should change from 2000 to 2002.
    pts = [
        DiscriminationPointInput(load=Decimal("2000"), initial_indication_i=Decimal("2000"), indication_after_1_4d=Decimal("2002")),
        DiscriminationPointInput(load=Decimal("6000"), initial_indication_i=Decimal("6000"), indication_after_1_4d=Decimal("6002")),
    ]
    res = evaluate_discrimination(instrument, pts, ruleset_2006)
    assert res.overall_verdict == Verdict.PASS


def test_zero_return_evaluation(ruleset_2006):
    instrument = InstrumentMasterData(
        manufacturer="Acme",
        model="ZeroRet",
        serial_number="SN-ZR",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g"
    )

    # e = 2g. Allowed 30m drift <= 0.5e = 1.0g.
    # Case 1: pass (|0.6| <= 1.0)
    input_pass = ZeroReturnInput(
        test_load_near_max=Decimal("6000"),
        zero_indication_initial_p0=Decimal("0.0"),
        zero_indication_after_30m_p30=Decimal("0.6")
    )
    res_pass = evaluate_zero_return(instrument, input_pass, ruleset_2006)
    assert res_pass.overall_verdict == Verdict.PASS
    assert res_pass.delta_p30_p0 == Decimal("0.6")

    # Case 2: fail (|1.4| > 1.0)
    input_fail = ZeroReturnInput(
        test_load_near_max=Decimal("6000"),
        zero_indication_initial_p0=Decimal("0.0"),
        zero_indication_after_30m_p30=Decimal("1.4")
    )
    res_fail = evaluate_zero_return(instrument, input_fail, ruleset_2006)
    assert res_fail.overall_verdict == Verdict.FAIL
