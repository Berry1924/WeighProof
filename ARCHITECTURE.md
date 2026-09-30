# WeighProof System Architecture
## NAWI Test Report Generator based on OIML R 76 (SIH 2026 - PS26035)

---

## 1. High-Level Architectural Topology

```mermaid
flowchart TB
    subgraph Client_Tier["Client Presentation Layer"]
        WebUI["React 18 Workbench & Dashboard\n(Vite + Component Architecture)"]
        VerifyPortal["Public Verification Portal\n(SHA-256 Checksum & QR Scanner)"]
    end

    subgraph Gateway_Tier["FastAPI Application Services"]
        Router["FastAPI Application Router (/api)"]
        AuthMiddleware["JWT Bearer Authentication\n& RBAC Enforcement"]
        AuditMiddleware["Immutable Audit Logger"]
    end

    subgraph Metrology_Core["Pure Metrological Engine (Zero Dependencies, Decimal Arithmetic)"]
        RulesetRegistry["Ruleset Registry & Schema Validator\n(JSON Schema / schemas/ruleset.schema.json)"]
        PlausibilityEngine["Master Data Plausibility Engine\n(Table 3, 4, Clause 3.2, 3.4)"]
        MPEEngine["MPE Calculation Engine\n(Table 6 & Multi-Interval Bands)"]
        WPEngine["Weighing Performance Engine\n(Clause A.4.4 Changeover Method)"]
        EccEngine["Eccentricity Engine\n(Clause A.4.7 Quadrant Loading)"]
        RepEngine["Repeatability Engine\n(Clause A.4.10 Spread ΔE & Range)"]
    end

    subgraph Data_Storage["Persistence Tier"]
        DB[(SQLite / PostgreSQL Relational DB)]
        RulesetStore[("rulesets/*.json Versioned Store")]
    end

    subgraph Export_Sealing["Cryptographic Sealing & Export Subsystem"]
        CanonicalHasher["Canonical JSON Serializer\n& SHA-256 Hasher"]
        QRGenerator["Vector / Raster QR Code Generator"]
        PDFGen["OIML R 76-2 PDF Generator (ReportLab)"]
        DOCXGen["Editable DOCX Generator (python-docx)"]
    end

    WebUI --> Router
    VerifyPortal --> Router
    Router --> AuthMiddleware
    AuthMiddleware --> AuditMiddleware
    AuditMiddleware --> DB

    Router --> PlausibilityEngine
    Router --> MPEEngine
    Router --> WPEngine
    Router --> EccEngine
    Router --> RepEngine

    RulesetStore --> RulesetRegistry
    RulesetRegistry --> PlausibilityEngine
    RulesetRegistry --> MPEEngine

    Router --> CanonicalHasher
    CanonicalHasher --> QRGenerator
    QRGenerator --> PDFGen
    QRGenerator --> DOCXGen
    PDFGen --> WebUI
    DOCXGen --> WebUI
```

---

## 2. Core Metrological Engine Principles

1. **Deterministic Arbitrary-Precision Arithmetic**:
   The engine uses Python's `decimal.Decimal` exclusively. IEEE 754 floating-point numbers (`float`) are completely forbidden in calculations. This eliminates fractional representation drift (e.g. $0.1 + 0.2 \ne 0.3$), which would invalidate legal metrology compliance.
2. **Standard Rounding Rules**:
   Rounding operations are parameterized by the active ruleset (defaulting to `ROUND_HALF_UP` as specified in OIML R 76-1). Rounding is strictly confined to presentation layers; intermediate calculations maintain full precision.
3. **Changeover Point Error Determination**:
   Conforming to OIML R 76-1 Clause A.4.4.3:
   $$P = I + \frac{1}{2}e - \Delta L$$
   $$E = P - L = I + \frac{1}{2}e - \Delta L - L$$
   $$E_c = E - E_0$$
   where $E_0$ is zero error determined prior to loading.
4. **Explainable Verdicts (INNOVATION B)**:
   Every evaluation step returns a human-readable and machine-verifiable explanation citing the exact OIML clause, the numbers substituted into the formula, the applicable MPE limit, and the binary PASS/FAIL decision.

---

## 3. Report Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Tester creates new evaluation
    DRAFT --> DRAFT: Tester edits load points & metadata
    DRAFT --> SUBMITTED: Tester submits report for Review
    SUBMITTED --> REJECTED: Reviewer rejects with deficiency notes
    REJECTED --> DRAFT: Tester edits & updates
    SUBMITTED --> SIGNED: Reviewer approves, signs & seals
    SIGNED --> SIGNED: Permanent Immutability (Modifications Blocked - HTTP 409)
    SIGNED --> DRAFT: Branch Version (creates v2 draft, leaves v1 intact)
```

---

## 4. Cryptographic Sealing & Tamper Evidence (INNOVATION C)

```mermaid
sequenceDiagram
    autonumber
    actor Reviewer as Reviewer / Metrologist
    participant API as FastAPI Backend
    participant Engine as Canonical Hasher
    participant DB as Relational Database
    actor Public as Public Auditor / Verifier

    Reviewer->>API: POST /api/reports/{id}/sign (comments)
    API->>API: Verify Reviewer Role (RBAC)
    API->>Engine: create_canonical_report_payload(report_dict)
    Note over Engine: Sort keys, strip mutable fields, format Decimals deterministically
    Engine->>Engine: Compute SHA-256 Digest
    Engine->>API: Returns 64-char Hex Hash & QR Code
    API->>DB: UPDATE test_reports SET status='SIGNED', canonical_hash=H, qr_data_uri=QR
    API-->>Reviewer: 200 OK (Report Locked & Sealed)

    Public->>API: GET /api/reports/verify/{report_number}?hash={H}
    API->>DB: Fetch signed report by report_number
    API->>Engine: Re-compute SHA-256 over current DB record
    Engine-->>API: Recomputed Hash
    alt Recomputed Hash == Query Hash
        API-->>Public: 200 OK (Valid, Genuine & Untampered)
    else Content Tampered or Wrong Hash
        API-->>Public: 200 OK (TAMPER DETECTED / Non-Conforming)
    end
```

---

## 5. Security & RBAC Model

| Role | Instrument Creation | Test Evaluations | Save Draft | Submit Report | Sign & Seal Report | Reject Report | Manage Rulesets | View Audit Logs |
|---|---|---|---|---|---|---|---|---|
| **Tester** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Forbidden (403) | ❌ Forbidden (403) | ❌ Read Only | ❌ Forbidden (403) |
| **Reviewer** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ (Review only) | ✅ Authorized | ✅ Authorized | ❌ Read Only | ✅ Authorized |
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Authorized | ✅ Authorized | ✅ Full Control | ✅ Full Control |

---

## 6. Multi-Format Export Architecture

1. **PDF (OIML R 76-2 Layout)**:
   - Generated dynamically via ReportLab.
   - Includes official Part 2 Test Report layout: Page 5 Instrument Characteristics, Page 9 Summary of Type Evaluation, Page 10 Weighing Performance Table, Page 12 Eccentricity, Page 16 Repeatability, Reviewer Signature Block, and embedded verification QR code image.
2. **DOCX (Editable Laboratory Report)**:
   - Generated dynamically via `python-docx`.
   - Formatted tables with bold headers, standard test rows, and high-resolution QR code image.
3. **JSON (DCC / Machine-Readable Format)**:
   - Aligned with EURAMET/CG-18 and PTB IMEKO TC6 (2025) Digital Calibration Certificate schemas.
