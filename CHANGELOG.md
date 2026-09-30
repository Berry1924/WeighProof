# WeighProof: Engineering Changelog & Vertical Slice History

> Complete tracking of incremental development from initial metrological research to production-ready release for Smart India Hackathon 2026 (PS26035).

---

## [1.0.0] - 2026-09-30

### Vertical Slice S0: Research, Foundation & Metrological Knowledge Base
- Ingested and parsed official legal metrology source standards:
  - **OIML R 76-1:2006 (E)** (`downloaded_sources/oiml_r76_1_2006.pdf`)
  - **OIML R 76-1:1992 (E)** (`downloaded_sources/oiml_r76_1_1992.pdf`)
  - **OIML R 76-2:2007 (E)** (`downloaded_sources/oiml_r76_2.pdf`)
  - **NMi Type Examination Certificate NL1-20.50** (`downloaded_sources/example_cert.pdf`)
  - **IMEKO TC6 2025 Machine-Readable Test Reports** (`downloaded_sources/imeko_tc6.pdf`)
- Synthesized metrological claims in `docs/KNOWLEDGE.md` (claims KB-01 through KB-16 with primary clauses and confidence levels).
- Hand-calculated metrological test oracles:
  - `docs/oracle/oracle_class_iii_6kg.md` & `docs/oracle/oracle_class_iii_6kg.json` (6kg Class III scale, $e=2\text{ g}$, 15 load points).
  - `docs/oracle/oracle_failing_cases.json` (deliberate failure edge cases).
- Established boundary assumptions in `docs/ASSUMPTIONS.md`.
- Authored initial project master plan in `docs/PLAN.md`.
- Formulated the formal ruleset schema in `schemas/ruleset.schema.json` (JSON Schema Draft 2020-12) and encoded baseline rulesets `rulesets/oiml_r76_2006.json` and `rulesets/oiml_r76_1992.json`.

---

### Vertical Slice S1: Core Metrological Engine (Part 1)
- Implemented decimal domain types and Pydantic validation in `backend/app/engine/types.py`.
- Built schema-validated dynamic ruleset registry in `backend/app/engine/ruleset.py`.
- Developed `backend/app/engine/plausibility.py`:
  - Table 3 verification interval and scale division bounds ($n \in [n_{min}, n_{max}]$).
  - Table 4 multi-interval transition ratios ($Max_i / e_{i+1}$).
  - Clause 3.2 minimum capacity check ($Min \ge 20e$ or $50e$).
  - Clause 3.4.2 step interval verification ($e, d \in \{1, 2, 5\} \times 10^k$).
  - Auxiliary device scale interval bounds ($d < e \le 10d$).
- Developed `backend/app/engine/mpe.py`:
  - Table 6 Maximum Permissible Error step function for single and multi-interval scales.
  - Initial evaluation vs in-service ($2.0 \times \text{MPE}$) calculation.
- Developed `backend/app/engine/weighing_performance.py`:
  - Clause A.4.4 changeover point evaluation ($P = I + 0.5e - \Delta L$).
  - Uncorrected error calculation ($E = P - L$).
  - Initial zero error correction ($E_c = E - E_0$).
  - Point-by-point verdict generation with explainable mathematical narratives.

---

### Vertical Slice S2: Core Metrological Engine (Part 2)
- Developed `backend/app/engine/eccentricity.py`:
  - Clause A.4.7 off-center evaluation for arbitrary points of support ($N=4 \implies 1/3 Max$, $N>4 \implies 1/(N-1) Max$).
  - Corrected error evaluation across quadrants and centers.
- Developed `backend/app/engine/repeatability.py`:
  - Clause A.4.10 repeatability evaluation across multiple load series (e.g., $50\% Max$, $100\% Max$).
  - Dual condition check: individual error $E_i \le \text{mpe}$ and maximum difference $\Delta E = E_{max} - E_{min} \le |\text{mpe}|$.
- Implemented pluggable tests in `backend/app/engine/pluggable_tests.py`:
  - Clause A.4.8 Discrimination evaluation ($1.4d$ test load).
  - Clause A.4.11 Zero Return / Zero setting drift evaluation.

---

### Vertical Slice S3: Persistence, Authentication & REST API
- Set up SQLite database with SQLAlchemy in `backend/app/db.py` and `backend/app/models.py`.
- Implemented direct Bcrypt password hashing and PyJWT token issuance in `backend/app/auth.py`.
- Enforced Role-Based Access Control (RBAC) across three distinct metrology roles:
  - `tester`: Can create, edit drafts, submit for review, branch new versions.
  - `reviewer`: Can inspect, sign/lock, or reject submitted reports.
  - `admin`: Can manage users, register rulesets, view system audit logs.
- Built immutable audit trail recording user logins, report creation, submissions, sign-offs, and ruleset registrations.
- Built FastAPI endpoints in `backend/app/main.py`.

---

### Vertical Slice S4: Cryptographic Sealing & Multi-Format Export
- Developed canonical report serialization and SHA-256 digest engine in `backend/app/engine/hasher.py`.
- Integrated high-density QR code generation linking to public verification portal.
- Implemented report state locking: signing a report sets status to `SIGNED`, rendering it immutable (further edits return HTTP 409 Conflict).
- Developed `backend/app/reports/pdf_generator.py` using ReportLab:
  - Formatted strictly according to OIML R 76-2:2007 (E) test report layout.
  - Embedded instrument metadata, test result tables, verdict badges, canonical SHA-256 hash, and verification QR code.
- Developed `backend/app/reports/docx_generator.py` using `python-docx` for editable laboratory documentation.
- Built public verification endpoint `/api/reports/verify/{report_number}`.

---

### Vertical Slice S5: Responsive Web Frontend
- Created modern React 19 single-page application with Vite in `frontend/`.
- Designed clean, metrology-grade CSS design system in `frontend/src/App.css`.
- Implemented core user views:
  - **Dashboard**: Filterable report listing, statistics counters, status badges.
  - **Live Metrology Workbench**: Real-time plausibility validation, dynamic weighing performance calculator, eccentricity grid, and repeatability analysis with explainable working.
  - **Reviewer Sign-Off Modal**: Authorized sign-off with permanent cryptographic locking.
  - **Public Verification Portal**: Real-time hash verification and QR code scanner.
  - **Ruleset Explorer**: Interactive standard browser and dynamic ruleset loader.
  - **Audit Trail Viewer**: System-wide immutable action log.
- Pre-seeded synthetic benchmark reports (6kg Class III scale, 600g Class II balance, 30t weighbridge, deliberate failing scale).
- Compiled production build into `frontend/dist` and mounted directly into FastAPI for unified single-port serving.

---

### Vertical Slice S6: Verification, Containerization & Evaluator Audit
- Created containerization files: `Dockerfile` and `docker-compose.yml`.
- Created single-click native launchers: `run_app.bat` and `run_app.ps1`.
- Authored third-person evaluator test suite `backend/tests/test_evaluator_audit.py`:
  - Bit-for-bit oracle verification.
  - Breaking input plausibility rejections ($n < n_{min}$, $n > n_{max}$, $Min < 20e$, invalid $e$ step).
  - RBAC 403 Forbidden enforcement.
  - Report immutability 409 Conflict checks.
  - Database tamper detection via canonical SHA-256 recalculation.
  - Dynamic ruleset hot-reloading without server restarts.
- Achieved **28 passed tests, 0 failures, and 92% coverage** on metrology engine and report generators.
- Authored documentation suite: `ARCHITECTURE.md`, `RULESET_GUIDE.md`, `TESTING.md`, `BUGS.md`, `DECISIONS.md`, `CHANGELOG.md`, and `README.md`.
