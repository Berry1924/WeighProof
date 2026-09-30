# WeighProof: AI Agent & Developer Domain Instructions

> **Repository Purpose**: Non-Automatic Weighing Instrument (NAWI) Pattern Approval / Laboratory Type Evaluation Test Report Generator conforming strictly to **OIML R 76-1:2006**, **OIML R 76-1:1992**, and **OIML R 76-2:2007**.
> **Context**: Smart India Hackathon 2026 (Problem Statement PS26035).

---

## 1. Golden Metrological Rules

### Rule 1: Zero Binary Floating-Point Mathematics
- **NEVER** use Python `float` or JavaScript native floating-point math for metrological calculations (loads, indications, add-loads, turning points, errors, MPEs, or repeatability spreads).
- **ALWAYS** use Python's `decimal.Decimal` with metrology rounding (`ROUND_HALF_UP`).
- Validate incoming numerical fields using Pydantic `field_validator(..., mode="before")` and convert strings/numbers into `Decimal`.

### Rule 2: Three Architectural Innovations
1. **INNOVATION A — Decoupled Rulesets**:
   - Standards are versioned JSON files in `rulesets/*.json` governed by `schemas/ruleset.schema.json`.
   - Never hardcode limits, class bounds, or MPE bands in procedural code.
   - Dynamic reloading happens via `ruleset_registry.reload()`.
2. **INNOVATION B — Explainable Verdict Architecture**:
   - Never return an unadorned `PASS` or `FAIL`.
   - Always return raw inputs, turning point $P$, uncorrected error $E$, corrected error $E_c$, initial zero error $E_0$, MPE, remaining tolerance margin, and normative clause citations.
3. **INNOVATION C — Cryptographic Sealing & Immutability**:
   - Reviewer sign-off permanently locks reports into `SIGNED` state.
   - Any attempt to edit or re-sign returns HTTP 409 Conflict.
   - Canonical JSON is hashed using SHA-256 and verified via `/api/reports/verify/{report_number}?hash={sha256}`.

---

## 2. Fundamental Metrological Formulas (OIML R 76-1)

| Concept | Standard Clause | Exact Formula |
| :--- | :--- | :--- |
| **Changeover Turning Point ($P$)** | Clause A.4.4.3 | $P = I + 0.5e - \Delta L$ |
| **Uncorrected Error ($E$)** | Clause A.4.4.3 | $E = P - L$ |
| **Corrected Error ($E_c$)** | Clause A.4.4.3 | $E_c = E - E_0$ |
| **Table 3 Interval Count ($n$)** | Clause 3.2, Table 3 | $n = Max / e$ (or $n_i = Max_i / e_i$ for multi-interval) |
| **Auxiliary Device Bounds** | Clause 3.4.2, Table 2 | $d < e \le 10d$ |
| **Repeatability Spread ($\Delta E$)** | Clause A.4.10 | $\Delta E = E_{max} - E_{min} \le \|\text{mpe}\|$ |
| **Eccentricity Load** | Clause A.4.7 | $L_{ecc} = 1/3 Max$ (for $N=4$ supports) |
| **In-Service Multiplier** | Clause 3.5.2 | $\text{MPE}_{in\_service} = 2.0 \times \text{MPE}$ |

---

## 3. Directory Layout & File Ownership

```
├── backend/
│   ├── app/
│   │   ├── engine/          # METROLOGICAL CORE (Pure, deterministic, Decimal)
│   │   │   ├── types.py     # Domain models & Pydantic Decimal validators
│   │   │   ├── ruleset.py   # Schema-validated ruleset registry
│   │   │   ├── plausibility.py # Table 3 & Table 4 instrument validation
│   │   │   ├── mpe.py       # Table 6 MPE calculation with explanations
│   │   │   ├── weighing_performance.py # Clause A.4.4 error calculation
│   │   │   ├── eccentricity.py # Clause A.4.7 off-center evaluation
│   │   │   ├── repeatability.py # Clause A.4.10 spread evaluation
│   │   │   ├── pluggable_tests.py # Discrimination & Zero Return
│   │   │   └── hasher.py    # Canonical serialization & SHA-256 sealing
│   │   ├── reports/         # DOCUMENT GENERATION
│   │   │   ├── pdf_generator.py # OIML R 76-2 ReportLab PDF layout
│   │   │   └── docx_generator.py # python-docx Word generator
│   │   ├── auth.py          # Direct Bcrypt & JWT role enforcement
│   │   ├── db.py            # SQLite database engine
│   │   ├── models.py        # SQLAlchemy persistence models
│   │   └── main.py          # FastAPI application & static SPA mount
│   └── tests/               # 28 passing unit & integration tests
├── frontend/                # React 19 + Vite Metrology Workbench UI
├── rulesets/                # Versioned JSON standards (2006, 1992, custom)
├── schemas/                 # JSON Schema Draft 2020-12
└── docs/                    # KNOWLEDGE.md, ASSUMPTIONS.md, PLAN.md, oracles
```

---

## 4. Testing & Quality Requirements

Before submitting changes:
1. Run `python -m pytest -v --cov=backend/app/engine --cov=backend/app/reports`.
2. Ensure **100% test pass rate** and **$\ge 90\%$ test coverage**.
3. Verify adversarial cases in `backend/tests/test_evaluator_audit.py`.
4. Validate schema compliance with `jsonschema.validate()`.
