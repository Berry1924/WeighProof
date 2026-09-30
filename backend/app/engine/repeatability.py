from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from app.engine.types import (
    InstrumentMasterData,
    Verdict,
)
from app.engine.mpe import calculate_mpe, MpeCalculationResult
from app.engine.plausibility import to_grams


class RepeatabilityRunInput(BaseModel):
    run_number: int
    load: Decimal
    indicated: Decimal
    delta_load: Optional[Decimal] = None
    remarks: Optional[str] = None

    @field_validator("load", "indicated", "delta_load", mode="before")
    def convert_to_decimal(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v


class RepeatabilityRunResult(BaseModel):
    run_number: int
    load: Decimal
    indicated: Decimal
    delta_load: Optional[Decimal]
    turning_indication_p: Decimal
    error_e: Decimal
    mpe: Decimal
    verdict: Verdict
    explanation: str


class RepeatabilitySeriesResult(BaseModel):
    series_name: str
    target_load: Decimal
    mpe: Decimal
    runs: List[RepeatabilityRunResult]
    e_max: Decimal
    e_min: Decimal
    spread_delta_e: Decimal
    individual_errors_verdict: Verdict
    spread_verdict: Verdict
    overall_series_verdict: Verdict
    explanation: str


class RepeatabilityEvaluation(BaseModel):
    series_evaluations: List[RepeatabilitySeriesResult]
    overall_verdict: Verdict
    summary_explanation: str


def evaluate_repeatability_series(
    series_name: str,
    runs_input: List[RepeatabilityRunInput],
    instrument: InstrumentMasterData,
    ruleset: Dict[str, Any],
    is_in_service: bool = False
) -> RepeatabilitySeriesResult:
    if not runs_input:
        raise ValueError(f"No runs provided for repeatability series '{series_name}'.")

    e = instrument.verification_scale_interval_e
    unit = instrument.unit.strip().lower()
    target_load = runs_input[0].load

    mpe_res = calculate_mpe(target_load, instrument, ruleset, is_in_service=is_in_service)
    mpe_val = mpe_res.mpe_value

    evaluated_runs: List[RepeatabilityRunResult] = []
    all_runs_pass = True

    for r in runs_input:
        if r.delta_load is not None:
            p = r.indicated + (Decimal("0.5") * e) - r.delta_load
            err = p - r.load
            formula = f"P = {r.indicated} + 0.5*{e} - {r.delta_load} = {p} {unit}, E = {err} {unit}"
        else:
            p = r.indicated
            err = r.indicated - r.load
            formula = f"P = {p} {unit}, E = {err} {unit}"

        run_pass = abs(err) <= mpe_val
        if not run_pass:
            all_runs_pass = False

        status = "PASS" if run_pass else "FAIL"
        run_explain = (
            f"Run #{r.run_number}: Load L = {r.load} {unit}. {formula}. "
            f"MPE = +/- {mpe_val} {unit}. Criterion |E| <= |mpe|: |{err}| <= {mpe_val} -> {status} (Clause 3.6)."
        )

        evaluated_runs.append(RepeatabilityRunResult(
            run_number=r.run_number,
            load=r.load,
            indicated=r.indicated,
            delta_load=r.delta_load,
            turning_indication_p=p,
            error_e=err,
            mpe=mpe_val,
            verdict=Verdict.PASS if run_pass else Verdict.FAIL,
            explanation=run_explain
        ))

    errors = [r.error_e for r in evaluated_runs]
    e_max = max(errors)
    e_min = min(errors)
    spread = e_max - e_min

    spread_pass = spread <= mpe_val
    overall_pass = all_runs_pass and spread_pass

    series_explain = (
        f"{series_name} (Load = {target_load} {unit}, MPE = +/- {mpe_val} {unit}, {len(evaluated_runs)} weighings): "
        f"Individual errors range [{e_min} {unit} to {e_max} {unit}] -> {'All PASS' if all_runs_pass else 'One or more FAIL'}. "
        f"Repeatability spread ΔE = Emax - Emin = {e_max} - ({e_min}) = {spread} {unit}. "
        f"Criterion b: ΔE <= |mpe| ({spread} <= {mpe_val}) -> {'PASS' if spread_pass else 'FAIL'} (Clause 3.6.1). "
        f"Series verdict: {'PASS' if overall_pass else 'FAIL'}."
    )

    return RepeatabilitySeriesResult(
        series_name=series_name,
        target_load=target_load,
        mpe=mpe_val,
        runs=evaluated_runs,
        e_max=e_max,
        e_min=e_min,
        spread_delta_e=spread,
        individual_errors_verdict=Verdict.PASS if all_runs_pass else Verdict.FAIL,
        spread_verdict=Verdict.PASS if spread_pass else Verdict.FAIL,
        overall_series_verdict=Verdict.PASS if overall_pass else Verdict.FAIL,
        explanation=series_explain
    )


def evaluate_repeatability(
    instrument: InstrumentMasterData,
    series_inputs: Dict[str, List[RepeatabilityRunInput]],
    ruleset: Dict[str, Any],
    is_in_service: bool = False
) -> RepeatabilityEvaluation:
    if not series_inputs:
        raise ValueError("No repeatability series provided.")

    evaluations: List[RepeatabilitySeriesResult] = []
    overall_pass = True

    for name, runs in series_inputs.items():
        res = evaluate_repeatability_series(name, runs, instrument, ruleset, is_in_service=is_in_service)
        evaluations.append(res)
        if res.overall_series_verdict != Verdict.PASS:
            overall_pass = False

    summary = (
        f"Repeatability evaluation finished across {len(evaluations)} series. "
        f"Overall test verdict: {'PASS' if overall_pass else 'FAIL'}."
    )

    return RepeatabilityEvaluation(
        series_evaluations=evaluations,
        overall_verdict=Verdict.PASS if overall_pass else Verdict.FAIL,
        summary_explanation=summary
    )
