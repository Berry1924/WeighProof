from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.engine.types import (
    InstrumentMasterData,
    Verdict,
)
from app.engine.mpe import calculate_mpe


class DiscriminationPointInput(BaseModel):
    load: Decimal
    initial_indication_i: Decimal
    indication_after_1_4d: Decimal
    remarks: Optional[str] = None

    @field_validator("load", "initial_indication_i", "indication_after_1_4d", mode="before")
    def convert_to_decimal(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v


class DiscriminationPointResult(BaseModel):
    load: Decimal
    initial_indication_i: Decimal
    extra_load_applied_1_4d: Decimal
    observed_indication: Decimal
    required_indication: Decimal
    verdict: Verdict
    explanation: str


class DiscriminationEvaluation(BaseModel):
    points: List[DiscriminationPointResult]
    overall_verdict: Verdict
    summary_explanation: str


def evaluate_discrimination(
    instrument: InstrumentMasterData,
    points_input: List[DiscriminationPointInput],
    ruleset: Dict[str, Any]
) -> DiscriminationEvaluation:
    d = instrument.actual_scale_interval_d
    unit = instrument.unit.strip().lower()
    extra_load = Decimal("1.4") * d

    results: List[DiscriminationPointResult] = []
    overall_pass = True

    for pt in points_input:
        expected_ind = pt.initial_indication_i + d
        passed = (pt.indication_after_1_4d == expected_ind)
        if not passed:
            overall_pass = False

        status = "PASS" if passed else "FAIL"
        explain = (
            f"At load {pt.load} {unit}: Initial indication I = {pt.initial_indication_i} {unit}. "
            f"Upon applying 1.4d ({extra_load} {unit}), indication changed to {pt.indication_after_1_4d} {unit}. "
            f"Required indication is I + d = {expected_ind} {unit} -> {status} (OIML R 76-1 Clause 3.8.2.2 & A.4.8.2)."
        )

        results.append(DiscriminationPointResult(
            load=pt.load,
            initial_indication_i=pt.initial_indication_i,
            extra_load_applied_1_4d=extra_load,
            observed_indication=pt.indication_after_1_4d,
            required_indication=expected_ind,
            verdict=Verdict.PASS if passed else Verdict.FAIL,
            explanation=explain
        ))

    summary = (
        f"Discrimination test evaluated for {len(results)} load points (d = {d} {unit}). "
        f"Overall verdict: {'PASS' if overall_pass else 'FAIL'}."
    )

    return DiscriminationEvaluation(
        points=results,
        overall_verdict=Verdict.PASS if overall_pass else Verdict.FAIL,
        summary_explanation=summary
    )


class ZeroReturnInput(BaseModel):
    test_load_near_max: Decimal
    zero_indication_initial_p0: Decimal
    zero_indication_after_30m_p30: Decimal
    zero_indication_after_35m_p35: Optional[Decimal] = None
    remarks: Optional[str] = None

    @field_validator("test_load_near_max", "zero_indication_initial_p0", "zero_indication_after_30m_p30", "zero_indication_after_35m_p35", mode="before")
    def convert_to_decimal(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v


class ZeroReturnEvaluation(BaseModel):
    delta_p30_p0: Decimal
    allowed_max_change_30m: Decimal
    change_30m_verdict: Verdict
    delta_p35_p30: Optional[Decimal]
    allowed_max_change_35m: Optional[Decimal]
    change_35m_verdict: Optional[Verdict]
    overall_verdict: Verdict
    summary_explanation: str


def evaluate_zero_return(
    instrument: InstrumentMasterData,
    test_input: ZeroReturnInput,
    ruleset: Dict[str, Any]
) -> ZeroReturnEvaluation:
    e = instrument.verification_scale_interval_e
    unit = instrument.unit.strip().lower()

    # Clause 3.9.4.2 & A.4.11.2: |delta(P30 - P0)| <= 0.5 e
    delta_30 = abs(test_input.zero_indication_after_30m_p30 - test_input.zero_indication_initial_p0)
    allowed_30 = Decimal("0.5") * e
    pass_30 = delta_30 <= allowed_30

    pass_35 = True
    delta_35 = None
    allowed_35 = None
    verdict_35 = None

    if test_input.zero_indication_after_35m_p35 is not None and instrument.is_multi_interval:
        delta_35 = abs(test_input.zero_indication_after_35m_p35 - test_input.zero_indication_after_30m_p30)
        # For multi-interval: |delta(P35 - P30)| <= e1
        e1 = instrument.partial_ranges[0].verification_scale_interval_e if instrument.partial_ranges else e
        allowed_35 = e1
        pass_35 = delta_35 <= allowed_35
        verdict_35 = Verdict.PASS if pass_35 else Verdict.FAIL

    overall_pass = pass_30 and pass_35
    status = "PASS" if overall_pass else "FAIL"

    summary = (
        f"Zero Return Test (Clause 3.9.4.2 & A.4.11.2): Unloaded after 30 min under Max load. "
        f"|P30 - P0| = |{test_input.zero_indication_after_30m_p30} - {test_input.zero_indication_initial_p0}| = {delta_30} {unit}. "
        f"Allowed <= 0.5e ({allowed_30} {unit}) -> {'PASS' if pass_30 else 'FAIL'}."
    )
    if delta_35 is not None:
        summary += f" Multiple range 5-min drift = {delta_35} {unit} (allowed <= {allowed_35} {unit}) -> {'PASS' if pass_35 else 'FAIL'}."
    summary += f" Overall verdict: {status}."

    return ZeroReturnEvaluation(
        delta_p30_p0=delta_30,
        allowed_max_change_30m=allowed_30,
        change_30m_verdict=Verdict.PASS if pass_30 else Verdict.FAIL,
        delta_p35_p30=delta_35,
        allowed_max_change_35m=allowed_35,
        change_35m_verdict=verdict_35,
        overall_verdict=Verdict.PASS if overall_pass else Verdict.FAIL,
        summary_explanation=summary
    )
