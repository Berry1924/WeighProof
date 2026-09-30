02 — System Architecture & Design Document

The single source of truth for how the MVP works

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Architectural Goal

Create a middleware/orchestration layer that can sit conceptually between a hospital workflow feed and workforce operations. For the hackathon, the intake is simulated and the routing engine is real. The image interpretation layer is deliberately absent.

# 2. Logical Architecture

                    ┌──────────────────────────┐                    │      Mock RIS Feed        │  ← simulated intake                    └────────────┬─────────────┘                                 │ orders/events                                 ▼                    ┌──────────────────────────┐                    │ Intake + Validation API  │                    └────────────┬─────────────┘                                 ▼                    ┌──────────────────────────┐                    │ Operational Data Store   │                    │ orders / staff / events  │                    └────────────┬─────────────┘                                 ▼             ┌────────────────────────────────────────┐             │ Workflow Decision Layer               │             │ 1) priority  2) eligibility           │             │ 3) workload   4) capacity prediction  │             └──────────────┬──────────────┬─────────┘                            │              │                    routing │              │ alerts                            ▼              ▼                 ┌────────────────┐  ┌──────────────────┐                 │ Routing Engine │  │ Escalation Layer │                 │ assign/reassign│  │ timers/notify    │                 └───────┬────────┘  └─────────┬────────┘                         │                     │                         └──────────┬──────────┘                                    ▼                          ┌────────────────────┐                          │ Real-time Dashboard │                          │ worklist / KPIs     │                          └────────────────────┘                                    │                                    ▼                           ┌─────────────────┐                           │ Audit/Event Log │                           └─────────────────┘   Integration boundary (future/adapter): HL7/FHIR order feeds + DICOM metadata.   Production deployment and real-system integration are NOT claimed in the MVP.

# 3. Component Responsibilities


| Component | Responsibility | Real in MVP?
| Mock RIS feed | Generate/submit synthetic orders and status events. | Yes
| Intake API | Validate schema, normalize, persist event. | Yes
| Operational store | Persist orders, staff, policies, events. | Yes
| Priority engine | Compute explainable operational priority from structured metadata. | Yes
| Qualification engine | Check specialty/skill compatibility. | Yes
| Workload engine | Compute active queue/load/capacity. | Yes
| Routing engine | Rank eligible resources and perform assignment/reassignment. | Yes
| Bottleneck predictor | Estimate risk of SLA breach from configurable workload inputs. | Yes
| Escalation service | Trigger notification stubs and escalation states. | Yes
| Dashboard | Visualize worklist, load, alerts, analytics, simulation. | Yes
| RIS/PACS adapters | Real production integration. | No; interface only
| Diagnostic AI | Interpret images. | No


# 4. Core Data Flow

- Order arrives through mock RIS feed.

- Input schema is validated and normalized.

- Order enters active worklist.

- Priority and SLA state are calculated.

- Eligible radiologists are identified from skill + availability.

- Routing engine scores candidates and assigns the best available resource.

- Workload monitor updates queue state continuously.

- Predictor evaluates potential SLA breach.

- If risk exceeds threshold, system creates an alert/reassignment recommendation.

- If a case is not accepted within the escalation timer, the next escalation step is triggered.

- Every automated transition creates an audit event.

# 5. Innovation Layer (Proposed)


| Innovation | What is different | Why it matters
| Predict-before-blockage | Forecast likely SLA breach before backlog is visible as a crisis. | Moves operations from reactive to preventive.
| Skill + load + urgency routing | Do not route only by shortest queue; require eligibility and policy-aware priority. | Reduces unsafe/naive routing.
| Cross-facility capacity pool | Treat eligible remote/teleradiology resources as a network pool in the simulation. | Addresses distribution imbalance.
| Explainable decisions | Every automated route exposes reasons/factors. | Improves trust and judge defensibility.
| What-if simulator | Operator can create overload/unavailability and compare outcomes. | Makes the value measurable live on stage.
| Admin transparency | Expose TAT, SLA risk, workload imbalance and bottleneck causes. | Turns the system into an operational control plane, not a passive dashboard.


# 6. Failure Handling

- No eligible local resource → search configured network pool.

- No eligible network resource → escalate to on-call/admin; leave case unresolved and visible.

- Dashboard unavailable → backend state and APIs remain authoritative.

- Routing engine error → preserve case in current state and raise system alert; do not silently reassign or drop.

- Conflicting policies → highest-priority safety policy wins; record policy/version in audit event.

# 7. Architecture Decisions to Defend

- Middleware, not RIS/PACS replacement: lowers integration scope and preserves existing hospital systems.

- Structured metadata, not image AI: keeps MVP focused on workflow blockage and avoids diagnostic claims.

- Configurable policy engine: allows facility-specific definitions of priority, SLA, specialty, and escalation.

- Event/audit model: enables reproducibility for judge Q&A and future production governance.