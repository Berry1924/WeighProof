03 — Data Model & Schema Specification

Exact contracts shared by backend, frontend, simulator, and analytics

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Design Principle

Define the shared data contract before coding. Every service should consume the same canonical radiology-order object and the same workforce object. Patient identifiers are synthetic in the MVP.

# 2. Canonical Order Object

{  "exam_id": "RAD-000123",  "facility_id": "FAC-CHN-01",  "synthetic_patient_id": "PAT-00421",  "modality": "CT",  "exam_type": "HEAD_CT",  "urgency_flag": "STAT",  "clinician_priority": "HIGH",  "order_time": "2026-09-07T09:15:00+05:30",  "sla_minutes": 30,  "sla_deadline": "2026-09-07T09:45:00+05:30",  "status": "PENDING",  "assigned_radiologist_id": null,  "eligible_specialties": [    "NEURORADIOLOGY",    "EMERGENCY"  ],  "patient_location": "ED",  "created_by": "MOCK_RIS",  "routing_policy_version": "v1.0",  "metadata": {    "arrival_source": "RIS_SIM",    "referring_unit": "EMERGENCY"  }}

# 3. Order Field Dictionary


| Field | Type | Required | Meaning / rule
| exam_id | string | Yes | Unique study/work item identifier.
| facility_id | string | Yes | Origin facility code.
| synthetic_patient_id | string | Yes (MVP) | Synthetic identifier only; never real patient identifiers.
| modality | enum | Yes | CT/MRI/XR/US in MVP; configurable.
| exam_type | string | Yes | Operational exam category.
| urgency_flag | enum | Yes | STAT / URGENT / ROUTINE; based on structured order metadata.
| clinician_priority | enum | Yes | Priority supplied by ordering workflow.
| order_time | datetime | Yes | Timestamp of order intake.
| sla_minutes | integer | Yes | Configured target duration for the case class.
| sla_deadline | datetime | Yes | Derived deadline.
| status | enum | Yes | PENDING/ASSIGNED/IN_PROGRESS/COMPLETED/ESCALATED/CANCELLED.
| assigned_radiologist_id | string/null | No | Current responsible resource.
| eligible_specialties | array[string] | Yes | Allowed specialty set for routing.
| patient_location | enum/string | Yes | ED/INPATIENT/OUTPATIENT/etc.; used operationally.
| created_by | string | Yes | Source system identifier.
| routing_policy_version | string | Yes | Policy version used for decisions.
| metadata | object | No | Simulator fields and extension data.


# 4. Workforce Object

{  "radiologist_id": "RAD-002",  "display_name": "Dr. B",  "facility_ids": [    "FAC-CHN-01",    "FAC-CHN-02"  ],  "specialties": [    "GENERAL",    "EMERGENCY"  ],  "available": true,  "status": "ACTIVE",  "max_active_cases": 12,  "current_active_cases": 7,  "on_call": true,  "shift_end": "2026-09-07T18:00:00+05:30"}


| Field | Type | Purpose
| radiologist_id | string | Stable resource identifier.
| display_name | string | Dashboard label.
| facility_ids | array | Facilities the resource may serve.
| specialties | array | Eligibility matching.
| available | boolean | Real-time availability flag.
| status | enum | ACTIVE/PAUSED/OFFLINE/ON_CALL.
| max_active_cases | integer | Configurable load ceiling for the demo.
| current_active_cases | integer | Current workload.
| on_call | boolean | Escalation eligibility.
| shift_end | datetime | Capacity forecast boundary.


# 5. Event/Audit Object

{  "event_id": "EV-00091",  "exam_id": "RAD-000123",  "event_type": "AUTO_REASSIGNMENT",  "actor_type": "SYSTEM",  "actor_id": "ROUTER-01",  "timestamp": "2026-09-07T09:32:14+05:30",  "from_resource": "RAD-001",  "to_resource": "RAD-002",  "reason_code": "OVERLOAD_AND_SLA_RISK",  "policy_version": "v1.0",  "details": {    "queue_size_before": 14,    "estimated_breach_minutes": 8  }}

# 6. Status State Machine

PENDING → ASSIGNED → IN_PROGRESS → COMPLETED   │          │              │   │          ├──────────────┘   │          └→ ESCALATED ─→ ASSIGNED / COMPLETED   └→ CANCELLEDRules:- PENDING means not currently owned.- ASSIGNED means a qualified resource accepted ownership.- ESCALATED means SLA/acceptance policy was triggered.- COMPLETED is terminal for the MVP.- CANCELLED is terminal only when a valid cancellation event exists.

# 7. Data Quality Rules

- exam_id must be unique.

- order_time must be <= current simulation time.

- sla_deadline must equal order_time + sla_minutes unless a policy override is recorded.

- assigned_radiologist_id must be null for PENDING and valid for ASSIGNED/IN_PROGRESS.

- A radiologist cannot be assigned if available=false or eligibility check fails.

- Every automated reassignment must produce an event object.

- Simulator must preserve referential integrity between orders, staff, and events.