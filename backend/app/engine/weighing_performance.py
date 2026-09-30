from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.engine.types import (
    AccuracyClass,
    InstrumentMasterData,
    WeighingDirection,
    Verdict,
)
from app.engine.mpe import calculate_mpe, MpeCalculationResult


class WeighingPointInput(BaseModel):
    direction: WeighingDirection
    load: Decimal
    indicated: Decimal
    delta_load: Optional[Decimal] = None
    remarks: Optional[str] = None

    @field_validator("load", "indicated", "delta_load", mode="before")
    def convert_to_decimal(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v


class WeighingPointResult(BaseModel):
    direction: WeighingDirection
    load: Decimal
    indicated: Decimal
    delta_load: Optional[Decimal]
    turning_indication_p: Decimal
    uncorrected_error_e: Decimal
    corrected_error_ec: Decimal
    mpe: Decimal
    mpe_details: MpeCalculationResult
    verdict: Verdict
    explanation: str


class WeighingPerformanceEvaluation(BaseModel):
    initial_zero_error_e0: Decimal
    points: List[WeighingPointResult]
    overall_verdict: Verdict
    max_corrected_error: Decimal
    worst_case_margin_to_mpe: Decimal
    summary_explanation: str


def evaluate_weighing_performance(
    instrument: InstrumentMasterData,
    points_input: List[WeighingPointInput],
    ruleset: Dict[str, Any],
    initial_zero_error_e0: Optional[Decimal] = None,
    is_in_service: bool = False
) -> WeighingPerformanceEvaluation:
    if not points_input:
        raise ValueError("Cannot evaluate empty weighing performance test points.")

    e = instrument.verification_scale_interval_e
    d = instrument.actual_scale_interval_d
    unit = instrument.unit.strip().lower()

    # Determine E0 (zero error) if not provided explicitly:
    # Check if the first point is at load = 0
    calculated_e0 = initial_zero_error_e0
    if calculated_e0 is None:
        first_pt = points_input[0]
        if first_pt.load == Decimal(0):
            if first_pt.delta_load is not None:
                p_zero = first_pt.indicated + (Decimal("0.5") * e) - first_pt.delta_load
                calculated_e0 = p_zero - first_pt.load
            else:
                calculated_e0 = first_pt.indicated - first_pt.load
        else:
            calculated_e0 = Decimal(0)

    evaluated_points: List[WeighingPointResult] = []
    overall_pass = True
    worst_margin = Decimal("999999999")
    max_abs_ec = Decimal(0)

    for pt in points_input:
        # Determine P and E
        if pt.delta_load is not None:
            # Changeover formula: P = I + 0.5e - delta_L
            p = pt.indicated + (Decimal("0.5") * e) - pt.delta_load
            e_uncorr = p - pt.load
            formula_note = f"P = {pt.indicated} + 0.5*{e} - {pt.delta_load} = {p} {unit}, E = P - L = {e_uncorr} {unit}"
        else:
            # High-resolution auxiliary mode or digital when d <= 0.2e
            p = pt.indicated
            e_uncorr = pt.indicated - pt.load
            formula_note = f"Direct indication P = {p} {unit}, E = I - L = {e_uncorr} {unit}"

        # Corrected error: Ec = E - E0
        ec = e_uncorr - calculated_e0
        abs_ec = abs(ec)
        if abs_ec > max_abs_ec:
            max_abs_ec = abs_ec

        # Calculate MPE
        mpe_res = calculate_mpe(pt.load, instrument, ruleset, is_in_service=is_in_service)
        mpe_val = mpe_res.mpe_value

        point_pass = abs_ec <= mpe_val
        if not point_pass:
            overall_pass = False

        margin = mpe_val - abs_ec
        if margin < worst_margin:
            worst_margin = margin

        status_str = "PASS" if point_pass else "FAIL"
        explain_str = (
            f"Direction: {pt.direction.value.capitalize()}, Load L = {pt.load} {unit}. "
            f"{formula_note}. With zero error E0 = {calculated_e0} {unit} -> "
            f"Corrected error Ec = E - E0 = {ec} {unit}. "
            f"MPE at this load is +/- {mpe_val} {unit}. "
            f"Criterion |Ec| <= |mpe|: |{ec}| <= {mpe_val} -> {status_str} (OIML R 76-1 Clause A.4.4.3)."
        )

        evaluated_points.append(WeighingPointResult(
            direction=pt.direction,
            load=pt.load,
            indicated=pt.indicated,
            delta_load=pt.delta_load,
            turning_indication_p=p,
            uncorrected_error_e=e_uncorr,
            corrected_error_ec=ec,
            mpe=mpe_val,
            mpe_details=mpe_res,
            verdict=Verdict.PASS if point_pass else Verdict.FAIL,
            explanation=explain_str
        ))

    summary = (
        f"Weighing Performance evaluation completed ({len(evaluated_points)} points). "
        f"Initial zero error E0 = {calculated_e0} {unit}. "
        f"Max |Ec| observed = {max_abs_ec} {unit}. "
        f"Smallest margin to MPE = {worst_margin} {unit}. "
        f"Overall test verdict: {'PASS' if overall_pass else 'FAIL'}."
    )

    return WeighingPerformanceEvaluation(
        initial_zero_error_e0=calculated_e0,
        points=evaluated_points,
        overall_verdict=Verdict.PASS if overall_pass else Verdict.FAIL,
        max_corrected_error=max_abs_ec,
        worst_case_margin_to_mpe=worst_margin,
        summary_explanation=summary
    )
