# 04 — API Contract Specification

**Source Basis**: `04_API_Contract.docx`

---

## 1. Core API Principles

* **Protocol**: RESTful HTTP + JSON payloads over HTTPS (WebSockets for real-time push).
* **Envelope Standard**: All endpoints return a uniform envelope containing `data`, `error`, and `meta`.
* **Explainability Requirement**: Every automated action endpoint exposes human-readable decision codes (`reason_code`).
* **Actor Traceability**: Requests carry actor headers (`X-Actor-ID`, `X-Actor-Type`) to ensure audit logging integrity.

---

## 2. Endpoint Catalogue

| Method | Endpoint Path | Purpose | Primary Response Object |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/orders` | Ingest new order from mock RIS feed | Created Order + Initial Routing Decision |
| **GET** | `/api/v1/orders` | List and filter active worklist | Paginated List of `RadiologyOrder` |
| **GET** | `/api/v1/orders/{exam_id}` | Fetch order details and complete audit timeline | `RadiologyOrder` + Array of `AuditEvent` |
| **PUT** | `/api/v1/orders/{exam_id}/reassign` | Reassign study (automated or manual override) | Updated Order + Reassignment Event |
| **GET** | `/api/v1/workforce` | Retrieve real-time radiologist roster & capacity | Array of `Workforce` objects |
| **PUT** | `/api/v1/workforce/{id}/availability` | Modify staff availability / shift state | Updated `Workforce` object |
| **GET** | `/api/v1/alerts` | List active bottleneck & escalation alerts | Array of Alert objects |
| **POST** | `/api/v1/alerts/{id}/ack` | Acknowledge active alert | Updated Alert state |
| **GET** | `/api/v1/analytics/summary` | Fetch operational KPIs (TAT, SLA breach, load variance) | KPI Summary Object |
| **POST** | `/api/v1/simulation/events` | Inject demo scenario (overload burst, outage) | Scenario Execution Result |
| **GET** | `/api/v1/policies` | Retrieve active routing & urgency policy configuration | Policy JSON |
| **PUT** | `/api/v1/policies` | Update policy rules live during demo | Versioned Policy Object |

---

## 3. Standard Response Envelope

```json
{
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2026-09-07T09:15:00+05:30",
    "policy_version": "v1.0",
    "request_id": "req-994812"
  }
}
```

---

## 4. Key Payload Specifications

### 4.1 Ingest New Order: `POST /api/v1/orders`

#### Request Payload
```json
{
  "exam_id": "RAD-000123",
  "facility_id": "FAC-CHN-01",
  "modality": "CT",
  "exam_type": "HEAD_CT",
  "urgency_flag": "STAT",
  "clinician_priority": "HIGH",
  "order_time": "2026-09-07T09:15:00+05:30",
  "sla_minutes": 30,
  "eligible_specialties": ["NEURORADIOLOGY", "EMERGENCY"],
  "patient_location": "ED"
}
```

#### Successful Response (`HTTP 201 Created`)
```json
{
  "data": {
    "exam_id": "RAD-000123",
    "status": "ASSIGNED",
    "assigned_radiologist_id": "RAD-002",
    "routing_reason": "ELIGIBLE_SPECIALTY + AVAILABLE_NOW + LOWER_WORKLOAD + STAT_PRIORITY",
    "score_breakdown": {
      "specialty_match": 40,
      "urgency_boost": 50,
      "workload_penalty": -12
    }
  },
  "error": null,
  "meta": {
    "policy_version": "v1.0"
  }
}
```

---

### 4.2 Reassign Study: `PUT /api/v1/orders/{exam_id}/reassign`

#### Request Payload
```json
{
  "target_radiologist_id": "RAD-005",
  "reason": "OVERLOAD_AND_SLA_RISK",
  "actor_type": "USER",
  "actor_id": "USER-SUPERVISOR-01"
}
```

#### Successful Response (`HTTP 200 OK`)
```json
{
  "data": {
    "exam_id": "RAD-000123",
    "status": "ASSIGNED",
    "assigned_radiologist_id": "RAD-005",
    "event_id": "EV-00091",
    "previous_assigned_id": "RAD-002"
  },
  "error": null,
  "meta": {
    "policy_version": "v1.0"
  }
}
```

---

## 5. HTTP Error Contract Matrix

| HTTP Status | Error Code | Root Cause / Meaning | Recommended UI Behavior |
| :--- | :--- | :--- | :--- |
| **400 Bad Request** | `INVALID_SCHEMA` | Payload failed JSON schema validation (missing required fields). | Highlight invalid fields in intake modal. |
| **404 Not Found** | `NOT_FOUND` | Specified `exam_id` or `radiologist_id` does not exist. | Display 404 alert toast; refresh view. |
| **409 Conflict** | `NO_ELIGIBLE_CAPACITY` | No qualified radiologist is available to accept assignment. | Trigger visible Level-3 escalation alert. |
| **409 Conflict** | `STALE_STATE` | Order status was modified concurrently by another process. | Silently refetch order and recalculate state. |
| **422 Unprocessable** | `POLICY_REJECTED` | Assignment violates active safety/qualification policy. | Show policy rejection reason code. |
| **500 Internal Error** | `ROUTER_FAILURE` | Decision engine exception occurred during candidate scoring. | Preserve order state; raise system alarm. |

---

## 6. Parallel Development Strategy

* **Frontend Team**: Mock responses using the envelope specs above to build the React dashboard independently.
* **Backend Team**: Implement FastAPI endpoints and scoring modules against stable JSON schema definitions.
* **ML / Analytics Team**: Supply feature extraction and capacity forecast logic consuming canonical JSON schemas without breaking contracts.
