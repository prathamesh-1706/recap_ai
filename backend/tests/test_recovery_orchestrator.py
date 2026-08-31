from datetime import datetime, timezone
from unittest.mock import Mock

from app.agents.base import AgentProposal
from app.core.enums import PolicyDecision, RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn
from app.services.customer_context import CustomerContext
from app.services.recovery_orchestrator import RecoveryOrchestrator


def make_event() -> PaymentEventIn:
    return PaymentEventIn(
        payment_id="pay_test_001",
        order_id="order_test_001",
        customer_id="customer_test_001",
        amount=1000,
        currency="INR",
        status="failed",
        method="card",
        error_code="TIMEOUT",
        error_description="Gateway timeout",
        retry_count=0,
        customer_previous_success_rate=0.95,
        created_at=datetime.now(timezone.utc),
    )


def make_context() -> CustomerContext:
    return CustomerContext(
        customer_id="customer_test_001",
        retry_count=0,
        amount=1000,
        success_rate=0.95,
        reliability="HIGH",
        retry_pressure="LOW",
        amount_segment="LOW",
        payment_method="card",
    )


def test_ai_success_uses_ai_proposal():
    ai_agent = Mock()

    ai_agent.propose.return_value = AgentProposal(
        recommended_action=RecoveryAction.RETRY,
        confidence=0.95,
        reason="Temporary gateway failure.",
        estimated_recovery_amount=1000,
    )

    orchestrator = RecoveryOrchestrator(ai_agent=ai_agent)

    result = orchestrator.decide(
        event=make_event(),
        risk_category=RiskCategory.TEMPORARY_FAILURE,
        classifier_reason="Gateway timeout indicates a temporary failure.",
        customer_context=make_context(),
    )

    assert result.agent_used == "ai"
    assert result.fallback_used is False
    assert result.proposal.recommended_action == RecoveryAction.RETRY
    assert result.policy_result.decision == PolicyDecision.APPROVED


def test_ai_failure_uses_deterministic_fallback():
    ai_agent = Mock()

    ai_agent.propose.side_effect = RuntimeError(
        "OpenAI unavailable"
    )

    orchestrator = RecoveryOrchestrator(ai_agent=ai_agent)

    result = orchestrator.decide(
        event=make_event(),
        risk_category=RiskCategory.TEMPORARY_FAILURE,
        classifier_reason="Gateway timeout indicates a temporary failure.",
        customer_context=make_context(),
    )

    assert result.agent_used == "deterministic"
    assert result.fallback_used is True
    assert result.proposal.recommended_action == RecoveryAction.RETRY
    assert result.policy_result.decision == PolicyDecision.APPROVED


def test_without_ai_uses_deterministic_agent():
    orchestrator = RecoveryOrchestrator(ai_agent=None)

    result = orchestrator.decide(
        event=make_event(),
        risk_category=RiskCategory.TEMPORARY_FAILURE,
        classifier_reason="Gateway timeout indicates a temporary failure.",
        customer_context=make_context(),
    )

    assert result.agent_used == "deterministic"
    assert result.fallback_used is True
    assert result.proposal.recommended_action == RecoveryAction.RETRY


def test_policy_engine_rejects_unsafe_ai_proposal():
    ai_agent = Mock()

    ai_agent.propose.return_value = AgentProposal(
        recommended_action=RecoveryAction.RETRY,
        confidence=0.99,
        reason="Retry payment.",
        estimated_recovery_amount=1000,
    )

    orchestrator = RecoveryOrchestrator(ai_agent=ai_agent)

    result = orchestrator.decide(
        event=make_event(),
        risk_category=RiskCategory.SUSPECTED_RISK_FAILURE,
        classifier_reason="Suspicious payment behaviour.",
        customer_context=make_context(),
    )

    assert result.agent_used == "ai"
    assert result.policy_result.decision == PolicyDecision.DENIED