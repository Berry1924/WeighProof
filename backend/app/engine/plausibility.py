from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from app.engine.types import (
    InstrumentMasterData,
    AccuracyClass,
    DeviceType,
    PlausibilityCheckResult,
    PlausibilityEvaluation,
    Verdict,
)


UNIT_TO_GRAMS = {
    "mg": Decimal("0.001"),
    "g": Decimal("1.0"),
    "kg": Decimal("1000.0"),
    "t": Decimal("1000000.0"),
}


def to_grams(value: Decimal, unit: str) -> Decimal:
    u = unit.strip().lower()
    if u not in UNIT_TO_GRAMS:
        raise ValueError(f"Unsupported metrological unit '{unit}'. Allowed: mg, g, kg, t.")
    return value * UNIT_TO_GRAMS[u]


def is_valid_scale_interval_step(val: Decimal) -> bool:
    """Verifies that the scale interval belongs to {1, 2, 5} x 10^k."""
    if val <= 0:
        return False
    # Normalize decimal representation
    # e.g. 0.02 -> tuple: (sign, digits=(2,), exp=-2)
    tup = val.as_tuple()
    # Strip trailing zeroes from digits
    digits_str = "".join(str(d) for d in tup.digits).rstrip("0")
    return digits_str in {"1", "2", "5"}


def find_matching_classification_interval(
    e_in_grams: Decimal,
    class_def: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    intervals = class_def.get("classification_intervals", [])
    for interval in intervals:
        e_min = Decimal(str(interval["e_min_g"])) if interval.get("e_min_g") is not None else None
        e_max = Decimal(str(interval["e_max_g"])) if interval.get("e_max_g") is not None else None

        if e_min is not None and e_in_grams < e_min:
            continue
        if e_max is not None and e_in_grams > e_max:
            continue
        return interval
    return None


def evaluate_instrument_plausibility(
    instrument: InstrumentMasterData,
    ruleset: Dict[str, Any]
) -> PlausibilityEvaluation:
    checks: List[PlausibilityCheckResult] = []
    unit = instrument.unit.strip().lower()

    # 1. Unit Check
    valid_unit = unit in UNIT_TO_GRAMS
    checks.append(PlausibilityCheckResult(
        check_name="Unit Validity",
        clause="OIML R 76-1 Clause 2.1",
        passed=valid_unit,
        message=f"Unit '{instrument.unit}' is recognized and standard." if valid_unit else f"Unit '{instrument.unit}' is invalid. Must be mg, g, kg, or t.",
    ))
    if not valid_unit:
        return PlausibilityEvaluation(
            is_valid=False,
            calculated_n=Decimal(0),
            allowed_n_min=None,
            allowed_n_max=None,
            allowed_min_capacity=Decimal(0),
            checks=checks,
            summary_verdict=Verdict.FAIL
        )

    e = instrument.verification_scale_interval_e
    d = instrument.actual_scale_interval_d
    max_cap = instrument.max_capacity
    min_cap = instrument.min_capacity
    acc_class = instrument.accuracy_class.value

    # 2. Scale division sequence {1, 2, 5} x 10^k
    e_step_valid = is_valid_scale_interval_step(e)
    checks.append(PlausibilityCheckResult(
        check_name="Scale Division Step (e)",
        clause="OIML R 76-1 Clause 3.4.2 & 4.2.2.1",
        passed=e_step_valid,
        message=f"Verification scale interval e = {e} {unit} conforms to sequence {{1, 2, 5}} x 10^k."
        if e_step_valid else f"Scale interval e = {e} {unit} violates sequence {{1, 2, 5}} x 10^k."
    ))

    d_step_valid = is_valid_scale_interval_step(d)
    checks.append(PlausibilityCheckResult(
        check_name="Actual Scale Interval Step (d)",
        clause="OIML R 76-1 Clause 3.4.2 & 4.2.2.1",
        passed=d_step_valid,
        message=f"Actual scale interval d = {d} {unit} conforms to sequence {{1, 2, 5}} x 10^k."
        if d_step_valid else f"Scale interval d = {d} {unit} violates sequence {{1, 2, 5}} x 10^k."
    ))

    # 3. Relationship between e and d
    class_def = ruleset["accuracy_classes"].get(acc_class)
    if not class_def:
        raise ValueError(f"Accuracy class {acc_class} not found in ruleset {ruleset.get('ruleset_id')}")

    if instrument.device_type == DeviceType.GRADUATED_WITHOUT_AUX:
        ed_passed = (e == d)
        checks.append(PlausibilityCheckResult(
            check_name="Verification Scale Interval Equality (e = d)",
            clause="OIML R 76-1 Table 2",
            passed=ed_passed,
            message=f"Instrument without auxiliary device has e = d ({e} = {d} {unit})."
            if ed_passed else f"Graduated instrument without auxiliary device must have e = d (got e={e}, d={d})."
        ))
    elif instrument.device_type == DeviceType.GRADUATED_WITH_AUX:
        # Permitted only for classes I and II
        allowed_class = acc_class in {"I", "II"}
        if not allowed_class:
            checks.append(PlausibilityCheckResult(
                check_name="Auxiliary Device Class Restriction",
                clause="OIML R 76-1 Clause 3.4.1",
                passed=False,
                message=f"Auxiliary indicating devices are only permitted for Class I and II (instrument is Class {acc_class})."
            ))
        else:
            # Check d < e <= 10d, or special Class I d < 1mg rule
            d_grams = to_grams(d, unit)
            e_grams = to_grams(e, unit)
            if acc_class == "I" and d_grams < Decimal("0.001"):
                # Exception Table 5b: e = 1 mg = 0.001 g
                ed_rule_passed = (e_grams == Decimal("0.001") and d < e)
                msg = f"Class I with d < 1 mg has e = 1 mg (got d={d}{unit}, e={e}{unit})." if ed_rule_passed else f"Class I with d < 1 mg must have e = 1 mg."
            else:
                ed_rule_passed = (d < e) and (e <= Decimal(10) * d)
                msg = f"Auxiliary device relationship d < e <= 10d satisfied ({d} < {e} <= {10*d} {unit})." if ed_rule_passed else f"Auxiliary device must satisfy d < e <= 10d (got d={d}, e={e})."
            
            checks.append(PlausibilityCheckResult(
                check_name="Auxiliary Device Interval Ratio (d < e <= 10d)",
                clause="OIML R 76-1 Clause 3.4.2 & Table 5a/5b",
                passed=ed_rule_passed,
                message=msg
            ))

    # 4. Multi-interval check
    if instrument.is_multi_interval:
        if instrument.device_type == DeviceType.GRADUATED_WITH_AUX:
            checks.append(PlausibilityCheckResult(
                check_name="Multi-Interval Auxiliary Device Prohibition",
                clause="OIML R 76-1 Clause 3.4.1",
                passed=False,
                message="A multi-interval instrument shall not be fitted with an auxiliary indicating device."
            ))
        if instrument.partial_ranges:
            sorted_ranges = sorted(instrument.partial_ranges, key=lambda r: r.range_index)
            # Check strictly increasing e
            e_increasing = all(
                sorted_ranges[i].verification_scale_interval_e < sorted_ranges[i+1].verification_scale_interval_e
                for i in range(len(sorted_ranges) - 1)
            )
            checks.append(PlausibilityCheckResult(
                check_name="Multi-Interval Scale Interval Progression",
                clause="OIML R 76-1 Clause 3.3.1",
                passed=e_increasing,
                message="Partial ranges exhibit strictly increasing verification scale intervals e_1 < e_2 < ... < e_r."
                if e_increasing else "Partial ranges must have strictly increasing scale intervals e_i < e_{i+1}."
            ))
            # Check Table 4: Max_i / e_{i+1} >= threshold
            min_ratios = ruleset.get("multi_interval_rules", {}).get("min_ratio_max_to_next_e", {})
            req_ratio = Decimal(min_ratios.get(acc_class, 500))
            for i in range(len(sorted_ranges) - 1):
                r_curr = sorted_ranges[i]
                r_next = sorted_ranges[i+1]
                ratio = r_curr.max_capacity / r_next.verification_scale_interval_e
                ratio_ok = ratio >= req_ratio
                checks.append(PlausibilityCheckResult(
                    check_name=f"Multi-Interval Table 4 Ratio Range {r_curr.range_index}",
                    clause="OIML R 76-1 Clause 3.3.3 Table 4",
                    passed=ratio_ok,
                    message=f"Max_{r_curr.range_index} / e_{r_next.range_index} = {ratio} >= {req_ratio}."
                    if ratio_ok else f"Max_{r_curr.range_index} / e_{r_next.range_index} = {ratio} is below required minimum {req_ratio} for Class {acc_class}."
                ))

    # 5. Number of verification scale intervals n = Max / e (or n_i = Max_i / e_i for multi-interval)
    if instrument.is_multi_interval and instrument.partial_ranges:
        all_ranges_n_ok = True
        range_msgs = []
        calculated_n = max(r.max_capacity / r.verification_scale_interval_e for r in instrument.partial_ranges)
        allowed_n_min = None
        allowed_n_max = None
        for r in instrument.partial_ranges:
            ni = r.max_capacity / r.verification_scale_interval_e
            ei_grams = to_grams(r.verification_scale_interval_e, unit)
            interval_def_i = find_matching_classification_interval(ei_grams, class_def)
            if interval_def_i:
                n_min_i = Decimal(interval_def_i["n_min"]) if interval_def_i.get("n_min") is not None else None
                n_max_i = Decimal(interval_def_i["n_max"]) if interval_def_i.get("n_max") is not None else None
                if allowed_n_min is None or (n_min_i and n_min_i < allowed_n_min):
                    allowed_n_min = n_min_i
                if allowed_n_max is None or (n_max_i and n_max_i > allowed_n_max):
                    allowed_n_max = n_max_i
                ni_ok = (n_min_i is None or ni >= n_min_i) and (n_max_i is None or ni <= n_max_i)
                if not ni_ok:
                    all_ranges_n_ok = False
                    range_msgs.append(f"Range {r.range_index}: n_{r.range_index} = {ni} outside [{n_min_i}, {n_max_i}]")
                else:
                    range_msgs.append(f"Range {r.range_index}: n_{r.range_index} = {ni} OK")
            else:
                all_ranges_n_ok = False
                range_msgs.append(f"Range {r.range_index}: e = {r.verification_scale_interval_e} not matching Table 3")

        checks.append(PlausibilityCheckResult(
            check_name="Number of Scale Intervals (Multi-Interval n_i = Max_i/e_i)",
            clause="OIML R 76-1 Clause 3.3.1 & 3.3.2",
            passed=all_ranges_n_ok,
            message="; ".join(range_msgs)
        ))

        # Min capacity check for multi-interval: Min_1 >= allowed limit based on e_1
        first_r = sorted(instrument.partial_ranges, key=lambda r: r.range_index)[0]
        first_e_grams = to_grams(first_r.verification_scale_interval_e, unit)
        first_def = find_matching_classification_interval(first_e_grams, class_def)
        multiplier = Decimal(first_def["min_capacity_multiplier_e"]) if first_def else Decimal(20)
        if instrument.is_grading_instrument:
            multiplier = Decimal(5)
        allowed_min_cap = multiplier * first_r.verification_scale_interval_e
        min_cap_passed = (min_cap >= allowed_min_cap)
        checks.append(PlausibilityCheckResult(
            check_name="Minimum Capacity Lower Limit (Min_1)",
            clause="OIML R 76-1 Clause 3.3.2 Table 3",
            passed=min_cap_passed,
            message=f"Min capacity {min_cap} {unit} >= allowed lower limit {allowed_min_cap} {unit} ({multiplier} x e_1)."
            if min_cap_passed else f"Min capacity {min_cap} {unit} is below required minimum {allowed_min_cap} {unit}."
        ))
    else:
        calculated_n = max_cap / e
        e_grams = to_grams(e, unit)
        interval_def = find_matching_classification_interval(e_grams, class_def)

        if not interval_def:
            checks.append(PlausibilityCheckResult(
                check_name="Verification Scale Interval Range",
                clause="OIML R 76-1 Table 3",
                passed=False,
                message=f"Scale interval e = {e} {unit} ({e_grams} g) is outside all allowed intervals for Class {acc_class}."
            ))
            allowed_n_min = None
            allowed_n_max = None
            allowed_min_cap = Decimal(0)
        else:
            allowed_n_min = Decimal(interval_def["n_min"]) if interval_def.get("n_min") is not None else None
            allowed_n_max = Decimal(interval_def["n_max"]) if interval_def.get("n_max") is not None else None

            n_min_ok = (allowed_n_min is None) or (calculated_n >= allowed_n_min)
            n_max_ok = (allowed_n_max is None) or (calculated_n <= allowed_n_max)
            n_passed = n_min_ok and n_max_ok

            details_msg = f"n = {calculated_n} within [{allowed_n_min}, {allowed_n_max if allowed_n_max else 'unlimited'}] for Class {acc_class}."
            if not n_min_ok:
                details_msg = f"Calculated n = {calculated_n} is below minimum {allowed_n_min} for Class {acc_class}."
            elif not n_max_ok:
                details_msg = f"Calculated n = {calculated_n} exceeds maximum {allowed_n_max} for Class {acc_class}."

            checks.append(PlausibilityCheckResult(
                check_name="Number of Scale Intervals (n = Max/e)",
                clause="OIML R 76-1 Table 3",
                passed=n_passed,
                message=details_msg
            ))

            # 6. Minimum Capacity (Min) check
            multiplier = Decimal(interval_def["min_capacity_multiplier_e"])
            if instrument.is_grading_instrument:
                multiplier = Decimal(5)  # Clause 3.2 reduction for grading instruments

            # If auxiliary device, Min uses d instead of e (Clause 3.4.3)
            ref_division = d if instrument.device_type == DeviceType.GRADUATED_WITH_AUX else e
            allowed_min_cap = multiplier * ref_division

            min_cap_passed = (min_cap >= allowed_min_cap)
            checks.append(PlausibilityCheckResult(
                check_name="Minimum Capacity Lower Limit (Min)",
                clause="OIML R 76-1 Clause 3.2 & 3.4.3 Table 3",
                passed=min_cap_passed,
                message=f"Min capacity {min_cap} {unit} >= allowed lower limit {allowed_min_cap} {unit} ({multiplier} x {'d' if instrument.device_type == DeviceType.GRADUATED_WITH_AUX else 'e'})."
                if min_cap_passed else f"Min capacity {min_cap} {unit} is below required minimum {allowed_min_cap} {unit}."
            ))

    overall_passed = all(c.passed for c in checks)
    return PlausibilityEvaluation(
        is_valid=overall_passed,
        calculated_n=calculated_n,
        allowed_n_min=allowed_n_min,
        allowed_n_max=allowed_n_max,
        allowed_min_capacity=allowed_min_cap,
        checks=checks,
        summary_verdict=Verdict.PASS if overall_passed else Verdict.FAIL
    )
