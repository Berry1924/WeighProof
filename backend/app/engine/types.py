from enum import Enum
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class AccuracyClass(str, Enum):
    CLASS_I = "I"
    CLASS_II = "II"
    CLASS_III = "III"
    CLASS_IIII = "IIII"


class DeviceType(str, Enum):
    GRADUATED_WITHOUT_AUX = "graduated_without_auxiliary"
    GRADUATED_WITH_AUX = "graduated_with_auxiliary"
    NON_GRADUATED = "non_graduated"


class WeighingDirection(str, Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class ReportStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    SIGNED = "SIGNED"
    REJECTED = "REJECTED"


class UserRole(str, Enum):
    TESTER = "tester"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class PartialWeighingRange(BaseModel):
    range_index: int = Field(..., description="1-indexed range index")
    max_capacity: Decimal
    verification_scale_interval_e: Decimal
    actual_scale_interval_d: Optional[Decimal] = None
    min_capacity: Optional[Decimal] = None


class InstrumentMasterData(BaseModel):
    manufacturer: str
    model: str
    serial_number: str
    accuracy_class: AccuracyClass
    max_capacity: Decimal
    min_capacity: Decimal
    verification_scale_interval_e: Decimal
    actual_scale_interval_d: Decimal
    unit: str = "g"
    device_type: DeviceType = DeviceType.GRADUATED_WITHOUT_AUX
    points_of_support: int = 4
    is_multi_interval: bool = False
    is_grading_instrument: bool = False
    partial_ranges: Optional[List[PartialWeighingRange]] = None
    temperature_min_c: Optional[Decimal] = Decimal("-10.0")
    temperature_max_c: Optional[Decimal] = Decimal("40.0")

    @field_validator("max_capacity", "min_capacity", "verification_scale_interval_e", "actual_scale_interval_d", mode="before")
    def convert_to_decimal(cls, v):
        if v is not None:
            return Decimal(str(v))
        return v


class PlausibilityCheckResult(BaseModel):
    check_name: str
    clause: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class PlausibilityEvaluation(BaseModel):
    is_valid: bool
    calculated_n: Decimal
    allowed_n_min: Optional[Decimal]
    allowed_n_max: Optional[Decimal]
    allowed_min_capacity: Decimal
    checks: List[PlausibilityCheckResult]
    summary_verdict: Verdict
