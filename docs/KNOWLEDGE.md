# Metrological Knowledge Base: OIML R 76 & NAWI Type Evaluation

This document consolidates verified metrological principles, clauses, mathematical formulas, and rules governing Type Evaluation (Pattern Approval) of Non-Automatic Weighing Instruments (NAWI) based on OIML R 76-1 (2006 and 1992 editions) and OIML R 76-2 (Test Report Format).

---

## 1. Verified Evidence Registry

| Claim ID | Metrological Rule / Requirement | Primary Source & Clause/Table | Corroborating Source | Confidence Level |
|---|---|---|---|---|
| **KB-01** | Accuracy Classes: Four accuracy classes exist: Special (I), High (II), Medium (III), Ordinary (IIII). | OIML R 76-1:2006, Cl. 3.1.1, Table 1 | OIML R 76-1:1992 Cl. 3.1.1 Table 1; NMI R 76-1 Table 1 | **Verified by 2+ sources** |
| **KB-02** | Scale Intervals $e$ and $d$: For graduated instruments without auxiliary indicating device, $e = d$. Scale interval $e$ must be of the form $1 \times 10^k, 2 \times 10^k, 5 \times 10^k$ units of mass. | OIML R 76-1:2006, Cl. 3.1.2 Table 2, Cl. 3.4.2 | OIML R 76-1:1992 Cl. 3.1.2 Table 2; NMi Cert NL1-20.50 | **Verified by 2+ sources** |
| **KB-03** | Auxiliary Indicating Devices (Classes I and II only): Permitted only to right of decimal point; requires $d < e \le 10d$ (except Class I $d < 1\text{ mg}$ where $e = 1\text{ mg}$). Multi-interval cannot have auxiliary device. | OIML R 76-1:2006, Cl. 3.4.1, Cl. 3.4.2, Table 5a/5b | OIML R 76-1:1992 Cl. 3.4.1, Cl. 3.4.2 | **Verified by 2+ sources** |
| **KB-04** | Instrument Classification Parameters (Table 3):<br>• Class I: $e \ge 0.001\text{ g}$, $Min = 100e$ ($100d$ if aux), $n_{min} = 50\,000$, $n_{max} = \infty$<br>• Class II ($0.001\text{ g} \le e \le 0.05\text{ g}$): $Min = 20e$, $n \in [100, 100\,000]$<br>• Class II ($e \ge 0.1\text{ g}$): $Min = 50e$, $n \in [5\,000, 100\,000]$<br>• Class III ($0.1\text{ g} \le e \le 2\text{ g}$): $Min = 20e$, $n \in [100, 10\,000]$<br>• Class III ($e \ge 5\text{ g}$): $Min = 20e$, $n \in [500, 10\,000]$<br>• Class IIII ($e \ge 5\text{ g}$): $Min = 10e$, $n \in [100, 1\,000]$ | OIML R 76-1:2006, Cl. 3.2, Table 3 | OIML R 76-1:1992 Cl. 3.2 Table 3; NMi Cert NL1-20.50 | **Verified by 2+ sources** |
| **KB-05** | Grading Instruments Exception: Minimum capacity is reduced to $5e$ for grading instruments determining transport tariff or toll (e.g. postal scales, waste material). | OIML R 76-1:2006, Cl. 3.2 | OIML R 76-1:1992 Cl. 3.2 | **Verified by 2+ sources** |
| **KB-06** | Multi-Interval Instruments (Table 4): $e_1 < e_2 < \dots < e_r$, $Min_1 = Min$, $Min_i = Max_{i-1}$. For $i < r$, $Max_i / e_{i+1} \ge 50\,000$ (I), $\ge 5\,000$ (II), $\ge 500$ (III), $\ge 50$ (IIII). | OIML R 76-1:2006, Cl. 3.3.1 - 3.3.3, Table 4 | OIML R 76-1:1992 Cl. 3.3.1 - 3.3.3 | **Verified by 2+ sources** |
| **KB-07** | MPE Bands on Initial Verification (Table 6):<br>• Class I: $0 \le m \le 50\,000e \to \pm 0.5e$; $50\,000e < m \le 200\,000e \to \pm 1.0e$; $m > 200\,000e \to \pm 1.5e$<br>• Class II: $0 \le m \le 5\,000e \to \pm 0.5e$; $5\,000e < m \le 20\,000e \to \pm 1.0e$; $20\,000e < m \le 100\,000e \to \pm 1.5e$<br>• Class III: $0 \le m \le 500e \to \pm 0.5e$; $500e < m \le 2\,000e \to \pm 1.0e$; $2\,000e < m \le 10\,000e \to \pm 1.5e$<br>• Class IIII: $0 \le m \le 50e \to \pm 0.5e$; $50e < m \le 200e \to \pm 1.0e$; $200e < m \le 1\,000e \to \pm 1.5e$ | OIML R 76-1:2006, Cl. 3.5.1, Table 6 | OIML R 76-1:1992 Cl. 3.5.1 Table 6; NMI R 76-1 Table 6 | **Verified by 2+ sources** |
| **KB-08** | In-Service MPE: Values in service are exactly $2 \times \text{MPE}_{\text{initial}}$. Lab type evaluation uses $\text{MPE}_{\text{initial}}$. | OIML R 76-1:2006, Cl. 3.5.2 | OIML R 76-1:1992 Cl. 3.5.2 | **Verified by 2+ sources** |
| **KB-09** | Elimination of Rounding Error & Changeover Points: Required if $d > 0.2e$. Indication prior to rounding $P = I + 0.5e - \Delta L$. Error prior to rounding $E = P - L = I + 0.5e - \Delta L - L$. | OIML R 76-1:2006, Cl. 3.5.3.2, Cl. A.4.4.3 | OIML R 76-2:2007 p. 5, p. 10; OIML R 76-1:1992 Cl. A.4.4.3 | **Verified by 2+ sources** |
| **KB-10** | Corrected Error Formula: $E_c = E - E_0$, where $E_0$ is the error calculated at zero or near zero (e.g. $10e$). Pass condition: $\|E_c\| \le \|\text{mpe}\|$. | OIML R 76-1:2006, Cl. A.4.4.3 | OIML R 76-2:2007 p. 5, p. 10 | **Verified by 2+ sources** |
| **KB-11** | Weighing Performance Test Protocol: Progressively increasing and decreasing test loads. At least 10 different test loads for initial intrinsic error (at least 5 for other tests). Must include Max, Min, and MPE transition points. | OIML R 76-1:2006, Cl. A.4.4.1 | OIML R 76-2:2007 Form 1 (p. 10); NITP 6.1 Cl. 3.1 | **Verified by 2+ sources** |
| **KB-12** | Eccentricity Test Protocol: Load applied is $\approx 1/3 (Max + T^+)$ for $\le 4$ supports; $1/(n-1)(Max + T^+)$ for $n > 4$. Quarter segments (1, 2, 3, 4) loaded successively. Corrected error at each location must satisfy $\|E_c\| \le \|\text{mpe}\|$. | OIML R 76-1:2006, Cl. 3.6.2, Cl. A.4.7 | OIML R 76-2:2007 Form 3 (p. 12); NITP 6.1 Cl. 3.2 | **Verified by 2+ sources** |
| **KB-13** | Repeatability Test Protocol: Two load series: $\approx 50\% Max$ and $\approx 100\% Max$. For $Max < 1\,000\text{ kg}$, 10 weighings per series; for $Max \ge 1\,000\text{ kg}$, at least 3 weighings. Conditions: (a) Each $\|E_i\| \le \|\text{mpe}\|$, and (b) $E_{max} - E_{min} \le \|\text{mpe}\|$. | OIML R 76-1:2006, Cl. 3.6.1, Cl. A.4.10 | OIML R 76-2:2007 Form 5 (p. 16); NITP 6.1 Cl. 3.3 | **Verified by 2+ sources** |
| **KB-14** | Tare Influence & Net Values: MPE applies to net values for any possible tare load (subtractive tare tested between $1/3$ and $2/3$ Max tare; additive tare tested at $1/3$ and $3/3$). | OIML R 76-1:2006, Cl. 3.5.3.3, Cl. A.4.6 | OIML R 76-2:2007 Form 9 (p. 21) | **Verified by 2+ sources** |
| **KB-15** | Discrimination Test Protocol: For digital indication ($d \ge 5\text{ mg}$): load + weights, remove until indication decreases by $1d$; add $0.1d$, then add $1.4d$. Indication must unambiguously increase by $+1d$. | OIML R 76-1:2006, Cl. 3.8.2.2, Cl. A.4.8.2 | OIML R 76-2:2007 Form 4 (p. 14) | **Verified by 2+ sources** |
| **KB-16** | Digital Reporting Data Structures: NAWI elements mapped to DCC XML/JSON: `itemQuantities` (Max, Min, e, d), test results series, environmental conditions (temperature, humidity, pressure). | IMEKO TC6 2025 (PTB) | ISO/IEC 17025; OIML R 76-2 | **Verified by 2+ sources** |

---

## 2. Mathematical Formalization & Rounding Rule

1. **Numerical Representation**:
   All metrological evaluations MUST use arbitrary-precision decimal arithmetic (`decimal.Decimal` in Python). Binary floating-point representation (`float`) is strictly prohibited in metrological calculations to prevent floating-point representation errors (e.g. $0.1 + 0.2 \ne 0.3$).

2. **Rounding Rule**:
   Rounding operations shall conform to standard metrological rounding (`ROUND_HALF_UP` unless specified otherwise). Rounding must ONLY occur at the final presentation layer, NOT during intermediate difference calculations.

3. **Core Equations**:
   $$\text{Turning Point Indication: } P = I + \frac{1}{2}e - \Delta L$$
   $$\text{Uncorrected Error: } E = P - L = I + \frac{1}{2}e - \Delta L - L$$
   $$\text{Corrected Error: } E_c = E - E_0$$
   $$\text{Verdict Criterion: } |E_c| \le |\text{mpe}|$$
   $$\text{Repeatability Range Criterion: } \Delta E = E_{max} - E_{min} \le |\text{mpe}|$$
