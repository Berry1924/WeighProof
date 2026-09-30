from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.engine.types import (
    InstrumentMasterData,
    Verdict,
)
from app.engine.mpe import calculate_mpe, MpeCalculationResult


class EccentricityPositionInput(BaseModel):
    position_id: str
    description: str
    load: Decimal
    indicated: Decimal
    delta_load: Optional[Decimal] = None
    zero_load_indicated: Optional[Decimal] = None
    zero_delta_load: Optional[Decimal] = None
    remarks: Optional[str] = None

    @field_validator("load", "indicated", "delta_load", "zero_load_indicated", "zero_delta_load", mode="before")
    def convert_to_decimal(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v


class EccentricityPositionResult(BaseModel):
    position_id: str
    description: str
    load: Decimal
    indicated: Decimal
    delta_load: Optional[Decimal]
    turning_indication_p: Decimal
    uncorrected_error_e: Decimal
    zero_error_e0_used: Decimal
    corrected_error_ec: Decimal
    mpe: Decimal
    verdict: Verdict
    explanation: str


class EccentricityEvaluation(BaseModel):
    recommended_test_load: Decimal
    actual_test_load: Decimal
    initial_zero_error_e0: Decimal
    positions: List[EccentricityPositionResult]
    overall_verdict: Verdict
    max_corrected_error: Decimal
    summary_explanation: str


def calculate_recommended_eccentricity_load(instrument: InstrumentMasterData) -> Decimal:
    """
    Computes required eccentricity load according to OIML R 76-1 Clause 3.6.2:
    - n <= 4 points of support: 1/3 Max
    - n > 4 points of support: 1/(n-1) Max
    """
    max_cap = instrument.max_capacity
    n_supports = instrument.points_of_support
    if n_supports <= 4:
        return (max_cap / Decimal(3)).quantize(instrument.verification_scale_interval_e)
    else:
        divisor = Decimal(n_supports - 1)
        return (max_cap / divisor).quantize(instrument.verification_scale_interval_e)


def evaluate_eccentricity(
    instrument: InstrumentMasterData,
    positions_input: List[EccentricityPositionInput],
    ruleset: Dict[str, Any],
    initial_zero_error_e0: Decimal = Decimal(0),
    is_in_service: bool = False
) -> EccentricityEvaluation:
    if not positions_input:
        raise ValueError("Cannot evaluate empty eccentricity positions.")

    e = instrument.verification_scale_interval_e
    unit = instrument.unit.strip().lower()
    rec_load = calculate_recommended_eccentricity_load(instrument)
    actual_test_load = positions_input[0].load

    evaluated_positions: List[EccentricityPositionResult] = []
    overall_pass = True
    max_abs_ec = Decimal(0)

    for pos in positions_input:
        # Determine local zero error if provided per position (Clause A.4.7)
        if pos.zero_load_indicated is not None:
            if pos.zero_delta_load is not None:
                p_zero = pos.zero_load_indicated + (Decimal("0.5") * e) - pos.zero_delta_load
                e0_pos = p_zero
            else:
                e0_pos = pos.zero_load_indicated
        else:
            e0_pos = initial_zero_error_e0

        # Determine P and E
        if pos.delta_load is not None:
            p = pos.indicated + (Decimal("0.5") * e) - pos.delta_load
            e_uncorr = p - pos.load
            formula_note = f"P = {pos.indicated} + 0.5*{e} - {pos.delta_load} = {p} {unit}, E = {e_uncorr} {unit}"
        else:
            p = pos.indicated
            e_uncorr = pos.indicated - pos.load
            formula_note = f"P = {p} {unit}, E = I - L = {e_uncorr} {unit}"

        # Corrected error: Ec = E - E0
        ec = e_uncorr - e0_pos
        abs_ec = abs(ec)
        if abs_ec > max_abs_ec:
            max_abs_ec = abs_ec

        # Calculate MPE for this position's load
        mpe_res = calculate_mpe(pos.load, instrument, ruleset, is_in_service=is_in_service)
        mpe_val = mpe_res.mpe_value

        pos_pass = abs_ec <= mpe_val
        if not pos_pass:
            overall_pass = False

        status_str = "PASS" if pos_pass else "FAIL"
        explain_str = (
            f"Location '{pos.description}' ({pos.position_id}): Load L = {pos.load} {unit}. "
            f"{formula_note}. Zero error E0 used = {e0_pos} {unit} -> "
            f"Corrected error Ec = {ec} {unit}. "
            f"MPE at this load is +/- {mpe_val} {unit}. "
            f"Criterion |Ec| <= |mpe|: |{ec}| <= {mpe_val} -> {status_str} (OIML R 76-1 Clause 3.6.2 & A.4.7)."
        )

        evaluated_positions.append(EccentricityPositionResult(
            position_id=pos.position_id,
            description=pos.description,
            load=pos.load,
            indicated=pos.indicated,
            delta_load=pos.delta_load,
            turning_indication_p=p,
            uncorrected_error_e=e_uncorr,
            zero_error_e0_used=e0_pos,
            corrected_error_ec=ec,
            mpe=mpe_val,
            verdict=Verdict.PASS if pos_pass else Verdict.FAIL,
            explanation=explain_str
        ))

    summary = (
        f"Eccentricity test evaluated across {len(evaluated_positions)} positions. "
        f"Recommended load: {rec_load} {unit} (actual applied: {actual_test_load} {unit}). "
        f"Max |Ec| observed = {max_abs_ec} {unit}. "
        f"Overall test verdict: {'PASS' if overall_pass else 'FAIL'}."
    )

    return EccentricityEvaluation(
        recommended_test_load=rec_load,
        actual_test_load=actual_test_load,
        initial_zero_error_e0=initial_zero_error_e0,
        positions=evaluated_positions,
        overall_verdict=Verdict.PASS if overall_pass else Verdict.FAIL,
        max_corrected_error=max_abs_ec,
        summary_explanation=summary
    )
