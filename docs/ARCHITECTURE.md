## RECAP Architecture

**RECAP — Revenue Intelligence & Recovery Agent**

RECAP is an AI-powered payment recovery intelligence system designed for failed-payment recovery scenarios.

The architecture separates AI reasoning from deterministic decision-making:

> **AI proposes. Policy decides.**

The current MVP focuses on failed-payment scenarios, local AI inference using Ollama/Gemma, policy-controlled recommendations, audit logging, Razorpay webhook integration, and a React operator dashboard.

---

## 1. High-Level Architecture

```text
Razorpay / Payment Simulator
          │
          ▼
    Event Ingestion
          │
          ▼
    Risk Classification
          │
          ▼
      AI Agent
   Ollama / Gemma 3:4b
          │
          ▼
 Recovery Recommendation
          │
          ▼
    Policy Engine
          │
      ┌───┴───┐
      ▼       ▼
  APPROVED   DENIED
      │       │
      └───┬───┘
          ▼
      Audit Log
          │
          ▼
    React Dashboard
```

The system is intentionally divided into separate layers so that the AI recommendation does not automatically become a financial action.

---

# 2. Event Ingestion

The ingestion layer accepts payment events from:

* Razorpay webhook integration
* Internal payment simulator for development and demonstration

The simulator provides controlled failure scenarios without requiring real financial transactions.

Examples include:

* Temporary failure
* Insufficient funds
* Payment method problem
* Risk failure
* Unknown failure
* Successful payment

The event is normalized into RECAP's internal payment-event representation before further processing.

---

# 3. Risk Classification

The risk classifier determines the category and context of the payment event.

For the MVP, the primary focus is failed payments.

The classifier provides information used by the recovery pipeline, such as:

* Failure category
* Payment context
* Amount
* Risk characteristics
* Failure reason

The classifier does not directly execute recovery actions.

---

# 4. AI Agent Layer

The AI layer uses:

**Ollama + Gemma 3:4b**

The AI agent receives structured payment and risk context and proposes a recovery strategy.

Typical outputs include:

* Recommended action
* Confidence
* Reasoning
* Estimated recovery amount
* Recovery explanation

Conceptually:

```text
Payment Context
      │
      ▼
Gemma 3:4b
      │
      ▼
Structured Recovery Proposal
```

The AI is a decision-support component.

### AI does not directly control financial actions.

It cannot bypass the Policy Engine.

---

# 5. Policy Engine

The Policy Engine is the deterministic control layer.

It evaluates the AI-generated recommendation against predefined rules.

```text
AI Proposal
     │
     ▼
Policy Engine
     │
 ┌───┴────┐
 ▼        ▼
APPROVED  DENIED
```

The Policy Engine is intentionally not an LLM.

Its purpose is to provide predictable and explainable decisions.

### Core principle

> **The AI provides intelligence. The Policy Engine provides control.**

This prevents the AI model's confidence score or reasoning from becoming an unrestricted financial authorization mechanism.

---

# 6. Recovery Orchestration

The recovery orchestrator coordinates the major components of the recovery pipeline.

Conceptually:

```text
Payment Event
     │
     ▼
Risk Classification
     │
     ▼
Customer / Payment Context
     │
     ▼
AI Recommendation
     │
     ▼
Policy Evaluation
     │
     ▼
Recovery Decision
```

The orchestrator provides the central application flow connecting event processing, risk analysis, AI recommendations, policy evaluation, and audit logging.

---

# 7. Audit Logging

RECAP records the important stages of a recovery decision.

The audit system provides visibility into:

```text
Event
  ↓
Risk
  ↓
AI Recommendation
  ↓
Policy Decision
  ↓
Recovery Result / Decision
```

Audit records can contain information such as:

* Payment/event identifier
* Risk category
* AI recommendation
* Confidence
* Policy decision
* Reason
* Timestamp
* Recovery information

This allows an operator to understand **what RECAP decided and why**.

---

# 8. Razorpay Integration Boundary

RECAP includes a Razorpay webhook integration layer.

The intended flow is:

```text
Razorpay
   │
   ▼
Webhook Endpoint
   │
   ▼
RECAP Event Processing
```

The webhook layer provides the integration boundary between Razorpay payment events and RECAP's internal processing pipeline.

For the current MVP:

* Razorpay integration is focused on receiving payment-related events.
* Demonstration scenarios use the internal simulator.
* Production payment execution is outside the MVP.
* Live Razorpay credentials are not required for the demo.
* Secrets remain outside source control.

This allows the recovery intelligence to be demonstrated safely without performing real financial transactions.

---

# 9. Database Layer

The MVP uses:

* SQLite
* SQLAlchemy

The database supports the application's payment-event, recommendation, and audit-related persistence.

The frontend does not access SQLite directly.

Instead:

```text
React Frontend
      │
      ▼
FastAPI API
      │
      ▼
Application Services
      │
      ▼
SQLAlchemy
      │
      ▼
SQLite
```

This maintains a clear separation between the operator interface and persistence layer.

---

# 10. Backend Architecture

The backend is implemented using FastAPI.

```text
backend/app/

agents/
    AI and deterministic agent implementations

api/
    REST API routes

core/
    Configuration and enums

db/
    Database configuration

models/
    SQLAlchemy models

policies/
    Deterministic policy engine

schemas/
    Pydantic API schemas

services/
    Business and recovery services

simulator/
    Payment failure scenarios

webhooks/
    Razorpay webhook integration
```

The backend follows a service-oriented structure so that AI, policy, persistence, and API concerns remain separated.

---

# 11. Frontend Architecture

The operator dashboard is implemented using:

* React
* Vite
* Recharts
* Lucide React

The frontend communicates with the FastAPI backend.

```text
React Dashboard
      │
      │ HTTP
      ▼
FastAPI Backend
      │
      ▼
RECAP Services
```

The dashboard provides visibility into:

* Recovery opportunities
* Payment events
* Failed payments
* Risk distribution
* AI decisions
* Confidence
* Recovery recommendations
* Audit logs
* Payment simulator results

The browser does not contain Razorpay secrets or direct database access.

---

# 12. End-to-End Decision Flow

A typical failed payment follows this path:

```text
1. Payment fails
        ↓
2. RECAP receives the event
        ↓
3. Failure/risk category is identified
        ↓
4. Relevant context is collected
        ↓
5. AI analyzes the recovery opportunity
        ↓
6. AI proposes a recovery action
        ↓
7. Policy Engine evaluates the proposal
        ↓
8. RECAP produces an approved/denied decision
        ↓
9. Decision is recorded in the audit system
        ↓
10. Dashboard displays the result
```

The important architectural boundary is:

```text
             AI
              │
        "What should we do?"
              │
              ▼
       Policy Engine
              │
        "Are we allowed?"
              │
              ▼
          Decision
```

---

# 13. Why This Architecture?

A financial system should not give unrestricted control to an LLM.

RECAP therefore separates:

| Component             | Responsibility                   |
| --------------------- | -------------------------------- |
| Event ingestion       | Receive payment events           |
| Risk classifier       | Understand failure/risk category |
| AI agent              | Propose recovery strategy        |
| Policy Engine         | Deterministically approve/reject |
| Recovery orchestrator | Coordinate the decision flow     |
| Audit system          | Record the decision trail        |
| Dashboard             | Provide operator visibility      |

This provides a clear separation between:

**Reasoning → Control → Accountability**

---

# 14. Current MVP vs Future Architecture

The current MVP prioritizes a working, demonstrable recovery intelligence pipeline.

### Implemented MVP

* FastAPI backend
* Payment event processing
* Razorpay webhook boundary
* Payment simulator
* Risk classification
* Customer/payment context
* Ollama/Gemma 3:4b AI agent
* Recovery recommendations
* Deterministic Policy Engine
* Recovery orchestration
* Audit logging
* React dashboard
* Automated backend tests

### Future extensions

The architecture can later be extended with:

* Policy-approved action executors
* Real Razorpay Test Mode action APIs
* Recovery outcome tracking
* More recovery strategies
* Merchant-configurable policies
* Human approval workflows
* Additional revenue leakage categories
* PostgreSQL
* Asynchronous event queues
* Read-only AI investigation tools
* Multi-merchant support
* Production infrastructure

These extensions do not change the fundamental architecture:

```text
Event
  ↓
Risk
  ↓
AI Proposal
  ↓
Policy
  ↓
Controlled Action
  ↓
Outcome
  ↓
Audit
```

---

# 15. Architecture Principle

RECAP is built around one central principle:

> **AI proposes. Policy decides. Audit explains.**

This allows AI to provide contextual intelligence while keeping critical decisions deterministic, controlled, and observable.
