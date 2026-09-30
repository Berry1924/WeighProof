# 08 — Team Sprint & Execution Plan

**Source Basis**: `08_Team_Sprint_Execution_Plan.docx`

---

## 1. Team Role Allocation (6-Person Model)

| Team Member | Primary Role | Primary Ownership | Secondary Responsibility |
| :--- | :--- | :--- | :--- |
| **Eng 1** | Backend / Systems Lead | Operational Data Store, FastAPI endpoints, Core Routing Engine. | Database migrations & Docker setup. |
| **Eng 2** | Backend / Rules Engineer | Priority Engine, Escalation Service, Audit Event Logging. | Pytest integration tests. |
| **Eng 3** | Frontend Lead | React Dashboard, Real-Time Worklist, Alerts & Analytics UI. | UX polish & WebSockets integration. |
| **Eng 4** | ML / Data Engineer | Synthetic Data Generator, Scenario Library (`S01`–`S08`), KPI math. | Data validation scripts. |
| **Eng 5** | Domain & QA Lead | Clinical workflow validation, rule calibration, stress testing. | Documentation & QA review. |
| **Eng 6** | PM / Presenter | Scope enforcement, slide deck, demo script, judge Q&A prep. | Pitch rehearsal & video backup. |

---

## 2. 36-Hour Sprint Execution Plan

```mermaid
gantt
    title 36-Hour Hackathon Execution Timeline
    dateFormat  HH:mm
    axisFormat %Hh
    
    section Foundation
    Docs & Skeleton Setup      :00:00, 3h
    section Core Build
    Intake APIs & Basic UI     :03:00, 5h
    Routing Engine & Assign    :08:00, 6h
    section Advanced Features
    Reassignment & Forecast    :14:00, 6h
    Escalation & Analytics     :20:00, 6h
    section Polish & Freeze
    Integration & Realtime     :26:00, 5h
    Hardening & Verification   :31:00, 3h
    Code Freeze & Pitch Prep   :34:00, 2h
```

### Detailed Milestone Breakdown

| Hours | Backend Tasks | Frontend Tasks | Data/Simulator Tasks | PM/Domain Tasks | Milestone Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0–3h** | Initialize FastAPI skeleton & Postgres DB schema. | Initialize React + Vite project & component layout. | Write generator schema & seed manager. | Confirm terminology, SRS requirements & glossary. | **Gate 0**: Architecture & Data Contract Frozen (`v0.1`). |
| **3–8h** | Build `/orders` and `/workforce` CRUD APIs. | Build active worklist table & staff roster view. | Implement synthetic order/staff generator. | Define detailed scenario parameters (`S01`–`S08`). | **Gate 1**: End-to-end synthetic data visible on UI. |
| **8–14h** | Implement Priority & Candidate Ranking logic. | Add manual assignment UI & candidate modal. | Implement priority score math & KPI calculations. | Review candidate scoring weights with team. | **Gate 2**: Automated study assignment functional. |
| **14–20h**| Build auto-reassignment & audit event store. | Build alert banners & detail panel view. | Implement queue service time forecast logic. | Stress-test failure scenarios (`S02`–`S04`). | **Gate 3**: Critical failover scenario operational. |
| **20–26h**| Implement 5-tier escalation service & timers. | Build analytics KPI dashboard & charts view. | Implement cross-facility simulation logic. | Draft judge Q&A answer deck & slides. | **Gate 4**: Before/after KPI analytics functional. |
| **26–31h**| Connect WebSocket pub/sub for real-time state. | Connect WebSockets; polish UI layout & dark mode. | Verify scenario reset & determinism. | Draft 2-minute demo pitch script. | **Gate 5**: Full demo scenario path verified. |
| **31–34h**| Bug fixes, performance tuning & API test run. | Visual polish, error toasts & empty states. | Verify 100% schema validation compliance. | Rehearse live presentation & record backup. | **Gate 6**: Code Freeze; Zero major bugs. |
| **34–36h**| **Code Freeze** | **UI Freeze** | **Scenario Freeze** | Final pitch rehearsals & demo setup. | **Gate 7**: Ready for Judge Presentation. |

---

## 3. Definition of Done (DoD) for MVP

1. **End-to-End Pipeline**: A study can be ingested via API, prioritized, matched to a qualified reader, assigned, and rendered live on the dashboard.
2. **Dynamic Reassignment**: Toggling radiologist availability (`available=false`) triggers automatic reassignment with a logged audit event.
3. **Early Warning Alert**: Injecting a traffic burst displays a predicted SLA breach banner *before* deadline expiration.
4. **Escalation Guarantee**: An unassigned critical study progresses through escalation levels to a visible admin alert state.
5. **Measurable Value**: Running scenario `S02` demonstrates measurable reduction in average TAT and SLA breach count.
6. **Demo Replayability**: The demo state can be reset to baseline seed and replayed reliably in $< 5$ minutes.

---

## 4. Scope Freeze Guidelines

* **No Image Reading**: Zero image AI features allowed after architecture freeze.
* **No Framework Churn**: No new frontend/backend frameworks after Hour 8.
* **Traceability Requirement**: Every new feature request must trace directly to an SRS requirement or judge differentiator.

---

## 5. Live Demo Pitch Script (2 Minutes)

```
[0:00 - 0:20] THE PROBLEM
"Every day, hospital diagnostic pipelines stall—not because images aren't taken, but because critical studies sit in unmanaged queues waiting for overloaded or unavailable radiologists."

[0:20 - 0:45] THE SOLUTION
"Meet RadFlow Orchestrator (RFO)—an intelligent operational control plane. RFO evaluates skill eligibility, workload capacity, urgency metadata, and SLA deadlines in real time to route work to qualified, available capacity across hospital networks."

[0:45 - 1:20] LIVE DEMO (SCENARIOS S02 -> S04)
"Watch what happens live: We inject an emergency CT burst. RFO's predictor forecasts an SLA bottleneck 15 minutes before breach. When Dr. Lin goes offline, RFO's failover automatically reassigns her urgent studies to an eligible network reader, logging an explainable audit reason code."

[1:20 - 1:45] MEASURABLE IMPACT
"Here on our analytics panel, RFO reduced average turnaround time by 34% and eliminated unhandled SLA breaches—guaranteeing zero silent drops."

[1:45 - 2:00] CONCLUSION & CALL TO ACTION
"RFO turns radiology operations from reactive crisis management into preventive, explainable orchestration. Thank you."
```
