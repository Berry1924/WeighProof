# 07 — Tech Stack Decision Note

**Source Basis**: `07_Tech_Stack_Decision_Note.docx`

---

## 1. Recommended MVP Technology Stack

| Architecture Layer | Recommended Technology | Technical Rationale & Justification |
| :--- | :--- | :--- |
| **Backend REST API** | **FastAPI (Python 3.11+)** | High performance async REST framework, auto-generated OpenAPI docs, native Pydantic data validation, fast rules development. |
| **Operational Store** | **PostgreSQL 15+** | Relational integrity for orders, workforce rosters, policy versioning, and immutable audit event logs. |
| **Operational Queue & Cache**| **Redis** | In-memory atomic counters for workforce capacity, active state caching, and fast message publishing. |
| **Frontend Framework** | **React 18 + TypeScript + Vite** | Rapid UI development, strict type safety, responsive component model for complex operational dashboards. |
| **Real-Time Push** | **WebSockets / Server-Sent Events** | Instant push of worklist status changes, alert banners, and simulator updates without polling. |
| **Data Visualization** | **Recharts / Chart.js** | Lightweight React chart components for live rendering of TAT trends, SLA risk, and workload variance. |
| **Containerization** | **Docker Compose** | Single-command (`docker-compose up`) reproducible local deployment environment for judge review. |
| **Automated Testing** | **Pytest + API Integration Tests** | Verifies routing rules, candidate scoring math, and state machine transitions against regression. |

---

## 2. Excluded Technologies & Anti-Patterns Avoided

* **Heavy Microservices Architecture**: Avoided to prevent infrastructure overhead and deployment friction during hackathon execution.
* **Complex Machine Learning Platforms (Kubeflow/MLflow)**: Unnecessary; routing is primarily rules-driven and policy-configurable at MVP stage.
* **Medical Image Inference Frameworks (PyTorch/MONAI)**: Excluded because image interpretation is explicitly out of scope.
* **Production Messaging Integrations (Twilio/WhatsApp)**: Subbed with mock notification logs to avoid external API dependency failures.
* **Direct Hospital Integration Engines (Mirth Connect)**: Interface boundaries are documented with JSON REST mocks instead of live HL7/DICOM connections.

---

## 3. Core Architectural Decision Rules

1. **Simplicity First**: Choose the simplest tech stack that demonstrates the core orchestration value reliably.
2. **Zero Fragile External Dependencies**: Avoid third-party APIs that could fail due to rate limits or network issues during live presentations.
3. **Decoupled Business Rules**: Keep priority algorithms and routing policies strictly isolated from UI code so rules can be modified live during judge Q&A.
4. **Reproducible One-Command Startup**: Ensure the entire platform compiles and launches via `docker-compose up`.

---

## 4. Judge Q&A Defensive Playbook

### Q1: "Why did you choose FastAPI and Python instead of Node.js or Java?"
> **Answer**: Python allows our team to use a unified language stack for backend REST APIs, rules engines, statistical data generation, and analytics calculations. FastAPI gives us high-async performance with native OpenAPI schema generation and Pydantic validation out of the box.

### Q2: "Why use PostgreSQL for operational data instead of a NoSQL database like MongoDB?"
> **Answer**: Our core domain model relies heavily on relational integrity between orders, staff credentials, facility permissions, and audit event logs. SQL transactions guarantee consistency, and relational queries make calculating operational metrics like average TAT and workload variance straightforward.

### Q3: "Why is Redis included alongside PostgreSQL?"
> **Answer**: PostgreSQL remains the durable source of truth for orders and audit history, while Redis acts as a high-speed in-memory counter and pub/sub layer for active workforce capacity and real-time dashboard updates.

### Q4: "Why aren't you using deep learning / AI for diagnosis?"
> **Answer**: Radiology workflow blockages are fundamentally an **operational orchestration problem**, not an image classification problem. Hospital bottlenecks occur when critical cases sit unread due to workforce unavailability. RFO solves the workflow blockage directly by ensuring qualified capacity is automatically matched to urgent demand.
