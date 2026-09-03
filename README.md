# RECAP AI

## Revenue Intelligence & Recovery Agent for Razorpay

> **AI proposes. Policy decides. RECAP recovers.**

RECAP is an AI-powered payment recovery intelligence system designed to help businesses make smarter decisions when payments fail.

Instead of treating every failed payment as the same problem, RECAP analyzes the failure context, classifies the risk, asks an AI recovery agent to propose an appropriate action, evaluates that proposal through a deterministic Policy Engine, and records the complete decision trail.

The goal is simple:

**Turn failed payment events into intelligent, controlled recovery opportunities.**

---

## 🚨 Problem

A failed payment does not always mean lost revenue.

Different failures require different responses:

| Payment failure        | Possible recovery strategy            |
| ---------------------- | ------------------------------------- |
| Temporary failure      | Retry at an appropriate time          |
| Insufficient funds     | Encourage the customer to retry later |
| Payment method problem | Suggest another payment method        |
| Risk failure           | Avoid aggressive automated recovery   |
| Unknown failure        | Use a conservative recovery strategy  |

A basic retry mechanism cannot reliably distinguish between these situations.

RECAP treats payment recovery as a **decision problem**, rather than simply a retry operation.

---

## 💡 Solution

RECAP creates an intelligent recovery pipeline:

```text
Payment Event
      ↓
Risk Classification
      ↓
AI Recovery Agent
      ↓
Recovery Recommendation
      ↓
Policy Engine
      ↓
Approved / Denied
      ↓
Recovery Decision
      ↓
Audit Log
      ↓
Dashboard
```

The AI does **not** directly control financial actions.

### AI proposes. Policy decides.

This separation provides a safer and more explainable architecture for AI-assisted payment recovery.

---

# 🤖 AI Recovery Agent

RECAP uses a locally running **Ollama + Gemma 3:4b** model as its AI recovery agent.

The agent receives payment failure context and produces a recovery recommendation including:

* Recommended recovery action
* Reasoning
* Confidence
* Estimated recovery amount
* Recovery context

The AI is used for **decision support**, not unrestricted financial execution.

```text
Payment Context
      ↓
Gemma 3:4b
      ↓
Recovery Proposal
      ↓
Policy Engine
```

The architecture is model-agnostic, so the local model can later be replaced with a stronger hosted or self-hosted model without changing the fundamental decision pipeline.

---

# 🛡️ Policy Engine

The Policy Engine is the deterministic safety layer between AI recommendations and financial actions.

The AI may recommend:

```text
"Retry payment"
```

But RECAP does not automatically trust that recommendation.

Instead:

```text
AI Recommendation
       ↓
Policy Engine
       ↓
Is this action allowed?
       ↓
APPROVED / DENIED
```

The Policy Engine provides deterministic decision-making and prevents the AI from bypassing predefined controls.

### Core principle

> **AI provides intelligence. Policy provides control.**

This separation is one of the central design principles of RECAP.

---

# 🔌 Razorpay Integration

RECAP includes a Razorpay webhook integration layer.

The webhook boundary is designed to receive payment-related events and normalize them into RECAP's internal payment-event model.

```text
Razorpay
   ↓
Webhook
   ↓
RECAP Event Ingestion
   ↓
Risk Classification
   ↓
AI Agent
```

The project is designed around **Razorpay Test Mode / simulated events for the MVP**.

Production financial execution and live payment credentials are intentionally outside the MVP scope.

No API keys or secrets are stored in the repository.

---

# 🧪 Payment Simulator

RECAP includes a built-in payment simulator so the complete recovery pipeline can be demonstrated without requiring real financial transactions.

Available scenarios include:

* Temporary Failure
* Insufficient Funds
* Payment Method Problem
* Risk Failure
* Unknown Failure
* Successful Payment

Example:

```text
Insufficient Funds
       ↓
Simulate Payment
       ↓
Risk Classification
       ↓
Gemma AI
       ↓
Recovery Recommendation
       ↓
Policy Decision
       ↓
Audit Log
```

This makes the project reproducible during demonstrations and development.

---

# 📊 Recovery Dashboard

The React dashboard provides a real-time view of the recovery system.

It displays:

* Recovery opportunity
* Recovery action rate
* Payment events
* Failed payments
* Recovery trend
* Risk distribution
* AI decisions
* AI confidence
* Latest recovery recommendation
* Audit logs
* Payment simulator results

The frontend communicates with the backend through the FastAPI API.

---

# 🧾 Auditability

Every important stage of the recovery pipeline can be recorded in the audit system.

The audit trail provides visibility into:

```text
Event received
      ↓
Risk identified
      ↓
AI recommendation
      ↓
Policy decision
      ↓
Recovery result
```

This makes the system easier to inspect and explain during both development and operation.

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │ Razorpay / Simulator│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    │  Event Ingestion    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Risk Classifier    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Ollama / Gemma 3:4b│
                    │    AI Agent         │
                    └──────────┬──────────┘
                               │
                         AI Proposal
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Policy Engine    │
                    └──────────┬──────────┘
                               │
                       ┌───────┴────────┐
                       ▼                ▼
                  APPROVED            DENIED
                       │                │
                       ▼                │
                Recovery Flow           │
                       │                │
                       └───────┬────────┘
                               ▼
                    ┌─────────────────────┐
                    │     Audit Log       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Dashboard   │
                    └─────────────────────┘
```

---

# 🧩 Project Structure

```text
recap_ai/
│
├── README.md
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── ai_agent.py
│   │   │   ├── base.py
│   │   │   ├── deterministic_agent.py
│   │   │   └── ollama_agent.py
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── policies/
│   │   │   └── engine.py
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── simulator/
│   │   └── webhooks/
│   │       └── razorpay.py
│   │
│   ├── tests/
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── docs/
    ├── ARCHITECTURE.md
    └── PRODUCT_SPEC.md
```

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* SQLite
* Pytest
* Uvicorn

### AI

* Ollama
* Gemma 3:4b
* Local AI inference

### Frontend

* React 19
* Vite
* Recharts
* Lucide React

### Integration

* Razorpay webhook layer
* Payment event simulator

---

# 🚀 Running RECAP Locally

## Prerequisites

Install:

* Python 3.11+
* Node.js / npm
* Ollama

Make sure the Gemma model is available locally:

```bash
ollama pull gemma3:4b
```

---

## 1. Start the Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 2. Start the Frontend

Open another terminal:

```bash
cd frontend

npm install
npm run dev
```

Vite will provide the local frontend URL in the terminal.

---

## 3. Run Tests

From the backend directory:

```bash
pytest -q
```

The current backend test suite passes:

```text
57 passed
```

---

# 🎬 Demo Flow

For a quick demonstration:

### Scenario 1 — Insufficient Funds

```text
Select "Insufficient Funds"
        ↓
Simulate Payment
        ↓
Risk classification
        ↓
AI recovery recommendation
        ↓
Policy decision
        ↓
Audit log
```

### Scenario 2 — Temporary Failure

Run the simulator with:

```text
Temporary Failure
```

Observe how the recovery recommendation changes according to the failure context.

### Scenario 3 — Risk Failure

Run:

```text
Risk Failure
```

This demonstrates the importance of the Policy Engine and controlled AI decision-making.

---

# 🧠 Why RECAP?

Traditional payment recovery can be overly generic:

```text
Payment Failed
      ↓
Retry
```

RECAP introduces an intelligence layer:

```text
Payment Failed
      ↓
Understand the failure
      ↓
Assess risk
      ↓
Ask AI for a recovery strategy
      ↓
Validate through policy
      ↓
Make an explainable recovery decision
```

The goal is not to replace the payment processor.

### RECAP is an intelligence layer around payment recovery.

---

# 🔐 Safety by Design

RECAP follows several important boundaries:

* AI does not directly execute financial actions.
* Policy decisions are deterministic.
* Financial actions require policy approval.
* Secrets remain outside source control.
* Production payment execution is outside the MVP.
* The simulator enables safe demonstrations.
* Important decisions are recorded for auditability.

---

# 📈 Future Scope

Potential future extensions include:

* Production Razorpay Test Mode integration
* Additional payment-recovery strategies
* Merchant-configurable policies
* Human approval workflows
* More advanced recovery models
* Outcome-based model evaluation
* PostgreSQL for larger deployments
* Asynchronous event processing
* Additional revenue leakage detectors
* Multi-merchant support
* Production-grade action execution adapters

These are intentionally outside the current MVP so the core recovery intelligence pipeline remains focused and demonstrable.

---

# 🎯 Project Vision

RECAP aims to move payment recovery from:

**Reactive retrying**

to:

**Context-aware, AI-assisted, policy-controlled recovery.**

### The core idea:

> **AI proposes. Policy decides. RECAP explains. Businesses recover.**

---

## Status

**MVP: Demo Ready**

Core components implemented:

* ✅ FastAPI backend
* ✅ Payment event processing
* ✅ Risk classification
* ✅ AI recovery agent
* ✅ Ollama / Gemma 3:4b integration
* ✅ Deterministic Policy Engine
* ✅ Razorpay webhook layer
* ✅ Payment simulator
* ✅ Audit logging
* ✅ React dashboard
* ✅ Automated backend tests
* ✅ 57/57 tests passing
