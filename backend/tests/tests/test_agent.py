from app.agents.deterministic_agent import DeterministicRecoveryAgent
from app.core.enums import PaymentStatus, RecoveryAction, RiskCategory
from app.services.customer_context import build_customer_context
from app.services.risk_classifier import classify_payment_event
from app.simulator.generator import generate_payment_event


def get_proposal(scenario: str):
    event = generate_payment_event(
        scenario=scenario,
        seed=42,
    )

    classification = classify_payment_event(event)
    customer_context = build_customer_context(event)

    agent = DeterministicRecoveryAgent()

    proposal = agent.propose(
        event=event,
        risk_category=classification.category,
        classifier_reason=classification.reason,
        customer_context=customer_context,
    )

    return event, classification, proposal


def test_successful_payment_requires_no_action():
    event, _, proposal = get_proposal("successful_payment")

    assert event.status == PaymentStatus.CAPTURED
    assert proposal.recommended_action == RecoveryAction.NO_ACTION
    assert proposal.confidence == 1.0
    assert proposal.estimated_recovery_amount == 0


def test_temporary_failure_waits_before_retry():
    event, classification, proposal = get_proposal(
        "temporary_failure"
    )

    assert classification.category == RiskCategory.TEMPORARY_FAILURE
    assert proposal.recommended_action == RecoveryAction.WAIT_AND_RETRY
    assert proposal.confidence == 0.78
    assert proposal.estimated_recovery_amount == event.amount


def test_insufficient_funds_sends_recovery_message():
    event, classification, proposal = get_proposal(
        "insufficient_funds"
    )

    assert classification.category == RiskCategory.INSUFFICIENT_FUNDS
    assert proposal.recommended_action == RecoveryAction.SEND_RECOVERY_MESSAGE
    assert proposal.estimated_recovery_amount == event.amount


def test_payment_method_problem_requests_update():
    event, classification, proposal = get_proposal(
        "payment_method_problem"
    )

    assert classification.category == RiskCategory.PAYMENT_METHOD_PROBLEM
    assert (
        proposal.recommended_action
        == RecoveryAction.REQUEST_PAYMENT_METHOD_UPDATE
    )
    assert proposal.estimated_recovery_amount == event.amount


def test_risk_failure_escalates():
    event, classification, proposal = get_proposal(
        "risk_failure"
    )

    assert classification.category == RiskCategory.SUSPECTED_RISK_FAILURE
    assert proposal.recommended_action == RecoveryAction.ESCALATE
    assert proposal.estimated_recovery_amount == 0


def test_unknown_failure_escalates():
    event, classification, proposal = get_proposal(
        "unknown_failure"
    )

    assert classification.category == RiskCategory.UNKNOWN
    assert proposal.recommended_action == RecoveryAction.ESCALATE
    assert proposal.estimated_recovery_amount == 0


def test_confidence_is_valid():
    scenarios = [
        "successful_payment",
        "temporary_failure",
        "insufficient_funds",
        "payment_method_problem",
        "risk_failure",
        "unknown_failure",
    ]

    for scenario in scenarios:
        _, _, proposal = get_proposal(scenario)

        assert 0.0 <= proposal.confidence <= 1.0
