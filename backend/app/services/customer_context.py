from dataclasses import dataclass

from app.schemas.payment_event import PaymentEventIn


@dataclass(frozen=True)
class CustomerContext:
    customer_id: str
    success_rate: float
    reliability: str
    retry_count: int
    retry_pressure: str
    amount: int
    amount_segment: str
    payment_method: str | None


def build_customer_context(event: PaymentEventIn) -> CustomerContext:
    """Build structured customer/payment context for recovery decisions."""

    success_rate = event.customer_previous_success_rate

    if success_rate >= 0.90:
        reliability = "HIGH"
    elif success_rate >= 0.60:
        reliability = "MEDIUM"
    else:
        reliability = "LOW"

    if event.retry_count == 0:
        retry_pressure = "LOW"
    elif event.retry_count < 3:
        retry_pressure = "MEDIUM"
    else:
        retry_pressure = "HIGH"

    if event.amount < 1000:
        amount_segment = "LOW"
    elif event.amount < 10000:
        amount_segment = "MEDIUM"
    else:
        amount_segment = "HIGH"

    return CustomerContext(
        customer_id=event.customer_id,
        success_rate=success_rate,
        reliability=reliability,
        retry_count=event.retry_count,
        retry_pressure=retry_pressure,
        amount=event.amount,
        amount_segment=amount_segment,
        payment_method=event.method,
    )
    