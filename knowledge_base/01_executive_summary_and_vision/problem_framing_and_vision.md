# 01 — Problem Framing, Vision & Executive Summary

**Source Basis**: `Radiology_Workforce_PS_Analysis` & `00_Master_PreCode_Project_Plan.docx`

---

## 1. Executive Summary

The **RadFlow Orchestrator (RFO)** addresses radiology workflow blockages caused by workforce dependencies and personnel overload. In traditional hospital operations, diagnostic pipelines stall when critical workflow steps depend on specific individuals who become unavailable, off-shift, or overloaded. 

RFO is designed as an **intelligent operational orchestration middleware**. It accepts structured imaging work items, evaluates urgency, qualification, availability, and workload capacity, predicts potential SLA bottlenecks before they occur, automatically reallocates eligible work across local and network resources, and escalates unresolved cases transparently.

> [!CAUTION]
> **Core Scope Boundary**: The MVP is intentionally **NOT diagnostic AI**. It does not perform image interpretation, fracture detection, hemorrhage segmentation, or automated diagnosis. It is strictly a workflow control plane.

---

## 2. Problem Framing & System Response Matrix

| Source-Derived Concern | Real-World Operational Impact | RFO System Response |
| :--- | :--- | :--- |
| **Specific-Person Dependency** | Case stalls if assigned reader is sick, in surgery, or off-shift. | Failover pool & skill-compatible distributable routing engine. |
| **Manual / Non-Intelligent Triage** | Critical cases sit behind routine cases in FIFO queues. | Dynamic priority engine factoring STAT flag, location (ED), and SLA risk. |
| **Fragmented Tooling** | Operations lack a single pane of glass across RIS/PACS. | Clean adapter boundary & unified real-time operational dashboard. |
| **No Predictive Visibility** | Bottlenecks are discovered only *after* an SLA is breached. | Capacity forecast model alerting operators prior to deadline breach. |
| **Weak Escalation & Redundancy** | Cases are silently dropped or delayed indefinitely without alert. | Timer-based cascading escalation policy with immutable audit logging. |

---

## 3. Core Product Modules (Proposed Architecture)

The system consists of 11 core functional modules:

1. **Order Intake & Normalization**: Validates and normalizes incoming mock RIS/HIS orders.
2. **Operational Data Store**: Maintained active state of orders, workforce roster, and event history.
3. **Priority Engine**: Evaluates metadata to calculate dynamic urgency scores.
4. **Eligibility / Qualification Engine**: Matches case modality/exam type against staff specialty matrices.
5. **Workload & Capacity Engine**: Tracks real-time active case count against max capacity thresholds.
6. **Routing / Reassignment Engine**: Scores candidate radiologists and handles automated failover.
7. **Bottleneck Predictor**: Forecasts queue completion times against SLA deadlines.
8. **Escalation & Notification Layer**: Triggers multi-level alerts when cases stall.
9. **Live Operations Dashboard**: Exposes real-time worklist, staff load, and KPI cards.
10. **Analytics & Audit Layer**: Records timestamped immutable event logs for every decision.
11. **Scenario Simulator**: Injects synthetic traffic, overload events, and unavailability to demonstrate value live.

---

## 4. Innovation Differentiators

* **Predictive Rather Than Reactive**: Detects queue buildup and forecasts SLA breaches *before* a failure occurs.
* **Cross-Facility Capacity Pooling**: Models eligible remote/teleradiology resources across multi-facility networks.
* **Explainable Automation**: Every routing and reassignment decision exposes explicit human-readable reason codes (e.g., `STAT_PRIORITY + SKILL_MATCH + LOW_WORKLOAD`).
* **Resilient Failover**: Automatic reassignment timers ensure zero silent case drops.
* **Demonstrable Value**: Embedded simulator proves TAT reduction and bottleneck prevention in live demo scenarios.

---

## 5. MVP Boundary (Build vs. Do Not Build)

To maintain focus and avoid scope creep during hackathon execution, the boundary is strictly enforced:

| Build (In Scope) | Do Not Build (Red Lines) |
| :--- | :--- |
| Synthetic RIS order feed | Real hospital EHR/RIS direct production integration |
| Operational metadata processing | Clinical image interpretation (DICOM pixel AI) |
| Skill- & load-aware routing engine | Automated clinical diagnosis |
| Predictive SLA bottleneck alerts | Clinical outcome prediction claims |
| Cascading escalation timers | Production WhatsApp / SMS integrations (use stubs) |
| Real-time React operations dashboard | Full replacement RIS or PACS system |
| Immutable JSON audit event log | Real patient identifiers (synthetic data only) |

---

## 6. Key Performance Indicator (KPI) Framework

| KPI | Baseline (Simulator Without RFO) | Target Demonstration (With RFO) |
| :--- | :--- | :--- |
| **Average Turnaround Time (TAT)** | Scenario-dependent backlog buildup | Demonstrate measurable reduction after intelligent rerouting. |
| **SLA Breaches** | High count during overload bursts | Demonstrate near-zero breaches via early reassignment. |
| **Predicted Bottlenecks** | Zero early warning | Alert operators before injected SLA deadlines expire. |
| **Workload Imbalance** | High variance (some staff overwhelmed, others idle) | Demonstrate equitable load distribution across eligible pool. |
| **Reassignment Latency** | Manual intervention (minutes/hours) | Automated decision executed within seconds of trigger. |
| **Unresolved Critical Cases** | Silent queue drop / stall | 100% visible escalation to administrative dashboard. |

---

## 7. Judge Narrative & Positioning

> "We are not building another hospital UI dashboard, and we are not replacing radiologists with diagnostic AI. We are building the **operational control plane** between incoming imaging demand and available qualified capacity. The system understands who can do what, who is available, who is overwhelmed, which study is urgent, where a bottleneck is forming, and what fallback must occur when human dependencies fail."

---

## 8. Non-Negotiable Engineering Rules

1. **Traceability**: Every requirement must trace directly to workforce-dependent blockage.
2. **No Diagnostic Claims**: Never claim the system reads X-rays, CTs, or MRIs.
3. **Synthetic Privacy**: 100% synthetic patient data; zero real PHI.
4. **Zero Silent Failures**: No case may ever vanish or stall without an active escalation trigger.
5. **Full Explainability**: No black-box automated assignments; reason codes are mandatory.
6. **Configurable Thresholds**: Priority weights, overload ratios, and SLA timers must remain policy-driven.
