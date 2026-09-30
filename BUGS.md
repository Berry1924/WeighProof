# WeighProof: Bug Tracking & Defect Resolution Log

> **Quality Assurance Policy**: Zero unresolved bugs, zero silent fallbacks, and zero metrological inaccuracies before production release.

---

## Summary of Defects

| Bug ID | Component | Severity | Description | Status |
| :--- | :--- | :--- | :--- | :---: |
| **BUG-01** | `auth.py` | High | Python 3.14 + `bcrypt 5.0.0` breaking `passlib.context` | **RESOLVED** |
| **BUG-02** | `plausibility.py` | High | Multi-interval scale interval count ($n$) evaluation ambiguity | **RESOLVED** |
| **BUG-03** | `hasher.py` / `main.py` | High | SQLite naive datetime formatting breaking SHA-256 hash reproducibility | **RESOLVED** |
| **BUG-04** | `models.py` | Low | Pytest collection warning on SQLAlchemy `TestReport` class | **RESOLVED** |
| **BUG-05** | `main.py` | Medium | Missing update endpoint and 405 response on draft modification | **RESOLVED** |
| **BUG-06** | `ruleset.py` | Medium | Schema validation rejection of custom ruleset missing required properties | **RESOLVED** |

---

## Detailed Defect Reports

### BUG-01: Passlib Incompatibility with Bcrypt 5.0.0 on Python 3.14
- **Discovered**: Vertical Slice S3 (Auth & Storage).
- **Symptoms**: `AttributeError: module 'bcrypt' has no attribute '__about__'` when attempting password verification via `passlib.context.CryptContext`.
- **Root Cause**: Passlib 1.7.4 is unmaintained and queries `bcrypt.__about__.__version__`, an internal legacy property removed in modern Bcrypt releases.
- **Resolution**: Replaced the Passlib abstraction entirely with direct calls to `bcrypt.hashpw()` and `bcrypt.checkpw()`.
- **Verification**: Verified via `test_auth_login_success_and_failure` in `test_api_integration.py`.

---

### BUG-02: Multi-Interval $n$ Calculation Ambiguity
- **Discovered**: Vertical Slice S1 (Metrological Core Engine).
- **Symptoms**: Multi-interval scale evaluations incorrectly failed with "Number of scale intervals $n$ exceeds maximum" when computing $n = Max_r / e_1$.
- **Root Cause**: Under OIML R 76-1:2006 Clause 3.3.1 and 3.3.2, each partial weighing range $i$ must be evaluated against Table 3 using its own verification scale interval: $n_i = Max_i / e_i$, rather than an aggregate $Max_r / e_1$.
- **Resolution**: Refactored `evaluate_instrument_plausibility()` to branch on `is_multi_interval`. For multi-interval instruments, each range evaluates $n_i = Max_i / e_i$ and verifies the Table 4 transition ratio $Max_i / e_{i+1}$.
- **Verification**: Verified with Class III multi-interval scale test case in `test_coverage_boost.py`.

---

### BUG-03: SQLite Naive Datetime Formatting Divergence
- **Discovered**: Vertical Slice S4 (Cryptographic Sealing & Verification).
- **Symptoms**: Verifying a signed report via `/api/reports/verify/{report_number}` intermittently reported `valid: false` even though the report data had not been modified.
- **Root Cause**: SQLite stores `datetime` objects as naive strings (`YYYY-MM-DD HH:MM:SS.mmmmmm`). During signing, the ISO string included timezone offset (`Z`), but subsequent database queries deserialized it differently, causing canonical JSON string divergence.
- **Resolution**: Normalized all signed report timestamps to canonical ISO-8601 UTC format using `.strftime("%Y-%m-%dT%H:%M:%SZ")` across both the signing and verification routines.
- **Verification**: Verified via `test_tamper_detection_in_verification` in `test_evaluator_audit.py`.

---

### BUG-04: Pytest Discovery of SQLAlchemy `TestReport` Class
- **Discovered**: Test suite execution.
- **Symptoms**: Pytest output included `PytestCollectionWarning: cannot collect test class 'TestReport' because it has a __init__ constructor`.
- **Root Cause**: Pytest uses the glob pattern `Test*` for test discovery, causing it to mistake the SQLAlchemy domain model `class TestReport(Base)` for a test case.
- **Resolution**: Added `__test__ = False` attribute to `TestReport` in `backend/app/models.py`.
- **Verification**: Clean pytest test collection with zero warnings.

---

### BUG-05: Missing Update Route for Draft Reports
- **Discovered**: Evaluator audit testing.
- **Symptoms**: Attempting to update notes or parameters on an existing draft report returned HTTP 405 Method Not Allowed.
- **Root Cause**: The API only defined `POST /api/reports`, `GET /api/reports/{id}`, `POST /api/reports/{id}/submit`, and `POST /api/reports/{id}/sign`.
- **Resolution**: Added `PUT /api/reports/{report_id}` to allow modifying draft notes and data, while strictly enforcing that signed reports reject modifications with HTTP 409 Conflict.
- **Verification**: Verified in `test_breaking_rbac_and_immutability` in `test_evaluator_audit.py`.

---

### BUG-06: Schema Validation Enforcement on Incomplete Rulesets
- **Discovered**: Live ruleset hot-reload testing.
- **Symptoms**: Dropping an ad-hoc test JSON caused `jsonschema.ValidationError: 'rounding_mode' is a required property`.
- **Root Cause**: Test fixture omitted required properties defined in `schemas/ruleset.schema.json`.
- **Resolution**: Updated the test fixture to include all schema-required properties (`rounding_mode`, `accuracy_classes`, etc.) and confirmed that `ruleset.py` isolates malformed rulesets while successfully loading valid ones.
- **Verification**: Verified in `test_dynamic_ruleset_hot_reload_without_server_restart`.

---

## Current Status: 0 Open Defects
All identified bugs have been addressed, verified by automated unit and integration tests, and archived.
