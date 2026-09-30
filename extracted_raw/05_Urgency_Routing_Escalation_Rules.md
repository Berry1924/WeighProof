05 — Urgency, Routing & Escalation Rules Specification

The safety-critical logic to agree on before coding

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Design Principle

The decision engine is operational, explainable, configurable, and human-overridable. It does not interpret images. Priority inputs are structured workflow metadata only.

# 2. Priority Model (MVP)


| Factor | Example weight | Meaning
| Urgency flag: STAT | +50 | Clinician/system explicitly marks as time-critical.
| Urgency flag: URGENT | +30 | Higher operational priority than routine.
| ED / emergency location | +15 | Operational context increases routing priority.
| Near SLA breach (<20 min) | +25 | Prevents known deadline miss.
| Near SLA breach (<10 min) | +40 | Strong escalation trigger.
| Routine | +0 | No priority boost.
| Manual override | Configurable | Authorized human override with reason.



| ImportantWeights above are a proposed demo policy, not clinical guidance. They must be configurable and must not be presented as universal hospital rules.


# 3. Candidate Ranking Logic

For each incoming/re-routing case:1. Filter by eligibility (specialty/skill/facility permissions).2. Filter by availability.3. Compute workload ratio = current_active_cases / max_active_cases.4. Compute SLA risk for the case.5. Rank candidates using:   candidate_score = capability + availability + lower_workload + continuity - risk_penalties6. Select highest-ranked eligible candidate.7. Record reason codes and policy version.Never assign to an ineligible or unavailable resource.

# 4. Bottleneck Prediction

For the MVP, prediction is best implemented as a transparent operational forecast rather than a black-box model.

Conceptual forecast inputs:- pending cases assigned to resource- average estimated service time for those cases- new-case arrival rate- remaining shift time- current SLA deadlines- availability of backup resourcesTrigger alert when:forecast_finish_time > configured SLA deadlineORworkload_ratio > overload_thresholdORcritical_case_wait > critical_wait_threshold

# 5. Escalation Cascade

LEVEL 0  Assigned resource   ↓ no acceptance / overloadLEVEL 1  Qualified in-house backup   ↓ no acceptanceLEVEL 2  Qualified network / teleradiology resource   ↓ no capacityLEVEL 3  Shift-in-charge / duty officer alert   ↓ unresolvedLEVEL 4  Visible unresolved-critical state on admin dashboardEvery level generates an audit event.No level may silently discard the case.

# 6. Manual Override

- Authorized operator can change assignment/priority.

- A reason is mandatory.

- System stores before/after state, actor, timestamp, policy version and reason.

- Automations never overwrite a human override without an explicit new event.

# 7. Safety / Judge Stress Cases


| Scenario | Expected behavior
| Two hospitals both overloaded | Choose only from eligible available capacity; if none, escalate visibly.
| Only ineligible radiologist available | Do not assign; escalate.
| Primary reader goes offline after assignment | Trigger reassignment timer.
| Critical case arrives during routine backlog | Priority engine moves it ahead operationally; no image interpretation involved.
| Routing service fails | Case remains visible; system alert; no silent drop.
| Clinician priority appears inconsistent | Honor configured policy but preserve manual override/audit path; do not invent a diagnosis.


# 8. Decision Explainability Template

Decision: ASSIGN RAD-002Reasons: eligible_specialty, available_now, workload_ratio=0.58, STAT_priority, SLA_risk=HIGHPolicy: v1.0Alternative considered: RAD-001 (overloaded, excluded)