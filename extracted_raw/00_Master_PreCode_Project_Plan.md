00 — Master Pre-Code Project Plan

What we are building, why, and how every engineering document connects

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# Executive Summary

The project addresses radiology workflow blockage caused by workforce dependency. The system is designed as an intelligent orchestration layer: it accepts structured work items, evaluates urgency, qualification, availability and workload, predicts bottlenecks, reallocates eligible work, and escalates unresolved cases. The MVP is intentionally not diagnostic AI.


| Problem → ProductProblem: the diagnostic pipeline can stall when critical workflow steps depend on specific people who become unavailable or overloaded. Product: a real-time workforce-aware orchestration layer that keeps cases moving and exposes bottlenecks before they become failures.


# 1. Evidence-Backed Problem Framing


| Source-derived concern | Implication for our build
| Specific-person dependency | Need failover and distributable routing.
| Manual/non-intelligent triage | Need explicit priority logic.
| Fragmented tooling | Need adapter boundary and unified operational view.
| No predictive visibility | Need forecast/early-warning layer.
| Weak escalation/redundancy | Need timer-based cascade and audit trail.


# 2. Proposed Product Modules

- Order Intake & Normalization

- Operational Data Store

- Priority Engine

- Eligibility/Qualification Engine

- Workload & Capacity Engine

- Routing/Reassignment Engine

- Bottleneck Predictor

- Escalation & Notification Layer

- Live Operations Dashboard

- Analytics & Audit Layer

- Scenario Simulator

# 3. What Makes It Innovative (Proposed)

- Predictive rather than merely reactive: forecast a blockage before an SLA breach.

- Cross-facility rather than single-department: model an eligible resource pool across facilities.

- Explainable rather than opaque: every decision shows factors and policy version.

- Resilient rather than person-dependent: automatic failover and visible escalation.

- Demonstrable rather than conceptual: scenario simulator proves the benefit in real time.

# 4. MVP Boundary


| Build | Do not build
| Synthetic RIS feed | Real hospital connection
| Operational metadata | Clinical image interpretation
| Routing + load balancing | Automated diagnosis
| Bottleneck prediction | Claimed clinical outcome prediction
| Escalation + alerts | Unverified WhatsApp production workflow
| Live dashboard | Replacement RIS/PACS
| Audit trail | Real patient data


# 5. KPI Framework


| KPI | Baseline in simulator | Target for demo
| Average TAT | Scenario-dependent | Show measurable reduction after rerouting.
| SLA breaches | Scenario-dependent | Demonstrate fewer breaches.
| Predicted bottlenecks | Count | Alert before injected deadline.
| Workload imbalance | Max/min or variance | Demonstrate reduction.
| Reassignment response | Seconds/minutes | Meet configured demo threshold.
| Unresolved critical cases | Count | Never silently lost; escalated visibly.


Use relative improvement and scenario-specific values rather than inventing a universal real-world percentage.

# 6. Judge Narrative

We are not building another hospital dashboard and we are not replacing radiologists.We are building the operational control layer between incoming imaging work and available qualified capacity.The system understands who can do what, who is available, who is overloaded, which case is urgent,where a bottleneck is forming, and what fallback should happen when a dependency fails.

# 7. Traceability Matrix


| Need | SRS | Architecture | Data | API | Rules | Simulator | Sprint
| Work intake | FR-01 | Intake layer | Order | POST /orders | Priority input | Generator | 3–8h
| Smart routing | FR-05/06 | Routing engine | Workforce + Order | PUT reassign | Candidate ranking | Overload scenario | 8–20h
| Prediction | FR-07 | Predictor | Operational history | GET alerts | Forecast trigger | Burst scenario | 14–26h
| Escalation | FR-08 | Escalation layer | Events | GET/ACK alerts | Cascade | No-capacity scenario | 14–26h
| Trust | FR-10/11 | Audit | Event | Order details | Explainability | Override scenario | 20–34h


# 8. Non-Negotiable Rules for the Team

- Everything must trace back to the problem of workforce-dependent blockage.

- No diagnosis claims.

- No real patient data in the prototype.

- No silent failure.

- No opaque routing decision that the presenter cannot explain.

- All thresholds remain configurable because facility policies vary.

- Build modularly so judges can change a rule live.

# 9. Next Gate Before Coding


| Go / No-Go checklistThe team is allowed to code only after the team agrees on: canonical data schema, architecture boundaries, priority/routing/escalation rules, API contracts, simulator scenarios, tech stack, and the first demo narrative. If any of these are undecided, coding will create rework.
