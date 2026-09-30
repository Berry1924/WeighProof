# 06 — Synthetic Data Generator Plan

**Source Basis**: `06_Synthetic_Data_Generator_Plan.docx`

---

## 1. Purpose & Product Role

Direct operational hospital workflow datasets containing real workforce blockages are unavailable due to privacy and proprietary restrictions. Therefore, RFO incorporates a **Synthetic Scenario Generator** as a primary product component. 

The simulator creates repeatable, controllable, and measurable traffic patterns, operational shocks, and stress scenarios (`S01`–`S08`) to demonstrate RFO's value live during judge presentations.

---

## 2. Synthetic Entities

1. **Facilities**: Urban Tertiary Hospital (`FAC-CHN-01`), Tier-2 Regional Center (`FAC-CHN-02`), and Network Teleradiology Partner (`FAC-NET-01`).
2. **Radiologists**: Roster with diverse sub-specialties (`NEURO`, `PEDS`, `CHEST`, `MSK`, `GENERAL`), shift patterns, availability states, and max capacity ceilings ($8–15$ cases).
3. **Orders**: Diagnostic work items with synthetic patient IDs (`PAT-XXXX`), modalities (`CT`, `MRI`, `XR`, `US`), urgency flags (`STAT`, `URGENT`, `ROUTINE`), and SLA timers.
4. **Operational Events**: Dynamic injection of staff unavailability, sudden emergency arrival bursts, shift conclusions, and network pool failovers.

---

## 3. Demo Baseline Distributions

| Variable | Target Baseline Ratio | Purpose in Simulator |
| :--- | :--- | :--- |
| **Modality Mix** | CT: 35%, XR: 40%, MRI: 15%, US: 10% | Generates heterogeneous service times and workload demands. |
| **Urgency Flags** | STAT: 10%, URGENT: 20%, ROUTINE: 70% | Creates realistic operational priority contrast for triage logic. |
| **Patient Location** | ED: 20%, Inpatient: 35%, Outpatient: 45% | Introduces emergency vs. elective workflow context. |
| **Staff Availability** | 5%–15% unavailable / off-shift | Forces failover and reassignment routing logic to execute. |
| **Initial Workload** | 20% staff near capacity, 60% moderate, 20% idle | Creates workload imbalance for RFO's engine to rebalance. |
| **Arrival Pattern** | Poisson baseline + Burst injections | Tests early-warning SLA bottleneck prediction logic. |

---

## 4. Scenario Library (S01 to S08)

| Scenario ID | Scenario Name | Injection Event | Expected RFO System Behavior |
| :--- | :--- | :--- | :--- |
| **S01** | **Normal Flow** | Standard arrival rate; staff fully available. | Balanced automated assignments; zero SLA alerts triggered. |
| **S02** | **Single Overload** | Single radiologist assigned 12+ cases rapidly. | Predictor detects queue buildup; system recommends reassignments. |
| **S03** | **Critical Backlog Bumping**| STAT ED Head CT arrives amidst routine backlog. | Priority Engine bumps STAT case to rank #1 ahead of routine studies. |
| **S04** | **Primary Reader Unavailability**| Primary reader goes offline mid-shift (`available=false`). | Reassignment timer triggers; cases fail over to eligible backup staff. |
| **S05** | **Cross-Facility Imbalance** | Hospital A overloaded; Hospital B idle. | System routes eligible Hospital A studies to Hospital B network pool. |
| **S06** | **Zero Capacity Escalation** | All qualified network readers at max capacity. | System triggers Level-4 visible escalation alert on dashboard. |
| **S07** | **Live Policy Change** | Operator updates STAT weight from $+50$ to $+70$. | System re-ranks pending worklist dynamically; updates reason codes. |
| **S08** | **Manual Human Override** | Operator manually assigns study to specific doctor. | System logs override reason, locks assignment, and updates audit trail. |

---

## 5. Generator Python Interface

```python
class SyntheticDataGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        
    def generate_workforce(
        self, 
        facilities: list[str], 
        headcount: int = 10
    ) -> list[dict]:
        """Generates synthetic radiologist roster with specialties and capacity limits."""
        pass

    def generate_orders(
        self, 
        start_time: str, 
        duration_mins: int = 60, 
        arrival_rate_per_min: float = 0.5
    ) -> list[dict]:
        """Generates stream of synthetic radiology orders matching baseline distributions."""
        pass

    def inject_event(
        self, 
        event_type: str, 
        target_id: str, 
        at_timestamp: str
    ) -> dict:
        """Injects dynamic shock events (e.g. UNAVAILABLE, BURST_ARRIVAL)."""
        pass
```

---

## 6. Determinism & Validation Criteria

1. **Seed Determinism**: Supplying the same integer `seed` generates identical order sequences and workforce initial states for repeatable judge demos.
2. **Schema Compliance**: 100% of generated JSON objects must strictly pass the `RadiologyOrder` and `Workforce` schemas.
3. **Referential Integrity**: All assigned `radiologist_id` values must correspond to existing active staff entries.
4. **No Real Data**: Strict enforcement of synthetic identifiers (`PAT-XXXX`, `RAD-XXXX`). Zero real patient records.
