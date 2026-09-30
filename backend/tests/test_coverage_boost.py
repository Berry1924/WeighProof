import pytest
from decimal import Decimal
import tempfile
from pathlib import Path

from app.engine.types import (
    AccuracyClass,
    DeviceType,
    InstrumentMasterData,
    PartialWeighingRange,
    WeighingDirection,
    Verdict,
)
from app.engine.ruleset import RulesetRegistry, ruleset_registry
from app.engine.plausibility import evaluate_instrument_plausibility, to_grams
from app.engine.mpe import calculate_mpe
from app.engine.weighing_performance import (
    WeighingPointInput,
    evaluate_weighing_performance,
)
from app.engine.eccentricity import (
    EccentricityPositionInput,
    calculate_recommended_eccentricity_load,
    evaluate_eccentricity,
)
from app.engine.repeatability import (
    RepeatabilityRunInput,
    evaluate_repeatability,
)
from app.engine.pluggable_tests import (
    DiscriminationPointInput,
    evaluate_discrimination,
    ZeroReturnInput,
    evaluate_zero_return,
)


def test_multi_interval_plausibility_and_mpe():
    ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
    # Multi-interval Class III instrument (from OIML R 76-1 Clause 3.3.3 example):
    # Max = 15 kg, e1 = 1g (up to 2kg), e2 = 2g (up to 5kg), e3 = 10g (up to 15kg)
    ranges = [
        PartialWeighingRange(range_index=1, max_capacity=Decimal("2000"), verification_scale_interval_e=Decimal("1")),
        PartialWeighingRange(range_index=2, max_capacity=Decimal("5000"), verification_scale_interval_e=Decimal("2")),
        PartialWeighingRange(range_index=3, max_capacity=Decimal("15000"), verification_scale_interval_e=Decimal("10")),
    ]
    inst = InstrumentMasterData(
        manufacturer="Bizerba",
        model="Multi-15",
        serial_number="SN-MI-01",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("15000"),
        min_capacity=Decimal("20"),
        verification_scale_interval_e=Decimal("1"),
        actual_scale_interval_d=Decimal("1"),
        unit="g",
        is_multi_interval=True,
        partial_ranges=ranges
    )

    eval_res = evaluate_instrument_plausibility(inst, ruleset)
    assert eval_res.is_valid is True

    # Test MPE at different partial ranges (matching 3.3.3 example)
    # m = 400g (range 1: 400 e1 <= 500 e1 -> 0.5 e1 = 0.5g)
    mpe_400 = calculate_mpe(Decimal("400"), inst, ruleset)
    assert mpe_400.mpe_value == Decimal("0.5")

    # m = 2100g (range 2: 2100 / 2 = 1050 e2. 500 < m <= 2000 -> 1.0 e2 = 2.0g)
    mpe_2100 = calculate_mpe(Decimal("2100"), inst, ruleset)
    assert mpe_2100.mpe_value == Decimal("2.0")

    # m = 5100g (range 3: 5100 / 10 = 510 e3. 500 < m <= 2000 -> 1.0 e3 = 10.0g)
    mpe_5100 = calculate_mpe(Decimal("5100"), inst, ruleset)
    assert mpe_5100.mpe_value == Decimal("10.0")


def test_auxiliary_device_plausibility():
    ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
    # Class II instrument with auxiliary device: d = 0.01 g, e = 0.1 g (e = 10d)
    inst_class_ii = InstrumentMasterData(
        manufacturer="Mettler",
        model="AuxBalance",
        serial_number="SN-AUX-01",
        accuracy_class=AccuracyClass.CLASS_II,
        max_capacity=Decimal("600"),
        min_capacity=Decimal("2"),  # Min = 20 d = 20 * 0.01 = 0.2g -> 2g is fine
        verification_scale_interval_e=Decimal("0.1"),
        actual_scale_interval_d=Decimal("0.01"),
        unit="g",
        device_type=DeviceType.GRADUATED_WITH_AUX
    )
    res = evaluate_instrument_plausibility(inst_class_ii, ruleset)
    assert res.is_valid is True

    # Illegal: Class III with auxiliary device
    inst_class_iii_bad = InstrumentMasterData(
        manufacturer="Bad",
        model="AuxClassIII",
        serial_number="SN-BAD",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("0.2"),
        unit="g",
        device_type=DeviceType.GRADUATED_WITH_AUX
    )
    res_bad = evaluate_instrument_plausibility(inst_class_iii_bad, ruleset)
    assert res_bad.is_valid is False
    assert any("Auxiliary Device Class Restriction" in c.check_name for c in res_bad.checks if not c.passed)


def test_dynamic_ruleset_registration():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg = RulesetRegistry(rulesets_dir=Path(tmpdir))
        sample_ruleset = {
            "ruleset_id": "test_ruleset_2026",
            "edition": "2026 Test",
            "title": "Custom Test Standard",
            "rounding_mode": "ROUND_HALF_UP",
            "in_service_mpe_multiplier": 2.0,
            "accuracy_classes": ruleset_registry.get_ruleset("oiml_r76_2006")["accuracy_classes"],
            "multi_interval_rules": ruleset_registry.get_ruleset("oiml_r76_2006")["multi_interval_rules"],
            "eccentricity_rules": ruleset_registry.get_ruleset("oiml_r76_2006")["eccentricity_rules"],
            "repeatability_rules": ruleset_registry.get_ruleset("oiml_r76_2006")["repeatability_rules"],
        }
        r_id = reg.register_ruleset(sample_ruleset, save_to_disk=True)
        assert r_id == "test_ruleset_2026"
        loaded = reg.get_ruleset("test_ruleset_2026")
        assert loaded["title"] == "Custom Test Standard"
        listed = reg.list_rulesets()
        assert any(item["ruleset_id"] == "test_ruleset_2026" for item in listed)


def test_eccentricity_more_than_4_supports_and_per_position_zero():
    ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
    inst = InstrumentMasterData(
        manufacturer="Avery",
        model="Weighbridge-30t",
        serial_number="SN-WB-01",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("30000"),
        min_capacity=Decimal("200"),
        verification_scale_interval_e=Decimal("10"),
        actual_scale_interval_d=Decimal("10"),
        unit="kg",
        points_of_support=6  # 6 load cells -> load = 1/(6-1) * 30000 = 6000 kg
    )
    rec_load = calculate_recommended_eccentricity_load(inst)
    assert rec_load == Decimal("6000")

    pos = [
        EccentricityPositionInput(
            position_id="cell_1",
            description="Support point 1",
            load=Decimal("6000"),
            indicated=Decimal("6000"),
            delta_load=Decimal("5"),
            zero_load_indicated=Decimal("0"),
            zero_delta_load=Decimal("5")
        )
    ]
    res = evaluate_eccentricity(inst, pos, ruleset)
    assert res.overall_verdict == Verdict.PASS


def test_repeatability_multi_series():
    ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
    inst = InstrumentMasterData(
        manufacturer="Acme",
        model="Scale",
        serial_number="SN-REP",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("6000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g"
    )

    series_data = {
        "50% Max": [
            RepeatabilityRunInput(run_number=1, load=Decimal("3000"), indicated=Decimal("3000")),
            RepeatabilityRunInput(run_number=2, load=Decimal("3000"), indicated=Decimal("3000")),
            RepeatabilityRunInput(run_number=3, load=Decimal("3000"), indicated=Decimal("3000")),
        ],
        "100% Max": [
            RepeatabilityRunInput(run_number=1, load=Decimal("6000"), indicated=Decimal("6000")),
            RepeatabilityRunInput(run_number=2, load=Decimal("6000"), indicated=Decimal("6000")),
            RepeatabilityRunInput(run_number=3, load=Decimal("6000"), indicated=Decimal("6000")),
        ]
    }
    eval_rep = evaluate_repeatability(inst, series_data, ruleset)
    assert eval_rep.overall_verdict == Verdict.PASS
    assert len(eval_rep.series_evaluations) == 2


def test_zero_return_multi_interval():
    ruleset = ruleset_registry.get_ruleset("oiml_r76_2006")
    inst = InstrumentMasterData(
        manufacturer="Mettler",
        model="MI",
        serial_number="1",
        accuracy_class=AccuracyClass.CLASS_III,
        max_capacity=Decimal("15000"),
        min_capacity=Decimal("40"),
        verification_scale_interval_e=Decimal("2"),
        actual_scale_interval_d=Decimal("2"),
        unit="g",
        is_multi_interval=True,
        partial_ranges=[
            PartialWeighingRange(range_index=1, max_capacity=Decimal("5000"), verification_scale_interval_e=Decimal("2")),
            PartialWeighingRange(range_index=2, max_capacity=Decimal("15000"), verification_scale_interval_e=Decimal("5")),
        ]
    )

    inp = ZeroReturnInput(
        test_load_near_max=Decimal("15000"),
        zero_indication_initial_p0=Decimal("0.0"),
        zero_indication_after_30m_p30=Decimal("0.5"),
        zero_indication_after_35m_p35=Decimal("0.8")
    )
    res = evaluate_zero_return(inst, inp, ruleset)
    assert res.overall_verdict == Verdict.PASS
    assert res.change_35m_verdict == Verdict.PASS
