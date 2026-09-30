04 — API Contract

Backend/frontend agreement before implementation

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. API Principles

- JSON over HTTP for MVP.

- All endpoints return a stable envelope: {data, error, meta}.

- API decisions expose reason codes so the UI can explain them.

- IDs are stable and synthetic.

- Authentication/authorization may be stubbed for hackathon, but actor identity is carried in audit events.

# 2. Endpoint Catalogue


| Method | Endpoint | Purpose | Primary response
| POST | /orders | Create order from mock RIS. | Order + initial routing state
| GET | /orders | List/filter active orders. | Paginated worklist
| GET | /orders/{exam_id} | Get one order + audit timeline. | Order details
| PUT | /orders/{exam_id}/reassign | Manually or automatically reassign. | Updated assignment + reason
| GET | /workforce | List current workforce/capacity. | Staff statuses + load
| PUT | /workforce/{id}/availability | Simulation/admin availability change. | Updated staff record
| GET | /alerts | Get active bottleneck/escalation alerts. | Alert list
| POST | /alerts/{id}/ack | Acknowledge alert. | Alert state
| GET | /analytics/summary | Operational KPIs. | TAT/SLA/load metrics
| POST | /simulation/events | Inject demo scenario. | Scenario execution result
| GET | /policies | Read routing/priority policy. | Policy config
| PUT | /policies | Update policy for demo. | Versioned policy


# 3. Core Request/Response Shapes

POST /ordersRequest:{  "exam_id": "RAD-000123",  "facility_id": "FAC-CHN-01",  "modality": "CT",  "exam_type": "HEAD_CT",  "urgency_flag": "STAT",  "clinician_priority": "HIGH",  "order_time": "2026-09-07T09:15:00+05:30",  "sla_minutes": 30,  "eligible_specialties": ["NEURORADIOLOGY", "EMERGENCY"],  "patient_location": "ED"}Response:{  "data": {    "exam_id": "RAD-000123",    "status": "ASSIGNED",    "assigned_radiologist_id": "RAD-002",    "routing_reason": "ELIGIBLE + AVAILABLE + LOWER_WORKLOAD + STAT_PRIORITY"  },  "error": null,  "meta": {"policy_version":"v1.0"}}

PUT /orders/{exam_id}/reassignRequest:{  "target_radiologist_id": "RAD-002",  "reason": "OVERLOAD_AND_SLA_RISK",  "actor_type": "SYSTEM"}Response:{  "data": {    "exam_id": "RAD-000123",    "status": "ASSIGNED",    "assigned_radiologist_id": "RAD-002",    "event_id": "EV-00091"  },  "error": null,  "meta": {}}

# 4. Error Contract


| HTTP | Code | Meaning | UI behavior
| 400 | INVALID_SCHEMA | Request malformed. | Show validation error.
| 404 | NOT_FOUND | Exam/resource does not exist. | Show not-found state.
| 409 | NO_ELIGIBLE_CAPACITY | No qualified resource available. | Create critical escalation alert.
| 409 | STALE_STATE | Concurrent state changed. | Refresh and recalculate.
| 422 | POLICY_REJECTED | Request violates routing policy. | Show policy reason.
| 500 | ROUTING_FAILURE | Internal routing error. | Keep case visible and raise system alert.


# 5. Parallel Development Contract

- Frontend can build against mocked JSON matching the response shapes before backend completion.

- Backend can implement routing without UI changes as long as contracts remain stable.

- ML/data component may later provide a score object, but the final routing contract consumes explainable structured features—not opaque model output only.