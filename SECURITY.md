# Security Policy & Cryptographic Assurance

## Supported Versions

| Version | Supported |
| :--- | :--- |
| 1.0.x | :white_check_mark: |

---

## Cryptographic Sealing & Tamper Verification

WeighProof implements an immutable sealing architecture (Innovation C) to ensure legal metrology test reports cannot be forged or tampered with:
1. **Canonical JSON**: Test report contents are normalized into a deterministic JSON representation (sorted keys, excluded transport headers, standardized ISO-8601 UTC timestamps).
2. **SHA-256 Digest**: The canonical payload is hashed using SHA-256 upon Reviewer sign-off.
3. **Public Verification Portal**: Scanning the embedded QR code or querying `/api/reports/verify/{report_number}?hash={sha256}` dynamically recomputes the SHA-256 hash across stored database rows. If any load, indication, error, or instrument parameter has been altered in the database, the portal immediately flags `tamper_detected: true`.

---

## Reporting a Security Vulnerability

If you discover a security vulnerability (such as a bypass of the report immutability mechanism, cryptographic hash collision vulnerability, or authentication defect):
1. **Do not disclose publicly** in GitHub issues.
2. Email security vulnerability details directly to the project maintainers.
3. Include detailed steps to reproduce, instrument test data, and expected impact.
4. Maintainers will acknowledge within 48 hours and work with you on a coordinated disclosure plan.
