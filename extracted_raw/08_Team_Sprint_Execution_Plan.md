08 — Team Sprint & Execution Plan

Turn the documents into a working prototype without scope creep

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Team Structure (6-person model)


| Role | Primary ownership | Secondary
| Backend / systems 1 | Data model, APIs, routing service | Integration
| Backend / systems 2 | Policies, events, simulation backend | Testing
| Frontend | Dashboard, worklist, alerts | UX
| ML/data | Synthetic generator, KPI calculations, optional forecast model | Data validation
| Domain/research | Workflow validation, terminology, evidence, scenario realism | QA
| PM/presenter | Scope, story, demo script, judge Q&A | Manual testing


# 2. Build Order

#3 Data Model   ↓#2 Architecture   ↓#5 Rules / Escalation   ↓#4 API Contract   ↓#6 Synthetic Data   ↓CODEParallel:#1 SRS   #7 Tech Note   #8 Sprint Plan

# 3. 36-Hour Example Plan


| Time | Backend | Frontend | ML/Data | Domain/PM | Gate
| 0–3h | Set project skeleton | UI skeleton | Define generator schema | Confirm workflow + glossary | Docs frozen v0.1
| 3–8h | Order/workforce APIs | Worklist + staff views | Generator + seeds | Scenario definitions | End-to-end data visible
| 8–14h | Routing engine | Assignment UI | Priority + KPI logic | Rule review | First assignment works
| 14–20h | Reassignment + events | Alerts + detail panel | Bottleneck forecast | Stress-test cases | Critical scenario works
| 20–26h | Escalation service | Analytics dashboard | Cross-facility simulation | Judge Q&A draft | Before/after metrics
| 26–31h | Integration + bugfix | Realtime + polish | Scenario replay | Demo script | Full demo path
| 31–34h | Hardening/tests | Visual polish | Data consistency | Compliance/safety story | No-showstopper defects
| 34–36h | Freeze build | Freeze UI | Freeze scenarios | Rehearse 2–3 min pitch | Final demo + backup video


# 4. Definition of Done for MVP

- A case can enter the system, be prioritized, assigned, and shown on the dashboard.

- A workforce availability change causes a visible reassignment or escalation.

- A predicted bottleneck alert appears before an injected SLA breach.

- An unresolved-capacity scenario escalates and remains visible.

- Every automatic action has a reason and event log.

- A before/after scenario produces measurable TAT/queue/load improvement in the simulator.

- The system can be reset and the full demo replayed in under 5 minutes.

# 5. Scope Freeze Rules

- No image diagnosis feature after architecture freeze.

- No new framework after first successful API-to-UI integration.

- No feature is accepted without a test scenario.

- Every new feature must trace to a problem-statement requirement or judge-facing differentiator.

# 6. Demo Story

- Show a normal balanced department.

- Inject a large arrival burst and overload one radiologist.

- System predicts an SLA risk before the breach.

- A critical case arrives; system prioritizes it and routes it to qualified available capacity.

- Make the primary radiologist unavailable; system reroutes an eligible case.

- Show cross-facility fallback and, finally, visible escalation when no capacity exists.

- End with before/after KPI cards: pending queue, predicted breaches, average TAT, workload imbalance.