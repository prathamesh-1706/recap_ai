from datetime import datetime, timedelta, timezone
import random
import uuid

from app.schemas.payment_event import PaymentEventIn
from app.simulator.scenarios import SCENARIOS


CUSTOMER_PROFILES = {
    "high_reliability": (0.90, 0.99),
    "medium_reliability": (0.60, 0.89),
    "low_reliability": (0.20, 0.59),
}


class PaymentEventGenerator:
    """Generate deterministic synthetic payment events for RECAP testing."""

    def __init__(self, seed: int | None = None):
        self.random = random.Random(seed)

    def _customer_success_rate(self) -> float:
        """Generate a customer reliability score."""
        profile = self.random.choice(list(CUSTOMER_PROFILES.values()))
        minimum, maximum = profile
        return round(self.random.uniform(minimum, maximum), 2)

    def _amount(self) -> int:
        """Generate a realistic INR transaction amount."""
        return self.random.choice(
            [
                199,
                299,
                499,
                799,
                999,
                1499,
                1999,
                2499,
                4999,
                9999,
                14999,
                24999,
            ]
        )

    def _created_at(self) -> datetime:
        """Generate a deterministic synthetic creation timestamp."""
        base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        seconds_offset = self.random.randint(
            0,
            365 * 24 * 60 * 60,
        )

        return base_time + timedelta(seconds=seconds_offset)

    def generate_payment_event(
        self,
        scenario: str | None = None,
    ) -> PaymentEventIn:
        """Generate one synthetic payment event."""

        if scenario is None:
            scenario = self.random.choice(list(SCENARIOS.keys()))

        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")

        selected = SCENARIOS[scenario]

        payment_id = (
            f"pay_sim_{uuid.UUID(int=self.random.getrandbits(128))}"
        )

        order_id = (
            f"order_sim_{uuid.UUID(int=self.random.getrandbits(128))}"
        )

        customer_id = (
            f"cust_sim_{self.random.randint(100000, 999999)}"
        )

        retry_count = 0

        if selected.status == "failed":
            retry_count = self.random.randint(0, 3)

        return PaymentEventIn(
            payment_id=payment_id,
            order_id=order_id,
            customer_id=customer_id,
            amount=self._amount(),
            currency="INR",
            status=selected.status,
            method=selected.method,
            error_code=selected.error_code,
            error_description=selected.error_description,
            retry_count=retry_count,
            customer_previous_success_rate=self._customer_success_rate(),
            created_at=self._created_at(),
        )

    def generate_batch(
        self,
        count: int,
    ) -> list[PaymentEventIn]:
        """Generate a batch of synthetic payment events."""

        if count <= 0:
            raise ValueError("count must be greater than zero")

        return [
            self.generate_payment_event()
            for _ in range(count)
        ]


def generate_payment_event(
    scenario: str | None = None,
    seed: int | None = None,
) -> PaymentEventIn:
    """Convenience function for generating one payment event."""

    generator = PaymentEventGenerator(seed=seed)

    return generator.generate_payment_event(
        scenario=scenario,
    )


def generate_batch(
    count: int,
    seed: int | None = None,
) -> list[PaymentEventIn]:
    """Convenience function for generating a batch."""

    generator = PaymentEventGenerator(seed=seed)

    return generator.generate_batch(
        count=count,
    )