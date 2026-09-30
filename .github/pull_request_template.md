## Pull Request Description

### Summary of Changes
<!-- Provide a clear, high-level explanation of what changes were made and why. -->

### Metrological & Regulatory Alignment
- [ ] Conforms to **OIML R 76-1:2006** / **OIML R 76-1:1992** / **OIML R 76-2:2007**
- [ ] Relevant clause citations included in code docstrings and test assertions:
  <!-- Example: Clause A.4.4.3 (Changeover points), Clause 3.5.1 (MPE step boundaries) -->
- [ ] Zero binary floating-point math (`decimal.Decimal` used exclusively with `ROUND_HALF_UP`)
- [ ] No hardcoded metrological limits introduced (ruleset decoupled via `schemas/ruleset.schema.json`)

### Testing & Verification
- [ ] Hand-calculated test oracle included or verified against existing benchmark (`docs/oracle/`)
- [ ] Pytest suite passes cleanly: `python -m pytest -v --cov=backend/app/engine --cov=backend/app/reports`
- [ ] Code coverage maintained at or above 90%
- [ ] Evaluator audit suite passes: `python -m pytest -v backend/tests/test_evaluator_audit.py`

### Security & State Integrity
- [ ] Immutability of `SIGNED` test reports preserved (HTTP 409 Conflict on modification)
- [ ] RBAC boundaries respected (Tester vs Reviewer vs Admin)
- [ ] Cryptographic SHA-256 canonical hash calculation unaffected or verified
