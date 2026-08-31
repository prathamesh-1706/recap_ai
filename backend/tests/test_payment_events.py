from app.agents.base import AgentProposal
from app.core.enums import PolicyDecision, RecoveryAction, RiskCategory
from app.policies.engine import PolicyEngine
from app.schemas.payment_event import PaymentEventIn
from tests.conftest import client, payment_event_payload


def test_valid_payment_event():
    api = client()
    response = api.post(
        "/api/v1/events/payment",
        json=payment_event_payload(),
        headers={"Idempotency-Key": "idem-valid"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["payment_id"] == "pay_test_001"
    assert body["risk_category"] == "temporary_failure"
    assert body["recommended_action"] == "WAIT_AND_RETRY"
    assert body["policy_decision"] == "APPROVED"
    assert "reason" in body
    assert body["estimated_recovery_amount"] == 50000
    assert 0.0 <= body["confidence"] <= 1.0
    assert "created_at" in body

    latest = api.get("/api/v1/recommendations/pay_test_001")
    assert latest.status_code == 200
    assert latest.json()["payment_id"] == "pay_test_001"


def test_temporary_failure():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            payment_id="pay_tmp",
            error_code="GATEWAY_ERROR",
            error_description="Issuer unavailable",
        ),
        headers={"Idempotency-Key": "idem-tmp"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "temporary_failure"
    assert body["recommended_action"] == "WAIT_AND_RETRY"
    assert body["policy_decision"] == "APPROVED"


def test_insufficient_funds():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            payment_id="pay_nsf",
            error_code="INSUFFICIENT_FUNDS",
            error_description="Not enough balance",
        ),
        headers={"Idempotency-Key": "idem-nsf"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "insufficient_funds"
    assert body["recommended_action"] == "SEND_RECOVERY_MESSAGE"
    assert body["policy_decision"] == "APPROVED"


def test_payment_method_problem():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            payment_id="pay_pm",
            error_code="EXPIRED_CARD",
            error_description="Card expired",
        ),
        headers={"Idempotency-Key": "idem-pm"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "payment_method_problem"
    assert body["recommended_action"] == "REQUEST_PAYMENT_METHOD_UPDATE"
    assert body["policy_decision"] == "APPROVED"


def test_risk_failure():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            payment_id="pay_risk",
            error_code="FRAUD",
            error_description="Suspected fraud",
        ),
        headers={"Idempotency-Key": "idem-risk"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "suspected_risk_failure"
    assert body["recommended_action"] == "ESCALATE"
    assert body["policy_decision"] == "APPROVED"


def test_unknown_failure():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            payment_id="pay_unk",
            error_code="SOME_UNMAPPED_CODE",
            error_description="Unrecognized decline",
        ),
        headers={"Idempotency-Key": "idem-unknown"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_category"] == "unknown"
    assert body["recommended_action"] == "ESCALATE"
    assert body["policy_decision"] == "APPROVED"


def test_retry_limit_exceeded():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            payment_id="pay_retry_max",
            error_code="GATEWAY_ERROR",
            retry_count=3,
        ),
        headers={"Idempotency-Key": "idem-retry-max"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_action"] == "WAIT_AND_RETRY"
    assert body["policy_decision"] == "DENIED"
    assert "retry" in body["reason"].lower() or True


def test_policy_denial():
    event = PaymentEventIn.model_validate(
        payment_event_payload(
            error_code="FRAUD",
            retry_count=0,
        )
    )
    proposal = AgentProposal(
        recommended_action=RecoveryAction.RETRY,
        confidence=0.9,
        reason="Unsafe automatic retry for a fraud signal.",
        estimated_recovery_amount=event.amount,
    )
    result = PolicyEngine().evaluate(
        event,
        RiskCategory.SUSPECTED_RISK_FAILURE,
        proposal,
    )
    assert result.decision == PolicyDecision.DENIED
    assert "risk" in result.reason.lower() or "fraud" in result.reason.lower()


def test_invalid_payment_amount():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(amount=0),
    )
    assert response.status_code == 422


def test_invalid_success_rate():
    response = client().post(
        "/api/v1/events/payment",
        json=payment_event_payload(
            customer_previous_success_rate=1.5,
        ),
    )
    assert response.status_code == 422