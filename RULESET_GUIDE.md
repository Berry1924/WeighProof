# WeighProof: Metrological Ruleset Authoring & Versioning Guide

> **Innovation A**: Schema-validated, decoupled metrological rulesets enabling instant updates, national adoptions, and standard revisions without modifying application source code or restarting servers.

---

## 1. Overview & Architectural Rationale

In conventional legal metrology software, tolerances, verification intervals, and MPE equations are hard-coded into procedural logic. When an international standard updates (such as the transition from **OIML R 76-1:1992** to **OIML R 76-1:2006**) or a nation adopts specific amendments (such as Australia's **NMI R 76-1** or India's **Legal Metrology (General) Rules, 2011**), legacy systems require extensive refactoring, re-compilation, and re-validation.

**WeighProof** solves this by separating **evaluation algorithms** from **metrological rulesets**:
- **Evaluation Engine**: Implements the immutable mathematical principles of metrology ($P = I + 0.5e - \Delta L$, $E = P - L$, $E_c = E - E_0$, $\Delta E \le |\text{mpe}|$).
- **Rulesets (`rulesets/*.json`)**: Declare standard-specific constants, Table 3 classification limits, Table 6 MPE step boundaries, auxiliary device ratios, and repeatability requirements.
- **Ruleset Schema (`schemas/ruleset.schema.json`)**: Strictly enforces structure using JSON Schema Draft 2020-12 before any ruleset can be registered or evaluated.

---

## 2. Directory Structure & Discovery

```
rulesets/
├── oiml_r76_2006.json    # OIML R 76-1:2006 (E) baseline
├── oiml_r76_1992.json    # OIML R 76-1:1992 edition
└── [custom_standard].json# Any dropped standard or amendment
schemas/
└── ruleset.schema.json   # JSON Schema Draft 2020-12 definition
```

### Hot-Reloading Without Server Restart
WeighProof supports **zero-downtime hot-reloading**:
1. **Filesystem Drop**: Any valid JSON file placed in `rulesets/` is automatically detected by `ruleset_registry.reload()` on subsequent requests.
2. **Explicit Admin API**: Administrators can register rulesets over HTTP via `POST /api/rulesets` (with persistent disk write) or invoke `POST /api/rulesets/reload`.

---

## 3. Ruleset Schema Specification

Every ruleset must strictly conform to `schemas/ruleset.schema.json`. Below is the comprehensive field breakdown:

| Field Path | Type | Metrological Clause & Description |
| :--- | :--- | :--- |
| `ruleset_id` | `string` | Unique snake_case identifier (e.g. `oiml_r76_2006`, `nmi_r76_2004`). |
| `edition` | `string` | Formal edition designation (e.g. `2006 (E)`). |
| `title` | `string` | Full title of the standard. |
| `citation` | `string` | Primary normative citation for audit trails. |
| `rounding_mode` | `string` | Decimal rounding policy (`ROUND_HALF_UP` per metrology consensus). |
| `in_service_mpe_multiplier` | `number` | Multiplier for field verification ($2.0 \times \text{MPE}$ under Clause 3.5.2). |
| `accuracy_classes` | `object` | Definitions for Classes `I`, `II`, `III`, and `IIII`. |
| `accuracy_classes.[CLASS].classification_intervals` | `array` | Table 3 intervals defining $e$ range, $n_{min}$, $n_{max}$, and $Min$ multiplier. |
| `accuracy_classes.[CLASS].mpe_bands_initial` | `array` | Table 6 load bands in multiples of $m = m / e$ and resulting MPE factors. |
| `multi_interval_rules.min_ratio_max_to_next_e` | `object` | Table 4 ratio $Max_i / e_{i+1}$ (e.g., Class III requires $\ge 500$). |
| `eccentricity_rules.fraction_of_max` | `number` | Load fraction for off-center tests (Clause A.4.7: $1/3 \approx 0.333333$). |
| `repeatability_rules.min_runs` | `integer` | Minimum series repetitions (Clause A.4.10 requires $\ge 3$ runs). |

---

## 4. Complete Annotated Example

Below is a valid ruleset extract illustrating Class III configuration under OIML R 76-1:2006:

```json
{
  "$schema": "../schemas/ruleset.schema.json",
  "ruleset_id": "oiml_r76_2006",
  "standard": "OIML R 76-1",
  "edition": "2006 (E)",
  "title": "Non-automatic weighing instruments - Part 1: Metrological and technical requirements - Tests",
  "citation": "OIML R 76-1:2006(E) Section 3 & Annex A",
  "rounding_mode": "ROUND_HALF_UP",
  "in_service_mpe_multiplier": 2.0,
  "accuracy_classes": {
    "III": {
      "name": "Medium Accuracy (Class III)",
      "classification_intervals": [
        {
          "e_min_g": 0.1,
          "e_max_g": 2.0,
          "min_capacity_multiplier_e": 20,
          "n_min": 100,
          "n_max": 10000
        },
        {
          "e_min_g": 5.0,
          "e_max_g": null,
          "min_capacity_multiplier_e": 20,
          "n_min": 500,
          "n_max": 10000
        }
      ],
      "mpe_bands_initial": [
        { "m_min_e": 0, "m_max_e": 500, "mpe_multiplier_e": 0.5 },
        { "m_min_e": 500, "m_max_e": 2000, "mpe_multiplier_e": 1.0 },
        { "m_min_e": 2000, "m_max_e": 10000, "mpe_multiplier_e": 1.5 }
      ]
    }
  },
  "multi_interval_rules": {
    "min_ratio_max_to_next_e": {
      "I": 50000,
      "II": 5000,
      "III": 500,
      "IIII": 50
    }
  },
  "eccentricity_rules": {
    "fraction_of_max": 0.333333,
    "support_points_factor": {
      "4": 0.333333,
      "more_than_4": 0.2
    }
  },
  "repeatability_rules": {
    "min_runs": 3,
    "load_fractions": [0.5, 1.0]
  }
}
```

---

## 5. Step-by-Step Guide: Adding a New National Standard

To add a new standard or revision (e.g., **Indian Legal Metrology Rules 2011**, `in_lmr_2011`):

1. **Create the Ruleset File**:
   Copy `rulesets/oiml_r76_2006.json` to `rulesets/in_lmr_2011.json`.
2. **Update Metadata**:
   Set `"ruleset_id": "in_lmr_2011"`, `"edition": "2011 Edition"`, `"title": "Standards of Weights and Measures (General) Rules / Legal Metrology Act 2009"`.
3. **Customize Specific Clauses**:
   Adjust any national tolerances, $n_{max}$ bounds, or verification intervals.
4. **Validate Schema**:
   Run schema validation locally or via pytest:
   ```bash
   python -c "import json, jsonschema; s=json.load(open('schemas/ruleset.schema.json')); r=json.load(open('rulesets/in_lmr_2011.json')); jsonschema.validate(r, s); print('Schema Validated Successfully!')"
   ```
5. **Reload into WeighProof**:
   Call the reload endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/rulesets/reload -H "Authorization: Bearer <TOKEN>"
   ```
   The standard is now immediately selectable in the UI workbench dropdown and API evaluation endpoints.

---

## 6. Safety & Immutability Rules

- **Sealed Reports Retain Original Ruleset Snapshot**: When a report is signed and locked, the active ruleset ID and edition string are permanently baked into the report record and cryptographic canonical hash. Subsequent alterations to ruleset files cannot alter historical evaluations.
- **Fail-Fast Validation**: If a ruleset JSON contains schema violations (e.g. negative numbers, missing classes, invalid enum), WeighProof logs a warning and isolates the corrupted file without affecting previously loaded rulesets.
