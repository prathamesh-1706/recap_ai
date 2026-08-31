from app.services.customer_context import build_customer_context
from app.simulator.generator import generate_payment_event


def test_high_reliability_customer():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    event = event.model_copy(
        update={
            "customer_previous_success_rate": 0.95,
        }
    )

    context = build_customer_context(event)

    assert context.reliability == "HIGH"


def test_medium_reliability_customer():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    event = event.model_copy(
        update={
            "customer_previous_success_rate": 0.75,
        }
    )

    context = build_customer_context(event)

    assert context.reliability == "MEDIUM"


def test_low_reliability_customer():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    event = event.model_copy(
        update={
            "customer_previous_success_rate": 0.30,
        }
    )

    context = build_customer_context(event)

    assert context.reliability == "LOW"


def test_retry_pressure():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    event = event.model_copy(
        update={"retry_count": 2}
    )

    context = build_customer_context(event)

    assert context.retry_pressure == "MEDIUM"


def test_high_retry_pressure():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    event = event.model_copy(
        update={"retry_count": 3}
    )

    context = build_customer_context(event)

    assert context.retry_pressure == "HIGH"


def test_amount_segments():
    event = generate_payment_event(
        scenario="temporary_failure",
        seed=42,
    )

    low = build_customer_context(
        event.model_copy(update={"amount": 500})
    )

    medium = build_customer_context(
        event.model_copy(update={"amount": 5000})
    )

    high = build_customer_context(
        event.model_copy(update={"amount": 20000})
    )

    assert low.amount_segment == "LOW"
    assert medium.amount_segment == "MEDIUM"
    assert high.amount_segment == "HIGH"