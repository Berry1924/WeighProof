---
name: Metrological Defect / Bug Report
about: Report an unexpected calculation, tolerance divergence, or software error
title: "[BUG]: "
labels: ["bug", "metrology"]
assignees: ""
---

### Describe the Bug
<!-- A clear and concise description of what the bug is. -->

### Instrument Under Evaluation
- **Accuracy Class**: Class I / II / III / IIII
- **Max Capacity ($Max$)**: 
- **Min Capacity ($Min$)**: 
- **Verification Scale Interval ($e$)**: 
- **Actual Scale Interval ($d$)**: 
- **Multi-Interval**: Yes / No (if yes, list partial ranges)

### Test Load & Observations
- **Test Type**: Weighing Performance / Eccentricity / Repeatability / Discrimination / Zero Return
- **Load Applied ($L$)**: 
- **Indication ($I$)**: 
- **Add-load at Changeover ($\Delta L$)**: 
- **Observed / Calculated Turning Point ($P$)**: 
- **Calculated Error ($E$)**: 
- **Corrected Error ($E_c$)**: 
- **Applicable MPE**: 
- **System Verdict**: PASS / FAIL

### Expected Behavior & Standard Clause Citation
<!-- What should the calculation or verdict be according to OIML R 76-1? Cite specific clause (e.g. Clause 3.5.1, Table 6). -->

### System Environment
- OS: [e.g. Windows 11, Ubuntu 22.04]
- Python Version: [e.g. 3.12, 3.13, 3.14]
- WeighProof Version: 1.0.0
