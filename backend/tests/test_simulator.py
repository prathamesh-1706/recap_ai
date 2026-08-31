from app.core.enums import RiskCategory
from app.schemas.payment_event import PaymentEventIn
from app.services.risk_classifier import classify_payment_event
from app.simulator.generator import (
    generate_batch,
    generate_payment_event,
)


def test_single_event_generation():
    event = generate_payment_event(seed=42)

    assert isinstance(event, PaymentEventIn)


def test_batch_generation():
    events = generate_batch(100, seed=42)

    assert len(events) == 100


def test_payment_ids_are_unique():
    events = generate_batch(1000, seed=42)

    payment_ids = [event.payment_id for event in events]

    assert len(payment_ids) == len(set(payment_ids))


def test_order_ids_are_unique():
    events = generate_batch(1000, seed=42)

    order_ids = [event.order_id for event in events]

    assert len(order_ids) == len(set(order_ids))


def test_same_seed_produces_same_data():
    first = generate_batch(20, seed=42)
    second = generate_batch(20, seed=42)

    assert first == second


def test_different_seed_produces_different_data():
    first = generate_batch(20, seed=42)
    second = generate_batch(20, seed=123)

    assert first != second


def test_generated_events_pass_schema_validation():
    events = generate_batch(100, seed=42)

    for event in events:
        assert isinstance(event, PaymentEventIn)


def test_all_scenarios_are_generated():
    scenarios = [
        "successful_payment",
        "temporary_failure",
        "insufficient_funds",
        "payment_method_problem",
        "risk_failure",
        "unknown_failure",
    ]

    for scenario in scenarios:
        event = generate_payment_event(
            scenario=scenario,
            seed=42,
        )

        assert isinstance(event, PaymentEventIn)


def test_customer_success_rate_is_valid():
    events = generate_batch(1000, seed=42)

    for event in events:
        assert 0.0 <= event.customer_previous_success_rate <= 1.0


def test_transaction_amounts_are_positive():
    events = generate_batch(1000, seed=42)

    for event in events:
        assert event.amount > 0


def test_scenarios_match_classifier():
    expected_categories = {
        "temporary_failure": RiskCategory.TEMPORARY_FAILURE,
        "insufficient_funds": RiskCategory.INSUFFICIENT_FUNDS,
        "payment_method_problem": RiskCategory.PAYMENT_METHOD_PROBLEM,
        "risk_failure": RiskCategory.SUSPECTED_RISK_FAILURE,
        "unknown_failure": RiskCategory.UNKNOWN,
    }

    for scenario, expected_category in expected_categories.items():
        event = generate_payment_event(
            scenario=scenario,
            seed=42,
        )

        result = classify_payment_event(event)

        assert result.category == expected_category