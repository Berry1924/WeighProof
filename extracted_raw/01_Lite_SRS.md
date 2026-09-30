01 — Lite Software Requirements Specification

What the system must do — testable, traceable, and scope-controlled

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Product Definition

Working product name: RadFlow Orchestrator (RFO). Purpose: reduce radiology workflow blockage caused by dependence on specific or overloaded personnel by prioritizing, routing, monitoring, predicting, and escalating work. The MVP is an operations/workflow layer, not diagnostic AI.


| Core product promiseKeep the radiology pipeline moving even when a particular human link becomes unavailable or overloaded, while never silently dropping a case.


# 2. Scope

- In scope: synthetic radiology-order intake, urgency metadata, skills/availability/workload modeling, explainable routing, reassignment, bottleneck prediction, SLA monitoring, escalation, live dashboard, audit trail, simulation controls.

- Out of scope for MVP: image interpretation, fracture/hemorrhage detection, automated diagnosis, replacement of RIS/PACS, real patient data, autonomous clinical decision-making.

# 3. Functional Requirements


| ID | Area | Requirement | Acceptance evidence
| FR-01 | Order intake | System shall accept a new radiology order containing exam ID, modality, priority metadata, order time, facility, and SLA deadline through a mock RIS/API feed. | API returns success; order appears on worklist.
| FR-02 | Worklist | System shall display all active studies with status, urgency, wait time, SLA state, assigned resource, and facility. | User can filter/sort and every active order has a visible status.
| FR-03 | Qualification check | System shall consider radiologist specialty/skill eligibility before assigning a case. | No automatic assignment is made to an ineligible resource.
| FR-04 | Availability check | System shall exclude unavailable resources from automatic routing and show the reason. | Unavailable staff are not selected by routing engine.
| FR-05 | Load-aware routing | When multiple eligible resources exist, system shall rank them using configurable workload + availability + urgency + specialty rules. | Routing decision contains a human-readable reason code.
| FR-06 | Auto-reassignment | When an assigned radiologist becomes unavailable or crosses a configured overload threshold, system shall attempt reassignment within a configurable response target. | Order moves to next eligible resource or escalation state.
| FR-07 | Bottleneck prediction | System shall flag a likely SLA breach before the deadline using queue size, estimated service time, priority, and available capacity. | Alert appears before breach and records forecast timestamp.
| FR-08 | Escalation | If no eligible resource accepts a critical case within the configured timer, system shall escalate through the configured chain and never silently close/drop the case. | Each escalation step is timestamped and auditable.
| FR-09 | Admin analytics | System shall show average TAT, pending volume, SLA breaches, workload distribution, reassignment count, and bottleneck frequency. | Metrics update from the same operational dataset used by the routing engine.
| FR-10 | Audit trail | System shall record routing/reassignment/escalation events with actor/system, timestamp, previous state, new state, and reason code. | Every state-changing automation produces an audit event.
| FR-11 | Manual override | Authorized users shall be able to override an automated assignment and provide a reason. | Override requires reason and is preserved in audit log.
| FR-12 | Simulation mode | System shall allow demo operators to inject cases, staff availability changes, overload events, and network-wide capacity changes. | Scenario can be reproduced on demand without real patient data.


# 4. Non-Functional Requirements


| NFR | Area | Requirement | MVP target
| NFR-01 | Trust | Every routing decision shows the factors/rules that caused it. | Reason code + top factors visible.
| NFR-02 | Responsiveness | Live worklist reflects operational changes quickly. | Target near-real-time for demo; exact production target to be validated.
| NFR-03 | Safety | System never silently drops a case. | Escalation timer + unresolved-case alert.
| NFR-04 | Configurability | Priority, overload, SLA and escalation thresholds are configurable. | Admin-configurable policy JSON/table.
| NFR-05 | Auditability | Automated decisions are reconstructable. | Immutable-style event records in MVP.
| NFR-06 | Privacy | Prototype uses synthetic identifiers and mock clinical metadata. | No real patient identifiers.
| NFR-07 | Interoperability | System exposes a clear adapter boundary for RIS/FHIR/HL7 and DICOM metadata. | Mock connector documented; real integration not claimed.
| NFR-08 | Availability | Core routing service can continue if dashboard UI is temporarily disconnected. | Backend decision path remains callable via API.


# 5. Traceability to Problem Statement


| Problem statement concern | System response
| Specific-person dependency | Skill-aware routing + backup pool + failover
| Manual/non-intelligent triage | Explainable priority engine
| No predictive visibility | Bottleneck forecast
| Cross-facility imbalance | Facility-aware capacity pool
| Weak escalation/redundancy | Cascading escalation + audit
| Administrative overload | Workflow visibility + redistribution


# 6. Scope Guardrails


| Red lineDo not add an image-reading model just to make the project look more like AI. The uploaded analysis explicitly frames the winning scope as workflow/orchestration, not diagnostic AI.
