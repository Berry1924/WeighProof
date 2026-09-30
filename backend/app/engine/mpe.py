from decimal import Decimal
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.engine.types import AccuracyClass, InstrumentMasterData, PartialWeighingRange


class MpeCalculationResult(BaseModel):
    load: Decimal
    e_used: Decimal
    unit: str
    load_in_e: Decimal
    mpe_multiplier_e: Decimal
    mpe_value: Decimal
    band_min_e: Decimal
    band_max_e: Optional[Decimal]
    is_in_service: bool
    clause_citation: str
    explanation: str


def get_active_partial_range(
    load: Decimal,
    partial_ranges: List[PartialWeighingRange]
) -> PartialWeighingRange:
    sorted_ranges = sorted(partial_ranges, key=lambda r: r.range_index)
    for r in sorted_ranges:
        if load <= r.max_capacity:
            return r
    # Fallback to the last range if load exceeds or equals max
    return sorted_ranges[-1]


def calculate_mpe(
    load: Decimal,
    instrument: InstrumentMasterData,
    ruleset: Dict[str, Any],
    is_in_service: bool = False
) -> MpeCalculationResult:
    """
    Computes MPE for a given load according to OIML R 76-1 Table 6 and ruleset definitions.
    Strictly uses Decimal arithmetic and generates an explainable breakdown.
    """
    unit = instrument.unit.strip().lower()
    acc_class = instrument.accuracy_class.value
    class_def = ruleset["accuracy_classes"].get(acc_class)
    if not class_def:
        raise ValueError(f"Accuracy class {acc_class} not found in ruleset.")

    # Determine applicable e (single or multi-interval)
    if instrument.is_multi_interval and instrument.partial_ranges:
        active_range = get_active_partial_range(load, instrument.partial_ranges)
        e = active_range.verification_scale_interval_e
        range_note = f" (Partial Range {active_range.range_index}, e = {e} {unit})"
    else:
        e = instrument.verification_scale_interval_e
        range_note = ""

    # Express load in multiples of e: m = load / e
    load_in_e = load / e

    # Find matching MPE band from ruleset
    bands = class_def.get("mpe_bands_initial", [])
    matched_band = None
    for band in bands:
        b_min = Decimal(str(band["m_min_e"]))
        b_max = Decimal(str(band["m_max_e"])) if band.get("m_max_e") is not None else None

        if b_min == Decimal(0):
            # First band: 0 <= m <= b_max
            if load_in_e <= b_max:
                matched_band = band
                break
        else:
            # Subsequent bands: b_min < m <= b_max
            if b_max is not None:
                if b_min < load_in_e <= b_max:
                    matched_band = band
                    break
            else:
                if load_in_e > b_min:
                    matched_band = band
                    break

    if matched_band is None:
        # Fallback to highest band
        matched_band = bands[-1]

    base_multiplier = Decimal(str(matched_band["mpe_multiplier_e"]))
    b_min_val = Decimal(str(matched_band["m_min_e"]))
    b_max_val = Decimal(str(matched_band["m_max_e"])) if matched_band.get("m_max_e") is not None else None

    # In-service multiplier (typically 2.0 if in-service verification, 1.0 for type evaluation)
    service_factor = Decimal(str(ruleset.get("in_service_mpe_multiplier", 2.0))) if is_in_service else Decimal(1)
    final_multiplier_e = base_multiplier * service_factor
    mpe_value = final_multiplier_e * e

    upper_str = f"<= {b_max_val} e" if b_max_val is not None else "< inf"
    lower_str = f"{b_min_val} e < " if b_min_val > Decimal(0) else "0 e <= "
    clause = "OIML R 76-1 Clause 3.5.2 (In-Service)" if is_in_service else "OIML R 76-1 Clause 3.5.1, Table 6"

    service_note = " [In-service 2x MPE applied]" if is_in_service else " [Initial verification MPE]"

    explanation = (
        f"Load {load} {unit} = {load_in_e} e{range_note}. "
        f"For Accuracy Class {acc_class}, Table 6 band ({lower_str}m {upper_str}) "
        f"yields MPE multiplier = {final_multiplier_e} e{service_note}. "
        f"With e = {e} {unit}, MPE = +/- {mpe_value} {unit}."
    )

    return MpeCalculationResult(
        load=load,
        e_used=e,
        unit=unit,
        load_in_e=load_in_e,
        mpe_multiplier_e=final_multiplier_e,
        mpe_value=mpe_value,
        band_min_e=b_min_val,
        band_max_e=b_max_val,
        is_in_service=is_in_service,
        clause_citation=clause,
        explanation=explanation
    )
