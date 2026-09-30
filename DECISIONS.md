# WeighProof: Architectural Decision Records (ADRs)

> Comprehensive record of architectural and metrological engineering decisions made during the design and implementation of WeighProof for Smart India Hackathon 2026 (PS26035).

---

## Index of Decisions

- [ADR-01: Decimal Arithmetic vs Binary Floating-Point](#adr-01-decimal-arithmetic-vs-binary-floating-point)
- [ADR-02: Decoupled Schema-Validated Rulesets (Innovation A)](#adr-02-decoupled-schema-validated-rulesets-innovation-a)
- [ADR-03: Explainable Verdict Architecture with Clause Citations (Innovation B)](#adr-03-explainable-verdict-architecture-with-clause-citations-innovation-b)
- [ADR-04: Canonical Serialization & SHA-256 Cryptographic Sealing (Innovation C)](#adr-04-canonical-serialization--sha-256-cryptographic-sealing-innovation-c)
- [ADR-05: Unified Single-Process SPA & API Serving](#adr-05-unified-single-process-spa--api-serving)
- [ADR-06: Direct Bcrypt Cryptographic Primitives over Passlib Wrapper](#adr-06-direct-bcrypt-cryptographic-primitives-over-passlib-wrapper)
- [ADR-07: Dual Native PDF & DOCX Generation over Headless Chrome](#adr-07-dual-native-pdf--docx-generation-over-headless-chrome)

---

### ADR-01: Decimal Arithmetic vs Binary Floating-Point
- **Status**: Accepted
- **Context**: In IEEE-754 floating-point arithmetic, fractions such as `0.1` and `0.2` cannot be represented exactly in binary (`0.1 + 0.2 = 0.30000000000000004`). In legal metrology, a difference of $0.00001\text{ e}$ can incorrectly flip a verdict between PASS and FAIL at MPE boundaries.
- **Decision**: All metrological calculations (loads, indications, add-loads, turning points, errors, MPEs, and spreads) are performed strictly using Python's `decimal.Decimal` with metrology rounding (`ROUND_HALF_UP`). Binary `float` is rejected at the Pydantic validator boundary.
- **Consequences**: Absolute mathematical determinism matching hand-calculated test oracles to arbitrary precision. Minor conversion overhead compared to native float, which is negligible for lab type evaluation workloads.

---

### ADR-02: Decoupled Schema-Validated Rulesets (Innovation A)
- **Status**: Accepted
- **Context**: Legal metrology standards evolve over time (e.g. OIML R 76-1:1992 vs 2006) and differ across national jurisdictions (e.g., India Legal Metrology Rules, Australia NMI R 76-1). Hardcoding these limits into backend code leads to technical debt, tight coupling, and difficult deployments.
- **Decision**: Define standards in versioned JSON rulesets (`rulesets/*.json`) governed by a formal JSON Schema Draft 2020-12 (`schemas/ruleset.schema.json`). Rulesets are hot-reloaded dynamically from disk without restarting the application server.
- **Consequences**: Type evaluation labs can add new editions or national adoptions instantly. Schema validation guarantees that corrupt or incomplete files cannot crash the evaluation engine.

---

### ADR-03: Explainable Verdict Architecture with Clause Citations (Innovation B)
- **Status**: Accepted
- **Context**: Typical software outputs boolean verdicts (`PASS` or `FAIL`) without context. In legal metrology type examination, certifying authorities and manufacturers require explicit mathematical working and normative clause citations to defend decisions in court or international audits.
- **Decision**: Every engine function returns structured objects including raw inputs, turning point calculations ($P$), uncorrected errors ($E$), corrected errors ($E_c$), applicable MPE, remaining tolerance margin, exact standard clause citation, and human-readable narrative explanations.
- **Consequences**: Total transparency for testers, reviewers, and manufacturers. Enables interactive inspection in the frontend UI and rich automated report generation.

---

### ADR-04: Canonical Serialization & SHA-256 Cryptographic Sealing (Innovation C)
- **Status**: Accepted
- **Context**: Manual Word/Excel type examination reports are prone to post-approval tampering, unauthorized alterations, or fraudulent certificates.
- **Decision**: Upon Reviewer sign-off, the report state is locked permanently. A deterministic canonical JSON string is formed (sorted keys, stripped volatile transport metadata, standardized ISO-8601 UTC timestamps) and hashed using SHA-256. A high-density QR code is embedded into the report pointing to the public verification endpoint.
- **Consequences**: Any unauthorized modification to the database or report document alters the calculated hash and immediately triggers a "TAMPER DETECTED" alert on the public verification portal.

---

### ADR-05: Unified Single-Process SPA & API Serving
- **Status**: Accepted
- **Context**: Requiring separate Node.js dev servers, Nginx reverse proxies, and Python backends complicates local execution, increasing friction for hackathon evaluators and lab technicians.
- **Decision**: Compile the React frontend into static assets (`frontend/dist`) and serve them directly from FastAPI using `StaticFiles(html=True)`. Provide simple single-click launcher scripts (`run_app.bat` and `run_app.ps1`) and a single `Dockerfile`.
- **Consequences**: The entire application (REST API, Interactive UI, Database, and Metrology Engine) starts with a single command on `http://localhost:8000` with zero configuration overhead.

---

### ADR-06: Direct Bcrypt Cryptographic Primitives over Passlib Wrapper
- **Status**: Accepted
- **Context**: Passlib 1.7.4 is unmaintained and incompatible with modern Python 3.14 + `bcrypt 5.0.0`, triggering `AttributeError` when inspecting version attributes.
- **Decision**: Remove Passlib and use direct native Python bindings to `bcrypt.hashpw()` and `bcrypt.checkpw()`.
- **Consequences**: Zero legacy wrapper dependencies, faster execution, and future-proof compatibility with Python 3.12, 3.13, and 3.14.

---

### ADR-07: Dual Native PDF & DOCX Generation over Headless Chrome
- **Status**: Accepted
- **Context**: Headless browser printing (Puppeteer/Playwright) requires heavy browser binaries (~300MB), high RAM usage, and exhibits cross-platform font rendering discrepancies.
- **Decision**: Implement native document generators using `ReportLab` for pixel-perfect OIML R 76-2 PDFs and `python-docx` for editable Word documents.
- **Consequences**: Blazing fast generation (< 100ms), zero external binary dependencies, lightweight container footprints, and strict conformance to OIML R 76-2 page layouts.
