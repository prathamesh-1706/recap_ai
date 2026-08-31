from app.agents.base import AgentProposal
from app.core.enums import (
    PolicyDecision,
    RecoveryAction,
    RiskCategory,
)
from app.policies.engine import PolicyEngine
from app.simulator.generator import generate_payment_event


def evaluate(
    scenario: str,
    action: RecoveryAction,
):
    event = generate_payment_event(
        scenario=scenario,
        seed=42,
    )

    proposal = AgentProposal(
        recommended_action=action,
        confidence=0.90,
        reason="Test agent proposal",
        estimated_recovery_amount=event.amount,
    )

    risk_category = {
        "temporary_failure": RiskCategory.TEMPORARY_FAILURE,
        "insufficient_funds": RiskCategory.INSUFFICIENT_FUNDS,
        "payment_method_problem": RiskCategory.PAYMENT_METHOD_PROBLEM,
        "risk_failure": RiskCategory.SUSPECTED_RISK_FAILURE,
        "unknown_failure": RiskCategory.UNKNOWN,
    }[scenario]

    return PolicyEngine().evaluate(
        event=event,
        risk_category=risk_category,
        proposal=proposal,
    )


def test_temporary_failure_wait_and_retry_is_approved():
    result = evaluate(
        "temporary_failure",
        RecoveryAction.WAIT_AND_RETRY,
    )

    assert result.decision == PolicyDecision.APPROVED


def test_risk_failure_retry_is_denied():
    result = evaluate(
        "risk_failure",
        RecoveryAction.RETRY,
    )

    assert result.decision == PolicyDecision.DENIED


def test_risk_failure_wait_and_retry_is_denied():
    result = evaluate(
        "risk_failure",
        RecoveryAction.WAIT_AND_RETRY,
    )

    assert result.decision == PolicyDecision.DENIED


def test_payment_method_retry_is_denied():
    result = evaluate(
        "payment_method_problem",
        RecoveryAction.RETRY,
    )

    assert result.decision == PolicyDecision.DENIED


def test_unknown_failure_retry_is_denied():
    result = evaluate(
        "unknown_failure",
        RecoveryAction.RETRY,
    )

    assert result.decision == PolicyDecision.DENIED


def test_insufficient_funds_recovery_message_is_approved():
    result = evaluate(
        "insufficient_funds",
        RecoveryAction.SEND_RECOVERY_MESSAGE,
    )

    assert result.decision == PolicyDecision.APPROVED


def test_retry_limit_blocks_financial_action():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    event = event.model_copy(
        update={"retry_count": 3}
    )

    proposal = AgentProposal(
        recommended_action=RecoveryAction.RETRY,
        confidence=0.90,
        reason="Test retry",
        estimated_recovery_amount=event.amount,
    )

    result = PolicyEngine().evaluate(
        event=event,
        risk_category=RiskCategory.TEMPORARY_FAILURE,
        proposal=proposal,
    )

    assert result.decision == PolicyDecision.DENIED