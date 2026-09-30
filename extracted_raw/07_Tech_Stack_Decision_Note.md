07 — Tech Stack Decision Note

Choose a stack once; defend it clearly; avoid mid-build churn

Source basis: Radiology_Workforce_PS_Analysis (uploaded project analysis). This pack preserves its problem framing and expands it into implementation-ready specifications. New items are clearly treated as proposed design decisions, not established facts.

# 1. Recommended MVP Stack


| Layer | Recommendation | Reason
| Backend | FastAPI + Python | Fast to build REST APIs, strong fit for rules/data logic, easy to add lightweight analytics/ML later.
| Queue/state | Redis + simple priority/state service | Fast in-memory operational state and event/queue handling; Celery optional if background jobs become necessary.
| Database | PostgreSQL | Clear relational model for orders, workforce, policies and audit events.
| Frontend | React + TypeScript | Rapid dashboard development and maintainable component model.
| Realtime | WebSocket / Server-Sent Events | Push live worklist/load/alert changes without constant refresh.
| Charts | Lightweight React chart library | Show TAT/load/SLA trends quickly.
| Containerization | Docker Compose | One-command reproducible local/demo environment.
| Testing | Pytest + API integration tests + frontend smoke tests | Protect routing rules from regressions.


# 2. What We Will NOT Add Unless Justified

- Heavy microservice decomposition — not needed for hackathon.

- Complex ML platform — routing is primarily rules/configuration at MVP stage.

- Image inference stack — out of scope.

- Production messaging integration — use notification stubs for demo.

- Real hospital integrations — demonstrate adapter interfaces only.

# 3. Decision Rules

- Prefer the simplest technology that demonstrates the core behavior.

- Do not select a technology merely because it is popular.

- Avoid technology that introduces a dependency we cannot debug during the event.

- Keep routing/policy logic isolated from UI so judge-requested changes can be demonstrated live.

# 4. Judge Answer Templates


| Question | Answer
| Why FastAPI? | The MVP is API- and rules-heavy. Python lets the same team move quickly from backend rules to analytics without splitting the language stack.
| Why PostgreSQL? | Our core entities are relational and auditability matters; SQL also makes the operational metrics straightforward.
| Why React? | The product needs a live worklist, staff load views, alerts and simulation controls; React supports a responsive component-based dashboard.
| Why Redis? | We need fast operational state/queue behavior for the demo, while durable truth remains in PostgreSQL.
| Why not build microservices? | The hackathon goal is a working orchestration engine, not infrastructure complexity. Boundaries are kept modular inside one deployable system.
