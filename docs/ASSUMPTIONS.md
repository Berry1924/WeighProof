# Metrological Assumptions and Boundary Conditions

This document identifies operational assumptions, interpretation boundaries, and points requiring human verification against specific laboratory accreditations or national legislation.

---

## 1. Flagged Items (HUMAN MUST VERIFY)

### [HUMAN MUST VERIFY 01] Eccentricity Zero-Point Re-Zeroing
* **Clause Reference**: OIML R 76-1:2006, Clause A.4.7 (Page 91).
* **Context**: The standard states: *"Normally it is sufficient to determine the zero error only at the beginning of the measurement, but on special instruments (accuracy class I, high capacity, etc.) it is recommended that the zero error be determined prior to each eccentricity loading. However, if the mpe is exceeded, the test with zero error prior to each loading is necessary."*
* **Engine Implementation**: The engine supports both modes:
  1. `single_zero` (default): Uses the initial $E_0$ recorded before position 1 across all positions.
  2. `per_position_zero`: Allows a dedicated $E_{0, pos}$ before each individual eccentricity position.
* **Human Verification Required**: Lab quality managers must verify which procedure is mandated by their national accreditation (e.g. NBL / NATA / PTB).

### [HUMAN MUST VERIFY 02] Repeatability Series Size for Type Approval vs In-Service
* **Clause Reference**: OIML R 76-1:2006, Clause A.4.10 (Page 93).
* **Context**: For type approval, Clause A.4.10 specifies two series of weighings (approx. $50\%$ Max and $100\%$ Max). For $Max < 1\,000\text{ kg}$, each series requires 10 weighings. For $Max \ge 1\,000\text{ kg}$, at least 3 weighings. In contrast, for routine field verification (NITP 6.1), only 3 weighings at $0.8 Max$ are commonly used.
* **Engine Implementation**: WeighProof strictly targets Type Evaluation (Pattern Approval), defaulting to 10 weighings for $Max < 1\,000\text{ kg}$ and at least 3 for $Max \ge 1\,000\text{ kg}$.
* **Human Verification Required**: Accredited test officer must confirm the series size matches their test schedule.

### [HUMAN MUST VERIFY 03] Overload Indication Blanking Threshold
* **Clause Reference**: OIML R 76-1:2006, Clause 4.2.2.4.
* **Context**: An instrument must not indicate values exceeding $Max + 9e$.
* **Engine Implementation**: Master data validation rejects test loads greater than $Max + 9e$.
* **Human Verification Required**: Testing officer must ensure test loads submitted for weighing performance remain within valid functional range.

### [HUMAN MUST VERIFY 04] High-Resolution Auxiliary Display ($d \le 0.2e$)
* **Clause Reference**: OIML R 76-1:2006, Clause 3.5.3.2 & A.4.4.3.
* **Context**: If an instrument provides an auxiliary mode or extended display during testing with actual scale interval $d \le 0.2e$, rounding error elimination via changeover weights ($\Delta L$) is not required; error can be computed directly as $E = I - L$.
* **Engine Implementation**: The engine checks whether turning load $\Delta L$ is provided. If $\Delta L$ is omitted and $d \le 0.2e$, it computes $E = I - L$. If $d > 0.2e$ and $\Delta L$ is missing, it raises a validation error.
* **Human Verification Required**: Operator must confirm whether the instrument was placed into service mode with fine resolution or if turning weights were added.

---

## 2. Engineering Scope Boundaries

1. **Type Evaluation Only**:
   The scope is restricted to laboratory type evaluation (OIML R 76-1 / R 76-2), not in-service field verification (which uses $2 \times \text{MPE}$), and not continuous dynamic scales.
2. **Deterministic Computations**:
   Metrological engine contains zero stochastic components or heuristics. Every result is computed using exact Decimal arithmetic.
3. **Traceability to Standard Editions**:
   Every test report and result payload explicitly records the exact ruleset ID (e.g. `oiml_r76_2006`) and version.
