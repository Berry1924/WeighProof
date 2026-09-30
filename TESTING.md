# WeighProof: Verification, Testing & Oracle Audit Guide

> **Zero Fabrications Mandate**: Every formula, error calculation, and tolerance comparison in WeighProof is verified against hand-calculated metrological test oracles and international legal metrology standards (OIML R 76-1:2006, OIML R 76-2:2007).

---

## 1. Test Architecture & Methodology

WeighProof employs a multi-tiered testing hierarchy designed for mission-critical legal metrology evaluation:
1. **Mathematical Unit Tests**: Direct evaluation of core algorithms (`mpe.py`, `plausibility.py`, `weighing_performance.py`, `eccentricity.py`, `repeatability.py`, `pluggable_tests.py`) using `decimal.Decimal` with Metrology Rounding (`ROUND_HALF_UP`). Zero binary float approximations.
2. **Oracle Benchmark Tests**: Bit-for-bit comparison against independently hand-calculated oracles derived from real-world laboratory type evaluation certificates (e.g. NMi Certificate NL1-20.50).
3. **Deliberate Failure Tests**: Explicit validation that out-of-tolerance errors, excessive repeatability spreads ($\Delta E > |\text{mpe}|$), and invalid scale parameters are deterministically flagged with metrological clause citations.
4. **End-to-End API & Security Tests**: Full HTTP lifecycle testing covering JWT authentication, role enforcement (RBAC), report state machine transitions, canonical hashing, tamper detection, and multi-format exports (PDF, DOCX, JSON).
5. **Evaluator Audit Suite**: Dedicated test suite simulating adversarial evaluations, database tamper injections, and live ruleset hot-reloading without server restarts.

---

## 2. Test Execution Commands

Run the full automated test suite with coverage from the project root:

```bash
# Full test suite with engine & report generator coverage
python -m pytest -v --cov=backend/app/engine --cov=backend/app/reports

# Run only SIH Evaluator Audit checks
python -m pytest -v backend/tests/test_evaluator_audit.py

# Run API & security integration tests
python -m pytest -v backend/tests/test_api_integration.py

# Run metrological formula tests
python -m pytest -v backend/tests/test_s1_engine.py backend/tests/test_s2_engine.py
```

---

## 3. Test Suite Breakdown

| Test Module | Tests | Focus Area | Status |
| :--- | :---: | :--- | :---: |
| `test_s1_engine.py` | 6 | Ruleset loading (1992 vs 2006), Table 3 plausibility, Table 6 MPE bands, Clause A.4.4 changeover calculation, deliberate failure detection. | **PASS** |
| `test_s2_engine.py` | 6 | Clause A.4.7 eccentricity (center + 4 corners), Clause A.4.10 repeatability spread ($\Delta E$), Clause A.4.8 discrimination, Clause A.4.11 zero return. | **PASS** |
| `test_coverage_boost.py` | 6 | Multi-interval ranges ($n_i = Max_i / e_i$), auxiliary devices ($d < e \le 10d$), dynamic ruleset registry, 6-support eccentricity, multi-series repeatability. | **PASS** |
| `test_api_integration.py` | 5 | JWT auth, tester submission, reviewer sign-off, report locking, version branching (v2), PDF/DOCX/JSON generation, immutable audit logging. | **PASS** |
| `test_evaluator_audit.py` | 5 | Exact oracle match, breaking parameter rejections, RBAC 403 enforcement, database tamper detection via canonical SHA-256, live ruleset drop & hot-reload. | **PASS** |
| **TOTAL** | **28** | **Comprehensive Core & Integration Coverage** | **100% PASS** |

---

## 4. Benchmark Oracle Verification Table

**Instrument Specification** (`docs/oracle/oracle_class_iii_6kg.json`):
- Class III ($e = 2\text{ g}$, $d = 2\text{ g}$, $Max = 6000\text{ g}$, $Min = 40\text{ g}$, $n = 3000$).
- Initial zero error: $E_0 = +0.2\text{ g}$.
- Formula: $P = I + 0.5e - \Delta L = I + 1.0 - \Delta L$; $E = P - L$; $E_c = E - E_0 = E - 0.2\text{ g}$.

| Direction | Load $L$ (g) | Indication $I$ (g) | Add-load $\Delta L$ (g) | Turning $P$ (g) | Error $E$ (g) | Corrected $E_c$ (g) | MPE (g) | Result | Oracle Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Increasing | 0.0 | 0.0 | 0.8 | 0.2 | +0.2 | 0.0 | $\pm 1.0$ | PASS | Verified |
| Increasing | 40.0 | 40.0 | 0.9 | 40.1 | +0.1 | -0.1 | $\pm 1.0$ | PASS | Verified |
| Increasing | 500.0 | 500.0 | 1.0 | 500.0 | 0.0 | -0.2 | $\pm 1.0$ | PASS | Verified |
| Increasing | 1000.0 | 1000.0 | 1.2 | 999.8 | -0.2 | -0.4 | $\pm 1.0$ | PASS | Verified |
| Increasing | 2000.0 | 2000.0 | 0.6 | 2000.4 | +0.4 | +0.2 | $\pm 2.0$ | PASS | Verified |
| Increasing | 3000.0 | 3000.0 | 0.8 | 3000.2 | +0.2 | 0.0 | $\pm 2.0$ | PASS | Verified |
| Increasing | 4000.0 | 4000.0 | 0.5 | 4000.5 | +0.5 | +0.3 | $\pm 2.0$ | PASS | Verified |
| Increasing | 5000.0 | 5000.0 | 0.7 | 5000.3 | +0.3 | +0.1 | $\pm 3.0$ | PASS | Verified |
| Increasing | 6000.0 | 6000.0 | 0.4 | 6000.6 | +0.6 | +0.4 | $\pm 3.0$ | PASS | Verified |
| Decreasing | 5000.0 | 5000.0 | 0.6 | 5000.4 | +0.4 | +0.2 | $\pm 3.0$ | PASS | Verified |
| Decreasing | 4000.0 | 4000.0 | 0.5 | 4000.5 | +0.5 | +0.3 | $\pm 2.0$ | PASS | Verified |
| Decreasing | 2000.0 | 2000.0 | 0.7 | 2000.3 | +0.3 | +0.1 | $\pm 2.0$ | PASS | Verified |
| Decreasing | 1000.0 | 1000.0 | 1.1 | 999.9 | -0.1 | -0.3 | $\pm 1.0$ | PASS | Verified |
| Decreasing | 40.0 | 40.0 | 0.8 | 40.2 | +0.2 | 0.0 | $\pm 1.0$ | PASS | Verified |
| Decreasing | 0.0 | 0.0 | 0.8 | 0.2 | +0.2 | 0.0 | $\pm 1.0$ | PASS | Verified |

---

## 5. Test Coverage Metrics

```
---------- coverage: platform win32, python 3.14.3 -----------
Name                                         Stmts   Miss  Cover
----------------------------------------------------------------
backend\app\engine\__init__.py                   0      0   100%
backend\app\engine\eccentricity.py              62      6    90%
backend\app\engine\hasher.py                    35      5    86%
backend\app\engine\mpe.py                       54      6    89%
backend\app\engine\plausibility.py             137     13    91%
backend\app\engine\pluggable_tests.py           62      3    95%
backend\app\engine\repeatability.py             61      5    92%
backend\app\engine\ruleset.py                   62      9    85%
backend\app\engine\types.py                     49      1    98%
backend\app\engine\weighing_performance.py      59      7    88%
backend\app\reports\docx_generator.py           81      0   100%
backend\app\reports\pdf_generator.py            67      0   100%
----------------------------------------------------------------
TOTAL                                          729     55    92%
```

---

## 6. Breaking Adversarial Verification Scenarios

| Test ID | Adversarial Input / Attack Vector | Expected System Behavior | Test Status |
| :--- | :--- | :--- | :---: |
| **ADV-01** | Scale interval $e = 3\text{ g}$ (violates 1-2-5 sequence). | Rejection with Clause 3.4.2 citation. | **PASS** |
| **ADV-02** | Class III scale with $Max = 30\text{ kg}, e = 2\text{ g} \implies n = 15000 > 10000$. | Rejection with Table 3 citation. | **PASS** |
| **ADV-03** | Class III scale with $Min = 20\text{ g} < 20e = 40\text{ g}$. | Rejection with Clause 3.2 citation. | **PASS** |
| **ADV-04** | Tester user attempts to call `/api/reports/{id}/sign`. | HTTP 403 Forbidden (RBAC enforced). | **PASS** |
| **ADV-05** | Anyone attempts to edit or re-sign a SIGNED report. | HTTP 409 Conflict (Strict immutability). | **PASS** |
| **ADV-06** | Manual database edit of `max_capacity` after reviewer signature. | Verification portal detects hash divergence and flags `tamper_detected = True`. | **PASS** |
| **ADV-07** | Custom ruleset dropped into `rulesets/` during runtime. | Instant detection via `/api/rulesets/reload` without server restart. | **PASS** |
