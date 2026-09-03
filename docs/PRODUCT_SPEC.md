# RECAP Product Specification

**RECAP — Revenue Intelligence & Recovery Agent**

Razorpay Buildathon Project

---

## 1. Product Name

**RECAP — Revenue Intelligence & Recovery Agent**

---

## 2. Product Vision

RECAP is an AI-powered payment recovery intelligence system for merchants.

It analyzes payment events, identifies revenue at risk, classifies the likely failure or risk category, uses an AI recovery agent to propose an appropriate recovery strategy, evaluates that proposal through a deterministic policy engine, and records the complete decision in an auditable trail.

RECAP is **not simply a blind payment retry system**. It is an intelligence and decision layer around payment recovery.

The system is designed to answer:

* What payment is at risk?
* Why is it at risk?
* How much revenue may be recoverable?
* What recovery action does the AI recommend?
* How confident is the recommendation?
* Is the recommendation allowed by policy?
* Why was the recommendation approved or rejected?
* What decision was ultimately recorded?

For the current MVP, RECAP focuses on **failed-payment scenarios in a safe simulated/Test Mode environment** rather than performing production financial transactions.

---

## 3. Problem Statement

Merchants lose revenue when legitimate payment attempts fail, but different payment failures should not necessarily receive the same recovery strategy.

For example:

* A temporary payment failure may be suitable for a retry.
* An insufficient-funds failure may require a customer notification or delayed retry.
* A high-risk failure may require the case to be held or rejected.
* An unknown failure may require further investigation rather than an automatic retry.

A simple retry-everything strategy can create unnecessary retries, poor customer experiences, and potentially unsafe financial decisions.

Operational teams also need to understand **why a recovery decision was made**.

RECAP addresses this by combining:

1. Payment-event ingestion
2. Risk classification
3. AI-assisted recovery recommendations
4. Deterministic policy controls
5. Explainable decisions
6. Audit logging
7. A merchant-facing dashboard
8. Safe payment simulation for demonstration and testing

---

## 4. Target Users

| User                                         | Role                                                                                             |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Merchant Operations / Revenue Operations** | Primary MVP user. Reviews payment risk, AI recommendations, policy decisions, and audit history. |
| **Finance / Collections**                    | Potential future user for broader revenue-recovery workflows.                                    |
| **Payments / Engineering**                   | Owns payment-event integration, webhook configuration, and policy configuration.                 |
| **Compliance / Audit**                       | Uses the audit trail to understand how recovery decisions were generated and evaluated.          |

**MVP focus:** Merchant operations for failed-payment recovery scenarios.

---

## 5. Core Use Cases

### MVP Use Cases

1. **Receive payment events** from the simulator or Razorpay integration boundary.
2. **Classify payment risk** based on the event and failure context.
3. **Estimate potentially recoverable revenue.**
4. **Generate an AI recovery recommendation.**
5. **Provide reasoning and confidence** for the recommendation.
6. **Evaluate the recommendation through deterministic policies.**
7. **Approve or reject the recommendation** based on policy.
8. **Record the complete decision path** in the audit log.
9. **Display the decision and history** through the operator dashboard.

### Future Use Cases

10. Execute approved actions through a controlled action executor.
11. Track actual recovery outcomes.
12. Learn from historical recovery outcomes while keeping policy enforcement deterministic.

---

## 6. Revenue Leakage Categories

The long-term RECAP platform can expand across multiple sources of revenue leakage:

1. Failed payments
2. Checkout abandonment
3. Subscription payment failures
4. Payment-method problems
5. Payment-system degradation
6. B2B overdue receivables
7. Other recoverable revenue leakage

### MVP Focus

The current implementation concentrates on **failed-payment and related payment-event scenarios**.

Other leakage categories are future extensions and are not represented as fully implemented MVP functionality.

---

## 7. What RECAP Does Today

The current MVP:

* Receives payment events.
* Supports simulated payment scenarios for safe demonstrations.
* Classifies payment risk.
* Builds customer/payment context for decision-making.
* Uses a local AI agent powered by Ollama and Gemma 3:4b.
* Generates a structured recovery recommendation.
* Provides a rationale and confidence for the recommendation.
* Passes the recommendation through a deterministic Policy Engine.
* Produces an approved/rejected policy decision.
* Records the decision in an audit log.
* Exposes dashboard APIs.
* Displays payment recovery intelligence through a React dashboard.
* Provides a Razorpay webhook integration boundary.

The MVP is designed primarily as a **recovery intelligence and decision-support layer**, not as a production payment executor.

---

## 8. What RECAP Does NOT Do

The current MVP:

* Does **not** allow the AI model to directly execute financial actions.
* Does **not** use LLM confidence as a substitute for deterministic policy.
* Does **not** perform uncontrolled production payment operations.
* Does **not** claim guaranteed revenue recovery.
* Does **not** bypass Razorpay payment infrastructure.
* Does **not** operate as a general CRM, ERP, or collections platform.
* Does **not** provide production-grade fraud detection.
* Does **not** claim production-scale financial infrastructure.
* Does **not** currently implement a full autonomous action executor.
* Does **not** currently measure real recovered revenue from production transactions.

The simulator is intentionally used to demonstrate the complete **decision-making path safely** without moving real money.

---

## 9. AI Recovery Agent Responsibilities

The AI agent **proposes**. It does not make the final policy decision.

The AI agent is responsible for:

* Interpreting the payment failure context.
* Understanding the likely reason for failure.
* Assessing the recovery situation.
* Estimating potentially recoverable value.
* Recommending an appropriate recovery strategy.
* Providing reasoning for the recommendation.
* Providing a confidence score.
* Returning structured information that can be consumed by the backend.

The current implementation uses:

**Ollama + Gemma 3:4b**

The model runs locally for the MVP, avoiding dependence on paid external LLM APIs.

The architecture is intentionally model-agnostic so that another model/provider can be introduced later.

### AI Safety Boundary

The AI agent does not directly:

* call financial write APIs,
* modify payment balances,
* authorize financial transactions,
* override policy decisions,
* or independently execute recovery actions.

---

## 10. Policy Engine Responsibilities

The Policy Engine **decides whether the AI proposal is permitted**.

Unlike the AI agent, the Policy Engine is deterministic.

It evaluates the recommendation using explicit business rules and safety constraints.

Examples of policy considerations include:

* Risk category
* Proposed action
* Amount or transaction value
* Retry-related constraints
* Merchant-defined restrictions
* Safety thresholds
* Other deterministic business rules

The Policy Engine returns a machine-readable decision such as:

**Approved** or **Rejected**

along with an explanation/reason for the decision.

The same inputs should produce the same policy decision.

The Policy Engine does not use an LLM to make its decision.

---

## 11. Recovery Orchestration

The recovery orchestrator connects the major decision-making components.

The current flow is:

**Payment Event → Risk Classification → Customer/Payment Context → AI Recommendation → Policy Evaluation → Audit Log**

The orchestrator ensures that the components operate in a controlled sequence and that the final decision can be recorded and displayed.

In the current MVP, the orchestration layer is primarily responsible for **decision generation and recording**, rather than performing real financial side effects.

---

## 12. Audit Requirements

Every recovery decision should provide an understandable trail of how the result was produced.

The current MVP records information including:

| Stage    | Recorded Information                       |
| -------- | ------------------------------------------ |
| Event    | Payment/event information and timestamp    |
| Risk     | Risk category and relevant payment context |
| AI       | Recommendation, reasoning, and confidence  |
| Policy   | Approval/rejection and policy reasoning    |
| Decision | Final recovery recommendation/decision     |
| Audit    | Persisted record of the decision           |

The audit trail should allow an operator to answer:

* What payment was being evaluated?
* What was the detected risk?
* What did the AI recommend?
* Why did the AI recommend it?
* What did the policy engine decide?
* Why was it approved or rejected?
* When was the decision recorded?

### Future Audit Expansion

When real action execution is introduced, the audit trail can be extended with:

* Executor request
* Executor response
* Execution timestamp
* Execution status
* Recovery outcome
* Recovered amount

---

## 13. Success Metrics

| Metric                         | Intent                                              |
| ------------------------------ | --------------------------------------------------- |
| Revenue at risk identified     | Measure detection coverage                          |
| Potentially recoverable amount | Evaluate recovery estimation                        |
| AI recommendation quality      | Evaluate usefulness of proposed strategies          |
| Policy approval/rejection rate | Measure effectiveness of safety controls            |
| Decision latency               | Measure time from event to decision                 |
| Audit completeness             | Ensure decisions are traceable                      |
| Scenario coverage              | Validate behavior across different payment failures |

### MVP Success Criteria

The MVP is successful when it can demonstrate an end-to-end flow for failed-payment scenarios:

**Event → Risk → AI Recommendation → Policy Decision → Audit → Dashboard**

with deterministic policy enforcement and reproducible test coverage.

The current backend test suite contains **57 passing tests**.

---

## 14. MVP Scope

### Included

* Product documentation
* Architecture documentation
* Python backend
* FastAPI API layer
* Pydantic schemas
* SQLAlchemy
* SQLite persistence
* Payment-event processing
* Risk classification
* Customer/payment context
* AI recovery agent
* Ollama + Gemma 3:4b local inference
* Structured recovery recommendations
* Deterministic Policy Engine
* Recovery orchestration
* Audit logging
* Razorpay webhook integration boundary
* Payment simulator
* React/Vite frontend
* Operator dashboard
* Audit-log visualization
* Recovery decision visualization
* Automated backend tests

### Current Demo Environment

The MVP is designed for **safe local/Test Mode-style demonstrations**.

The payment simulator provides scenarios such as:

* Temporary failure
* Insufficient funds
* Payment-method problem
* Risk failure
* Unknown failure
* Successful payment

This allows the recovery intelligence workflow to be demonstrated without moving real money.

### Out of MVP

The following are not fully implemented in the current MVP:

* Production Razorpay live-key financial operations
* Autonomous payment-side-effect execution
* Full action executor
* Real recovered-revenue measurement
* Checkout abandonment recovery
* Subscription recovery workflows
* Advanced payment-method analytics
* System-degradation detection
* B2B receivables
* Multi-merchant production infrastructure
* PostgreSQL migration
* LLM tool calling
* Autonomous LLM-controlled financial actions

---

## 15. Future Scope

### 15.1 Controlled Action Executor

Introduce a dedicated executor that can perform approved non-destructive or tightly controlled operations.

The executor would:

* Accept only policy-approved actions.
* Validate approval before execution.
* Execute permitted operations.
* Return structured execution results.
* Never override the Policy Engine.

Financial write operations would remain behind explicit permissions and safeguards.

### 15.2 Outcome Tracking

Connect decisions to actual payment outcomes:

**Recommendation → Action → Payment Result → Recovered Revenue**

This would allow RECAP to measure actual recovery effectiveness.

### 15.3 Broader Revenue Leakage Detection

Expand beyond failed payments into:

* Checkout abandonment
* Subscription failures
* Payment-method problems
* Payment-system degradation
* B2B overdue receivables
* Other recoverable revenue leakage

### 15.4 Read-Only AI Tools

Introduce controlled tool calling for investigation.

The initial tools should be read-only, allowing the AI to inspect additional payment or customer context without being able to directly modify financial state.

### 15.5 Merchant-Configurable Policies

Allow merchants to define:

* Retry limits
* Risk thresholds
* Amount limits
* Allowed actions
* Cooldown periods
* Escalation rules

### 15.6 Outcome-Driven Learning

Use historical recovery outcomes to improve future recommendations while keeping the Policy Engine deterministic.

The model may become better at proposing actions, but it should not be allowed to bypass safety policies.

### 15.7 Multi-Merchant Architecture

If RECAP evolves beyond the Buildathon MVP, the system can be extended to support multiple merchants and isolated workspaces.

---

## 16. Core Architecture Principle

RECAP follows a simple separation of responsibilities:

> **AI proposes. Policy decides. Audit explains.**

The AI provides intelligence and context.

The Policy Engine provides deterministic control.

The audit system provides accountability.

This separation allows RECAP to introduce AI into payment-recovery workflows without giving the AI unrestricted control over financial operations.

---

## 17. Product Positioning

RECAP is positioned as an **intelligent decision layer for payment recovery**.

It does not attempt to replace the payment processor.

Instead, it sits around the payment-event workflow and helps merchants determine:

> **“Given this failed payment and its context, what should we do next, and are we allowed to do it?”**

This makes the core value of RECAP the combination of:

**Payment Intelligence + AI Recommendations + Deterministic Policy + Explainability + Auditability**

rather than simply another automated retry mechanism.

---

## 18. Current Project Status

**MVP: Demo Ready**

Current implementation includes:

* AI recovery agent
* Local Gemma 3:4b inference through Ollama
* Risk classification
* Deterministic policy engine
* Recovery orchestration
* Razorpay integration boundary
* Payment simulator
* Audit logging
* React dashboard
* Automated backend testing

The current backend test suite passes **57/57 tests**.

The project is designed to demonstrate intelligent and controlled payment-recovery decision making without requiring production financial transactions.
