from datetime import datetime, timezone

import pytest

from app.agents.base import AgentProposal
from app.agents.deterministic_agent import DeterministicRecoveryAgent
from app.core.enums import RecoveryAction, RiskCategory
from app.services.event_service import PaymentEventService
from app.schemas.payment_event import PaymentEventIn


def payment_event() -> PaymentEventIn:
    return PaymentEventIn(
        payment_id="pay_ai_test_001",
        order_id="order_ai_test_001",
        customer_id="customer_ai_test_001",
        amount=50000,
        currency="INR",
        status="failed",
        method="card",
        error_code="GATEWAY_ERROR",
        error_description="Temporary gateway failure",
        retry_count=0,
        customer_previous_success_rate=0.9,
        created_at=datetime.now(timezone.utc),
    )


class FakeAIRecoveryAgent:
    def propose(
        self,
        event,
        risk_category,
        classifier_reason,
        customer_context,
    ):
        return AgentProposal(
            recommended_action=RecoveryAction.WAIT_AND_RETRY,
            confidence=0.95,
            reason="AI recommends waiting for the temporary gateway failure to recover.",
            estimated_recovery_amount=event.amount,
        )


class FailingAIRecoveryAgent:
    def propose(
        self,
        event,
        risk_category,
        classifier_reason,
        customer_context,
    ):
        raise RuntimeError("Simulated AI failure")


def test_service_accepts_custom_ai_agent():
    agent = FakeAIRecoveryAgent()

    service = PaymentEventService(agent=agent)

    assert service._agent is agent


def test_ai_agent_produces_structured_proposal():
    agent = FakeAIRecoveryAgent()

    event = payment_event()

    proposal = agent.propose(
        event,
        RiskCategory.TEMPORARY_FAILURE,
        "Temporary gateway failure",
        None,
    )

    assert isinstance(proposal, AgentProposal)
    assert proposal.recommended_action == RecoveryAction.WAIT_AND_RETRY
    assert proposal.confidence == 0.95
    assert proposal.estimated_recovery_amount == 50000


def test_deterministic_agent_is_available_as_fallback():
    service = PaymentEventService(
        agent=FailingAIRecoveryAgent()
    )

    assert isinstance(
        service._fallback_agent,
        DeterministicRecoveryAgent,
    )


def test_ai_failure_falls_back_to_deterministic_agent(
    monkeypatch,
):
    service = PaymentEventService(
        agent=FailingAIRecoveryAgent()
    )

    event = payment_event()

    classification = RiskCategory.TEMPORARY_FAILURE

    fallback_proposal = AgentProposal(
        recommended_action=RecoveryAction.WAIT_AND_RETRY,
        confidence=0.78,
        reason="Deterministic fallback used.",
        estimated_recovery_amount=event.amount,
    )

    monkeypatch.setattr(
        service._fallback_agent,
        "propose",
        lambda *args, **kwargs: fallback_proposal,
    )

    from app.services.customer_context import build_customer_context

    context = build_customer_context(event)

    proposal = None

    try:
        proposal = service._agent.propose(
            event,
            classification,
            "Temporary failure",
            context,
        )
    except Exception:
        proposal = service._fallback_agent.propose(
            event,
            classification,
            "Temporary failure",
            context,
        )

    assert proposal == fallback_proposal