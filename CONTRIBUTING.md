# Contributing to WeighProof

Thank you for your interest in contributing to **WeighProof**! WeighProof is designed for legal metrology type evaluations according to OIML R 76-1 and OIML R 76-2.

Because this system performs statutory legal metrology calculations, correctness, traceability, and strict adherence to international standards take precedence over any new features.

---

## 1. Development Principles

1. **Precision Mandate**: Never use binary floating-point arithmetic (`float`). Always use Python's `decimal.Decimal` with metrology rounding (`ROUND_HALF_UP`).
2. **Decoupled Rulesets**: Do not hardcode tolerances or limits in Python files. Standards belong in `rulesets/*.json` and must validate against `schemas/ruleset.schema.json`.
3. **Traceability**: Every formula, error calculation, and tolerance check must include comments or docstrings citing the relevant standard clause (e.g. OIML R 76-1:2006 Clause A.4.4.3).
4. **Zero Open Bugs**: All PRs must maintain 100% test pass rate and $\ge 90\%$ test coverage.

---

## 2. Local Environment Setup

### Prerequisites
- Python 3.12 or newer
- Node.js 20 or newer
- Git

### Setup Steps
```bash
# 1. Clone repository
git clone https://github.com/your-org/weighproof.git
cd weighproof

# 2. Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt
pip install pytest pytest-cov jsonschema

# 4. Install frontend dependencies and build
cd frontend
npm install
npm run build
cd ..

# 5. Run tests
python -m pytest -v --cov=backend/app/engine --cov=backend/app/reports
```

---

## 3. Proposing New Standards & Rulesets

If you wish to add a new national standard (e.g., Indian Legal Metrology Rules, Australian NMI, US NIST Handbook 44):
1. Review [`RULESET_GUIDE.md`](RULESET_GUIDE.md).
2. Create your ruleset in `rulesets/<standard_id>.json`.
3. Validate against `schemas/ruleset.schema.json`:
   ```bash
   python -c "import json, jsonschema; s=json.load(open('schemas/ruleset.schema.json')); r=json.load(open('rulesets/<standard_id>.json')); jsonschema.validate(r, s); print('Valid!')"
   ```
4. Add a test in `backend/tests/` demonstrating execution against an instrument oracle.

---

## 4. Pull Request Guidelines

1. Fork the repo and create a feature branch (`git checkout -b feature/your-feature`).
2. Ensure all tests pass: `python -m pytest -v`.
3. Fill out the [Pull Request Template](.github/pull_request_template.md).
4. Include metrological citations and hand-calculated oracles for any new formulas.
