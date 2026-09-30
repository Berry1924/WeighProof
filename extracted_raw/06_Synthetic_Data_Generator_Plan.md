06 — Synthetic Data Generator Plan

Create realistic operational traffic without real patient data

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Purpose

Because direct workflow-blockage datasets are not available for this project, the MVP uses synthetic operational data. The simulator is a product component: it creates repeatable traffic, stress cases, and measurable before/after scenarios.

# 2. Synthetic Entities

- Facilities: urban hospital, tier-2/3 hospital, optional network partner.

- Radiologists: varied specialties, availability, workload ceilings, shifts.

- Orders: modality, exam type, priority, arrival time, SLA, facility, assignment.

- Events: assignment, completion, unavailability, escalation, reassignment.

# 3. Proposed Demo Distributions


| Calibration ruleThe values below are simulation assumptions for demo generation, not claims about real hospitals. The team should label them as configurable assumptions and later tune them using published workflow research or hospital-partner data.



| Variable | Starting assumption | Why included
| Modality mix | CT 35%, XR 40%, MRI 15%, US 10% | Creates heterogeneous workload.
| Urgency | STAT 10%, URGENT 20%, ROUTINE 70% | Creates realistic operational priority contrast.
| Location | ED 20%, inpatient 35%, outpatient 45% | Creates emergency vs routine contexts.
| Staff availability | 5–15% unavailable at any snapshot | Creates failover scenarios without making system impossible.
| Workload | A few resources near capacity + several moderately loaded | Creates imbalance for the routing engine to resolve.
| Arrival pattern | Burst + baseline | Allows bottleneck prediction to be demonstrated.
| SLA miss risk | Generated from workload + priority + capacity | Creates measurable forecast events.


# 4. Scenario Library


| Scenario ID | Scenario | Expected system behavior
| S01 | Normal flow | Balanced assignment, no alert.
| S02 | Single radiologist overload | Predict risk and propose reassignments.
| S03 | Critical case enters routine backlog | Prioritize and assign to eligible capacity.
| S04 | Primary reader unavailable | Automatic failover to qualified backup.
| S05 | Two facilities imbalanced | Cross-facility routing recommendation.
| S06 | No eligible capacity anywhere | Escalate and show unresolved state.
| S07 | Rule change live | Policy version changes routing explanation.
| S08 | Manual override | Human decision supersedes automation and is audited.


# 5. Generator Interface

generate_orders(  start_time,  duration_minutes,  arrival_rate,  modality_mix,  urgency_mix,  facility_mix,  seed)generate_workforce(  facilities,  headcount_range,  specialty_mix,  availability_pattern,  capacity_range,  seed)inject_event(  event_type = UNAVAILABLE | OVERLOAD | BURST | RECOVER,  target_id,  at_time)

# 6. Reproducibility

- Every scenario has a seed.

- The demo can reset to a known baseline.

- The same seed reproduces the same order/workforce state.

- Scenario logs can be exported for judge evidence.

# 7. Validation of the Simulator


| Check | Acceptance
| Schema validity | 100% generated orders pass the data model schema.
| Referential integrity | All assigned resources exist and are eligible when assignment occurs.
| Scenario determinism | Same seed produces same key events.
| Stress behavior | System visibly creates backlog and clears or escalates it according to policy.
| No real data | Synthetic IDs only.
