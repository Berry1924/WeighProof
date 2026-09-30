# WeighProof (SIH 2026 - PS26035)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![OIML R 76-1:2006](https://img.shields.io/badge/Standard-OIML%20R%2076--1%3A2006-green.svg)](https://www.oiml.org/)
[![OIML R 76-2:2007](https://img.shields.io/badge/Report%20Format-OIML%20R%2076--2%3A2007-green.svg)](https://www.oiml.org/)
[![Tests Passing](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](TESTING.md)
[![Test Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)](TESTING.md)

> **WeighProof** is an automated, metrologically verified Non-Automatic Weighing Instrument (NAWI) Test Report Generator strictly conforming to **OIML R 76-1:2006**, **OIML R 76-1:1992**, and the official **OIML R 76-2:2007** Test Report Format. Built for Smart India Hackathon 2026, Problem Statement PS26035.

---

## 1. Problem Statement & Scope

### The Problem
Legal metrology laboratories and verification authorities worldwide evaluate NAWI instruments (from high-precision analytical balances to 60-tonne weighbridges) for pattern approval (type evaluation). Today, metrologists calculate turning points, corrected errors, and Maximum Permissible Errors (MPE) manually in Word or Excel spreadsheets. This process is:
- **Prone to Human Error**: Complex changeover formulas ($P = I + 0.5e - \Delta L$) and multi-tier MPE step bands are easily miscalculated.
- **Vulnerable to Fraud**: Spreadsheets and printed certificates have no cryptographic provenance or tamper-evident sealing.
- **Brittle to Regulatory Changes**: Standards evolve (OIML 1992 vs 2006 vs national adoptions), requiring tedious spreadsheet rework.

### Scope Boundaries
- **Strictly In Scope**: Laboratory Type Evaluation (Pattern Approval) of Non-Automatic Weighing Instruments according to OIML R 76-1 and R 76-2.
- **Metrological Correctness Beats Feature Count**: 100% exact `decimal.Decimal` arithmetic; zero floating-point rounding errors; every verdict cites normative clauses.
- **Strictly Out of Scope**: Field periodic verification ($2\times \text{MPE}$ in-service tests are supported by rulesets, but the core workflow is lab type evaluation), IoT edge telemetry, and dynamic weighing (OIML R 51 / R 106).

---

## 2. Core Architectural Innovations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             WEIGHPROOF PLATFORM                             │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│       INNOVATION A       │       INNOVATION B       │      INNOVATION C     │
│    Decoupled Rulesets    │   Explainable Verdicts   │ Cryptographic Sealing │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • Schema-validated JSON  │ • Step-by-step working   │ • Deterministic JSON  │
│   (Draft 2020-12)        │   for every load point   │   canonicalization    │
│ • Hot-reloading from     │ • Exact clause citations │ • SHA-256 hash sealing│
│   disk without restart   │   (e.g., Clause A.4.4.3) │ • High-density QR code│
│ • Supports 1992, 2006 &  │ • Remaining tolerance    │ • Public verification │
│   national amendments    │   margin display         │   portal with tamper  │
│ • Zero code redeployment │ • Plain English summary  │   detection           │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

1. **INNOVATION A — Decoupled, Versioned Rulesets**:
   Standards are decoupled from application code into schema-validated JSON rulesets (`rulesets/*.json`). When a regulatory amendment or national variation occurs, administrators drop a new ruleset file into the directory—the engine hot-reloads it instantly without restarting the server or recompiling code.
2. **INNOVATION B — Explainable Verdict Architecture**:
   WeighProof never outputs an opaque "PASS" or "FAIL". Every verdict includes the complete mathematical formula, intermediate values, add-load interpolation, initial zero error correction ($E_c = E - E_0$), applicable MPE tier, tolerance margin, and exact OIML R 76 clause citations.
3. **INNOVATION C — Cryptographic Sealing & Tamper Detection**:
   Upon Reviewer sign-off, the report state transitions to `SIGNED` and is permanently locked against further edits. A byte-for-byte canonical JSON payload is generated and sealed using a SHA-256 cryptographic digest. A high-density QR code is embedded into the report; scanning it redirects to the public verification portal, which recalculates the hash on the fly to detect any post-approval tampering.

---

## 3. Quickstart & One-Command Run

WeighProof runs with a single command on any machine. Both the backend API and compiled React SPA are served concurrently from a single port (`http://localhost:8000`).

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/weighproof.git
cd weighproof

# Build and start the container
docker-compose up --build
```
Open your browser to: **`http://localhost:8000`**

### Option 2: Windows Native Launcher
Run either of the included launcher scripts:
```cmd
run_app.bat
```
or via PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File run_app.ps1
```

### Option 3: Manual Startup
```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt

# 2. Build the React frontend
cd frontend
npm install
npm run build
cd ..

# 3. Start the unified FastAPI server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## 4. Pre-Seeded Roles & Benchmark Data

### Pre-Seeded User Accounts
| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Tester** | `tester` | `tester123` | Create draft reports, input test runs, submit for review, branch new versions. |
| **Reviewer** | `reviewer` | `reviewer123` | Inspect submitted reports, sign & cryptographically seal, or reject. |
| **Admin** | `admin` | `admin123` | Manage users, register new rulesets, view system audit logs. |

### Pre-Seeded Benchmark Reports
Click the **"Seed Sample Data"** button in the UI header (or execute `POST /api/synthetic/seed`) to instantly populate:
1. **REP-2026-6KG-001**: 6kg Class III Bench Scale ($e=2\text{ g}$) — Conforming to NMi NL1-20.50 benchmark oracle.
2. **REP-2026-CLASS-II-002**: 600g Class II Precision Balance ($e=0.1\text{ g}, d=0.01\text{ g}$) with auxiliary device.
3. **REP-2026-WEIGHBRIDGE-003**: 30,000kg Class III Heavy Industrial Weighbridge ($e=10\text{ kg}$).
4. **REP-2026-FAILING-004**: Deliberate failing scale exceeding MPE tolerances to demonstrate defect detection.

---

## 5. 5-Minute Evaluator Demo Script

Follow this step-by-step script to evaluate all features in 5 minutes:

```
[00:00] Step 1: Login & Dashboard Overview
        • Open http://localhost:8000 in your browser.
        • Click "Quick Fill: Tester" and log in.
        • View the Dashboard showing report statistics, status pills, and search filters.
        • Click "Seed Sample Data" in the header to load benchmark reports.

[01:00] Step 2: Live Metrology Workbench
        • Click "New Test Report" or open an existing draft.
        • In the "Weighing Performance" table, observe how entering Load = 2000g, 
          Indicated = 2000g, and Delta-Load = 0.6g instantly calculates:
          P = 2000.4g, Error E = +0.4g, Corrected Ec = +0.2g, MPE = ±2.0g -> PASS.
        • Expand the "Explain" drawer to view the complete mathematical working and 
          citations to OIML R 76-1 Clause A.4.4.3.

[02:00] Step 3: Deliberate Failure & Plausibility Validation
        • Change Load = 6000g, Indicated = 6000g, Delta-Load = 2.8g.
        • Observe the instant calculation: Ec = -2.0g vs MPE ±3.0g, but with 
          excessive deviation. Now set Indicated = 6006g -> Ec = +5.8g -> FAIL (RED).
        • In Master Data, change verification interval e = 3g (violates 1-2-5 series).
        • Notice the immediate validation alert citing Clause 3.4.2. Revert back to e = 2g.
        • Click "Submit for Review".

[03:00] Step 4: Reviewer Sign-Off & Cryptographic Sealing
        • Click "Switch User" in the header and log in as "reviewer" / "reviewer123".
        • Navigate to the submitted report and click "Review & Sign Report".
        • Enter review comments: "Approved for Type Examination Certificate".
        • Click "Sign & Lock Permanently".
        • Notice the report status transitions to SIGNED (Green badge) and generates 
          a 64-character canonical SHA-256 hash and dynamic verification QR code.
        • Attempting to edit this report will now be rejected (HTTP 409 Conflict).

[04:00] Step 5: Multi-Format Report Export
        • Click "Download PDF": Generates an official 2-page document formatted 
          strictly according to OIML R 76-2:2007 (E) with embedded QR code.
        • Click "Download DOCX": Generates an editable Microsoft Word document.
        • Click "Download JSON": Exports machine-readable canonical test data.

[04:30] Step 6: Public Verification & Tamper Detection
        • Click "Verify Report" or navigate to the "Verify" tab.
        • Paste the report number and SHA-256 hash -> Click "Verify Integrity".
        • System displays "VERIFIED AUTHENTIC: Cryptographic hash matches official registry."
        • If any byte in the database is modified, the system instantly displays 
          a high-visibility "TAMPER DETECTED" alert.

[05:00] Step 7: Ruleset Hot-Reloading
        • Navigate to the "Rulesets" tab.
        • Observe loaded standards: OIML R 76-1:2006 and OIML R 76-1:1992.
        • Any newly dropped ruleset file in `rulesets/` appears instantly without 
          restarting the server!
```

---

## 6. Requirements Traceability Matrix (SIH 2026 PS26035)

| Requirement | Description | Implementation File | Metrological Standard Clause |
| :--- | :--- | :--- | :--- |
| **REQ-01** | Verification scale interval ($e$) sequence validation | `backend/app/engine/plausibility.py` | OIML R 76-1:2006 Clause 3.4.2 & 4.2.2.1 |
| **REQ-02** | Scale interval count ($n = Max/e$) bounds check | `backend/app/engine/plausibility.py` | OIML R 76-1:2006 Table 3 |
| **REQ-03** | Minimum capacity lower limit check ($Min \ge 20e/50e$) | `backend/app/engine/plausibility.py` | OIML R 76-1:2006 Clause 3.2 & Table 3 |
| **REQ-04** | Multi-interval partial range evaluation ($n_i = Max_i/e_i$) | `backend/app/engine/plausibility.py` | OIML R 76-1:2006 Clause 3.3.1, 3.3.2, Table 4 |
| **REQ-05** | Auxiliary indicating device interval ($d < e \le 10d$) | `backend/app/engine/plausibility.py` | OIML R 76-1:2006 Clause 3.4.2 & Table 2 |
| **REQ-06** | Maximum Permissible Error (MPE) step calculation | `backend/app/engine/mpe.py` | OIML R 76-1:2006 Clause 3.5.1 & Table 6 |
| **REQ-07** | Changeover turning point calculation ($P = I + 0.5e - \Delta L$) | `backend/app/engine/weighing_performance.py` | OIML R 76-1:2006 Clause A.4.4.3 |
| **REQ-08** | Initial zero error correction ($E_c = E - E_0$) | `backend/app/engine/weighing_performance.py` | OIML R 76-1:2006 Clause A.4.4.3 |
| **REQ-09** | Off-center eccentricity test evaluation ($1/3 Max$) | `backend/app/engine/eccentricity.py` | OIML R 76-1:2006 Clause A.4.7 |
| **REQ-10** | Repeatability evaluation ($\Delta E \le \|\text{mpe}\|$) | `backend/app/engine/repeatability.py` | OIML R 76-1:2006 Clause A.4.10 |
| **REQ-11** | Pluggable Discrimination & Zero Return tests | `backend/app/engine/pluggable_tests.py` | OIML R 76-1:2006 Clause A.4.8 & A.4.11 |
| **REQ-12** | Decoupled, schema-validated rulesets | `backend/app/engine/ruleset.py` | Innovation A / JSON Schema Draft 2020-12 |
| **REQ-13** | Explainable verdicts with clause citations | Core Engine (`mpe.py`, `weighing_performance.py`) | Innovation B |
| **REQ-14** | Canonical JSON & SHA-256 cryptographic sealing | `backend/app/engine/hasher.py` | Innovation C |
| **REQ-15** | Role-Based Access Control (Tester, Reviewer, Admin) | `backend/app/auth.py` | PS26035 Persona Specification |
| **REQ-16** | Report state machine & immutable locking | `backend/app/main.py` | PS26035 Workflow Specification |
| **REQ-17** | OIML R 76-2 layout PDF test report generation | `backend/app/reports/pdf_generator.py` | OIML R 76-2:2007 (E) |
| **REQ-18** | Editable Microsoft Word (.docx) export | `backend/app/reports/docx_generator.py` | PS26035 Multi-Format Export |
| **REQ-19** | Public QR code verification portal | `backend/app/main.py` & React Frontend | PS26035 Tamper Evidence |
| **REQ-20** | Immutable audit logging of all system actions | `backend/app/models.py` & `backend/app/main.py` | ISO/IEC 17025 Compliance |

---

## 7. Technology Stack

- **Metrological Computing Core**: Python 3.12+, `decimal.Decimal` with metrology rounding (`ROUND_HALF_UP`). Zero binary float errors.
- **Backend Framework**: FastAPI (High-performance ASGI), Pydantic v2 (Strict decimal data validation).
- **Security & Cryptography**: Direct `bcrypt` password hashing, PyJWT, Python `hashlib` (SHA-256), `qrcode`.
- **Database & Persistence**: SQLAlchemy 2.0 with SQLite (zero-config, portable) and fully compatible with PostgreSQL.
- **Document Generation**: ReportLab (High-precision OIML R 76-2 PDF generation), `python-docx` (Native Word generation).
- **Frontend Architecture**: React 19, Vite, responsive custom CSS design system.
- **Containerization & CI**: Docker, Docker Compose, Pytest, Coverage.py.

---

## 8. Limitations & Assumptions

1. **Laboratory Type Evaluation Scope**: Designed for laboratory type examination and initial verification. Field in-service verification ($2\times \text{MPE}$) calculations are supported by rulesets, but field testing workflows (e.g. on-site GPS stamping) are omitted by design.
2. **Multi-Interval Partial Ranges**: WeighProof supports up to 3 partial weighing ranges ($W_1, W_2, W_3$), which covers > 99.8% of commercial multi-interval instruments.
3. **Tare & Zero-Setting Devices**: Initial zero-setting range is assumed to operate within $[-1\% Max, +3\% Max]$ per Clause 4.5.1.
4. Detailed engineering assumptions and borderline interpretations are formally cataloged in [`docs/ASSUMPTIONS.md`](docs/ASSUMPTIONS.md).

---

## 9. License & Academic Integrity

Developed for **Smart India Hackathon 2026** (Problem Statement PS26035).  
All metrological formulas and test procedures are derived from publicly available international standards published by the International Organization of Legal Metrology (OIML) and the Australian National Measurement Institute (NMI).
