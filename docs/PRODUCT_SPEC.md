# RECAP Product Specification

**RECAP** — Revenue Intelligence & Recovery Agent  
Razorpay Buildathon project

---

## 1. Product name

**RECAP** — Revenue Intelligence & Recovery Agent

---

## 2. Product vision

RECAP is an AI-powered revenue intelligence and recovery agent for payment merchants. It detects revenue at risk, investigates why the loss occurred, recommends the most appropriate recovery intervention, applies deterministic safety policies, executes only permitted actions, and records the entire decision in an audit trail.

RECAP is not a failed-payment retry tool. It is a closed-loop system that answers, over time:

- What revenue is at risk?
- Why is it at risk?
- How much is potentially recoverable?
- What action should be taken?
- Why is that action appropriate?
- Is the action allowed by policy?
- How much revenue was actually recovered?

---

## 3. Problem statement

Merchants lose revenue from more than failed card charges. Leakage also comes from checkout abandonment, subscription payment failures, payment-method issues, payment-system degradation, B2B overdue receivables, and other recoverable events.

Today these signals are fragmented across payment dashboards, webhooks, CRM, and operations. Operators often:

- Retry blindly without understanding the failure reason
- Miss recoverable cases that are not “failed payments”
- Take financial actions without a recorded policy check
- Cannot prove why an intervention was chosen or whether it was allowed

RECAP centralizes detection, reasoning, policy, execution, and outcome so merchants recover revenue safely and with a complete audit trail.

---

## 4. Target users

| User | Role |
|------|------|
| **Merchant operations / revenue ops** | Primary user. Reviews at-risk revenue, approved/rejected actions, and recovery outcomes. |
| **Finance / collections (B2B)** | Uses RECAP for overdue receivables and recovery recommendations (future). |
| **Engineering / payments** | Owns Razorpay webhooks, integration health, and executor permissions. |
| **Compliance / audit** | Reads the audit log: proposed action, policy decision, execution, outcome. |

MVP focus: **merchant operations** for a Razorpay Test Mode merchant.

---

## 5. Core use cases

1. **Detect revenue at risk** from incoming payment and related events.
2. **Investigate the reason** for the loss or risk (failure code, method, timing, system health, etc.).
3. **Estimate recoverable amount** for the case.
4. **Propose a recovery intervention** (retry, notify, escalate, hold, etc.) with a rationale.
5. **Apply deterministic policy** to approve or reject the proposal.
6. **Execute only permitted actions** via the action executor.
7. **Record the full decision path** in an audit trail.
8. **Track outcome** (recovered / not recovered / pending) against the original risk.

---

## 6. Revenue leakage categories

The long-term system analyzes:

1. Failed payments
2. Checkout abandonment
3. Subscription payment failures
4. Payment-method problems
5. Payment-system degradation
6. B2B overdue receivables
7. Other recoverable revenue leakage

MVP concentrates on **failed payments** (and closely related Razorpay payment events). Other categories are in scope for later phases, not for the first implementation.

---

## 7. What RECAP does

- Ingests events (webhooks and, later, other sources).
- Detects cases where revenue is at risk.
- Uses an AI agent to reason over the case and **propose** an action.
- Runs every proposal through a **deterministic policy engine**.
- Executes only **approved** actions.
- Tracks outcomes (whether revenue was recovered).
- Writes an immutable (append-only) audit record for each decision.

---

## 8. What RECAP does NOT do

- The AI agent **never** directly controls financial actions (charges, refunds, payouts, retries that move money).
- RECAP does not bypass Razorpay; all payment-side effects go through Razorpay APIs within Test Mode (MVP) and documented permissions.
- RECAP does not auto-approve based on LLM confidence alone; policy is deterministic.
- RECAP is not a general CRM, ERP, or full collections platform.
- RECAP does not invent new payment products; it operates on merchant events and Razorpay capabilities.
- RECAP does not skip audit logging for any proposed or executed action.

---

## 9. AI agent responsibilities

The AI **proposes**. It must not execute.

- Interpret detected risk: category, likely cause, recoverable amount (estimate).
- Recommend the most appropriate recovery intervention from an allowed action catalog.
- Explain why that action is appropriate for this case.
- Produce **structured outputs** (Pydantic-compatible schemas), not free-form financial commands.
- May use tool calling in later phases (read-only investigation tools first).
- Must not call Razorpay write APIs, mutate balances, or invoke the executor.

---

## 10. Policy engine responsibilities

The policy engine **decides**. It is deterministic, not an LLM.

- Evaluate the proposed action against explicit rules (amount limits, action type allowlist, retry caps, cooldown, merchant flags, risk category).
- Return **approved** or **rejected** with a machine-readable reason code.
- Never execute; only gate the executor.
- Same inputs must yield the same decision (no hidden model calls).
- Log the policy version and rule hits on every evaluation.

---

## 11. Action executor responsibilities

The executor **acts** only after approval.

- Accept only policy-approved action payloads.
- Perform permitted operations (e.g. customer notification, retry via Razorpay where allowed, internal status updates).
- Refuse execution if approval is missing, expired, or tampered.
- Return a structured execution result (success, failure, skipped).
- Do not interpret or override policy; do not re-ask the LLM.

---

## 12. Audit requirements

Every case must retain a trail covering:

| Stage | Required record |
|-------|-----------------|
| Event | Source, payload reference, received time |
| Detection | Risk case id, category, amount at risk |
| AI reasoning | Model/version, structured proposal, rationale |
| Proposed action | Action type, parameters |
| Policy | Engine version, approved/rejected, reason codes |
| Execution | If approved: executor result, timestamps |
| Outcome | Recovered amount (if any), status |

Audit records are append-only. They must support answering: what was at risk, why, what was proposed, whether it was allowed, what ran, and how much was recovered.

---

## 13. Success metrics

| Metric | Intent |
|--------|--------|
| Revenue at risk identified | Coverage of leakage events |
| Potentially recoverable amount | Quality of estimates |
| Policy approval / rejection rates | Guardrail tightness |
| Actions executed vs proposed | Executor and policy alignment |
| Revenue actually recovered | Closed-loop effectiveness |
| Time from event to decision | Operational latency |
| Audit completeness | % of cases with full trail |

MVP success: end-to-end path on Test Mode failed-payment cases with a complete audit log, even if recovery volume is small.

---

## 14. MVP scope

- Documentation (this spec + architecture).
- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite.
- Frontend: Next.js / React, Tailwind CSS (operator view of cases, proposals, policy decisions, audit).
- Razorpay Test Mode: APIs + webhooks for **failed payments** (primary leakage category).
- LLM with **structured outputs** for proposals (no tool calling required in MVP).
- Deterministic policy engine + action executor + audit log.
- Docker and GitHub as the delivery/infra baseline when implementation starts.

**Out of MVP:** checkout abandonment, subscriptions, payment-method analytics, system-degradation detection, B2B receivables, PostgreSQL (unless required), tool calling, production Razorpay live keys.

---

## 15. Future scope

- Remaining leakage categories (checkout abandonment, subscriptions, method problems, system degradation, B2B overdue, other recoverable leakage).
- LLM tool calling for investigation (read-only tools, then tightly scoped writes only via executor).
- PostgreSQL if SQLite is insufficient.
- Richer action catalog and merchant-configurable policies.
- Outcome-driven learning (which interventions recovered revenue) without letting the model skip policy.
- Multi-merchant / multi-workspace if the product expands beyond the Buildathon merchant.
---
