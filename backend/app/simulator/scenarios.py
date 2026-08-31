from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PaymentScenario:
    name: str
    status: str
    method: str
    error_code: Optional[str]
    error_description: Optional[str]


SCENARIOS = {
    "successful_payment": PaymentScenario(
        name="successful_payment",
        status="captured",
        method="upi",
        error_code=None,
        error_description=None,
    ),

    "temporary_failure": PaymentScenario(
        name="temporary_failure",
        status="failed",
        method="upi",
        error_code="BANK_TIMEOUT",
        error_description="Temporary bank timeout",
    ),

    "insufficient_funds": PaymentScenario(
        name="insufficient_funds",
        status="failed",
        method="card",
        error_code="INSUFFICIENT_FUNDS",
        error_description="Customer has insufficient funds",
    ),

    "payment_method_problem": PaymentScenario(
        name="payment_method_problem",
        status="failed",
        method="card",
        error_code="EXPIRED_CARD",
        error_description="Payment method requires customer attention",
    ),

    "risk_failure": PaymentScenario(
        name="risk_failure",
        status="failed",
        method="card",
        error_code="FRAUD",
        error_description="Payment rejected by risk controls",
    ),

    "unknown_failure": PaymentScenario(
        name="unknown_failure",
        status="failed",
        method="upi",
        error_code="UNKNOWN_ERROR",
        error_description="Unknown payment failure",
    ),
}
