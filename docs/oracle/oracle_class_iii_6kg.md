# Metrological Test Oracle: Class III 6 kg / 2 g Retail Counter Scale

This document specifies the exact, hand-verified test oracle calculations conforming strictly to **OIML R 76-1:2006**, Clauses 3.2, 3.5.1, 3.6, A.4.4, A.4.7, and A.4.10.

---

## 1. Instrument Master Parameters
* **Accuracy Class**: III
* **Maximum Capacity ($Max$)**: $6\,000\text{ g}$ ($6\text{ kg}$)
* **Verification Scale Interval ($e$)**: $2\text{ g}$
* **Actual Scale Interval ($d$)**: $2\text{ g}$ ($d = e$)
* **Scale Intervals Count ($n$)**: $n = Max / e = 6\,000 / 2 = 3\,000$ (Complies with Table 3: $100 \le n \le 10\,000$)
* **Minimum Capacity ($Min$)**: $20e = 40\text{ g}$ (Complies with Table 3: $Min \ge 20e$)
* **Units**: Grams ($\text{g}$)

### Applicable MPE Thresholds (OIML R 76-1 Table 6)
* **Band 1**: $0 \le m \le 500e$ ($0\text{ g} \le m \le 1\,000\text{ g}$): $\text{MPE} = \pm 0.5e = \pm 1.0\text{ g}$
* **Band 2**: $500e < m \le 2\,000e$ ($1\,000\text{ g} < m \le 4\,000\text{ g}$): $\text{MPE} = \pm 1.0e = \pm 2.0\text{ g}$
* **Band 3**: $2\,000e < m \le 10\,000e$ ($4\,000\text{ g} < m \le 6\,000\text{ g}$): $\text{MPE} = \pm 1.5e = \pm 3.0\text{ g}$

---

## 2. Test 1: Weighing Performance (OIML R 76-2 Form 1)

### Mathematical Formulation
* $P = I + 0.5e - \Delta L = I + 1.0 - \Delta L$
* $E = P - L$
* $E_0 = +0.20\text{ g}$ (determined at zero prior to loading)
* $E_c = E - E_0$
* Verdict: $|E_c| \le |\text{mpe}|$

### Hand-Computed Execution Table

| Direction | Load $L$ (g) | Multiples of $e$ | MPE ($\pm$ g) | Indication $I$ (g) | Added Load $\Delta L$ (g) | Turning Indication $P$ (g) | Error $E$ (g) | Corrected Error $E_c$ (g) | Step Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **Zero** | 0.0 | 0 | 1.0 | 0.0 | 0.8 | 0.20 | +0.20 | 0.00 | **PASS** |
| **Increasing** | 40.0 (Min) | 20 | 1.0 | 40.0 | 0.9 | 40.10 | +0.10 | -0.10 | **PASS** |
| **Increasing** | 500.0 | 250 | 1.0 | 500.0 | 1.0 | 500.00 | 0.00 | -0.20 | **PASS** |
| **Increasing** | 1000.0 (Step 1) | 500 | 1.0 | 1000.0 | 1.2 | 999.80 | -0.20 | -0.40 | **PASS** |
| **Increasing** | 2000.0 | 1000 | 2.0 | 2000.0 | 0.6 | 2000.40 | +0.40 | +0.20 | **PASS** |
| **Increasing** | 3000.0 | 1500 | 2.0 | 3000.0 | 0.8 | 3000.20 | +0.20 | 0.00 | **PASS** |
| **Increasing** | 4000.0 (Step 2) | 2000 | 2.0 | 4000.0 | 0.5 | 4000.50 | +0.50 | +0.30 | **PASS** |
| **Increasing** | 5000.0 | 2500 | 3.0 | 5000.0 | 0.7 | 5000.30 | +0.30 | +0.10 | **PASS** |
| **Increasing** | 6000.0 (Max) | 3000 | 3.0 | 6000.0 | 0.4 | 6000.60 | +0.60 | +0.40 | **PASS** |
| **Decreasing** | 5000.0 | 2500 | 3.0 | 5000.0 | 0.6 | 5000.40 | +0.40 | +0.20 | **PASS** |
| **Decreasing** | 4000.0 | 2000 | 2.0 | 4000.0 | 0.5 | 4000.50 | +0.50 | +0.30 | **PASS** |
| **Decreasing** | 2000.0 | 1000 | 2.0 | 2000.0 | 0.7 | 2000.30 | +0.30 | +0.10 | **PASS** |
| **Decreasing** | 1000.0 | 500 | 1.0 | 1000.0 | 1.1 | 999.90 | -0.10 | -0.30 | **PASS** |
| **Decreasing** | 40.0 (Min) | 20 | 1.0 | 40.0 | 0.8 | 40.20 | +0.20 | 0.00 | **PASS** |
| **Decreasing** | 0.0 | 0 | 1.0 | 0.0 | 0.8 | 0.20 | +0.20 | 0.00 | **PASS** |

**Weighing Performance Overall Verdict: PASS**

---

## 3. Test 2: Eccentricity Test (OIML R 76-2 Form 3)
* **Test Load**: $\approx \frac{1}{3} Max = 2\,000\text{ g}$
* **Load Band**: $2\,000\text{ g} = 1\,000e \implies \text{MPE} = \pm 1.0e = \pm 2.0\text{ g}$
* $E_0 = +0.20\text{ g}$

| Location ID | Description | Load $L$ (g) | $I$ (g) | $\Delta L$ (g) | $P$ (g) | $E$ (g) | Corrected $E_c$ (g) | MPE ($\pm$ g) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **Center** | Platform Center | 2000.0 | 2000.0 | 0.8 | 2000.20 | +0.20 | 0.00 | 2.0 | **PASS** |
| **Pos 1** | Front Left Quadrant | 2000.0 | 2000.0 | 0.5 | 2000.50 | +0.50 | +0.30 | 2.0 | **PASS** |
| **Pos 2** | Back Left Quadrant | 2000.0 | 2000.0 | 1.1 | 1999.90 | -0.10 | -0.30 | 2.0 | **PASS** |
| **Pos 3** | Back Right Quadrant | 2000.0 | 2000.0 | 0.7 | 2000.30 | +0.30 | +0.10 | 2.0 | **PASS** |
| **Pos 4** | Front Right Quadrant | 2000.0 | 2000.0 | 0.9 | 2000.10 | +0.10 | -0.10 | 2.0 | **PASS** |

**Eccentricity Overall Verdict: PASS**

---

## 4. Test 3: Repeatability Test (OIML R 76-2 Form 5)
* Since $Max = 6\text{ kg} < 1\,000\text{ kg}$, 10 weighings are evaluated per series.

### Series 1: Load $\approx 50\% Max = 3\,000\text{ g}$ ($1\,500e$, $\text{MPE} = \pm 2.0\text{ g}$)
* Zero error reset between weighings if indicated.

| Run # | Load $L$ (g) | $I$ (g) | $\Delta L$ (g) | $P$ (g) | Error $E_i$ (g) | Criterion a: $\|E_i\| \le 2.0$ |
|---|---|---|---|---|---|---|
| 1 | 3000.0 | 3000.0 | 0.8 | 3000.20 | +0.20 | PASS |
| 2 | 3000.0 | 3000.0 | 0.7 | 3000.30 | +0.30 | PASS |
| 3 | 3000.0 | 3000.0 | 0.9 | 3000.10 | +0.10 | PASS |
| 4 | 3000.0 | 3000.0 | 0.8 | 3000.20 | +0.20 | PASS |
| 5 | 3000.0 | 3000.0 | 1.0 | 3000.00 | 0.00 | PASS |
| 6 | 3000.0 | 3000.0 | 0.7 | 3000.30 | +0.30 | PASS |
| 7 | 3000.0 | 3000.0 | 1.1 | 1999.90 (3000-0.1) | -0.10 | PASS |
| 8 | 3000.0 | 3000.0 | 0.8 | 3000.20 | +0.20 | PASS |
| 9 | 3000.0 | 3000.0 | 1.2 | 2999.80 | -0.20 | PASS |
| 10 | 3000.0 | 3000.0 | 0.8 | 3000.20 | +0.20 | PASS |

* $E_{max} = +0.30\text{ g}$, $E_{min} = -0.20\text{ g}$
* Spread $\Delta E = E_{max} - E_{min} = +0.30 - (-0.20) = 0.50\text{ g}$
* Criterion b: $\Delta E \le |\text{mpe}| = 2.0\text{ g} \implies 0.50 \le 2.0 \implies$ **PASS**

### Series 2: Load $\approx 100\% Max = 6\,000\text{ g}$ ($3\,000e$, $\text{MPE} = \pm 3.0\text{ g}$)
* $E_{max} = +0.60\text{ g}$, $E_{min} = +0.10\text{ g}$
* Spread $\Delta E = +0.60 - (+0.10) = 0.50\text{ g}$
* Criterion b: $0.50 \le 3.0\text{ g} \implies$ **PASS**

**Repeatability Overall Verdict: PASS**
