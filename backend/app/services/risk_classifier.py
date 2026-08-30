from dataclasses import dataclass

from app.core.enums import RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn

TEMPORARY_ERROR_CODES = {
    "GATEWAY_ERROR",
    "SERVER_ERROR",
    "TIMEOUT",
    "NETWORK_ERROR",
    "BANK_TIMEOUT",
    "TEMPORARY_FAILURE",
    "ISSUER_UNAVAILABLE",
}

INSUFFICIENT_FUNDS_ERROR_CODES = {
    "INSUFFICIENT_FUNDS",
    "INSUFFICIENT_BALANCE",
}

PAYMENT_METHOD_ERROR_CODES = {
    "INVALID_CARD",
    "EXPIRED_CARD",
    "CARD_EXPIRED",
    "INVALID_VPA",
    "INVALID_PAYMENT_METHOD",
    "CARD_DECLINED",
    "BANK_ACCOUNT_INVALID",
    "PAYMENT_METHOD_NOT_SUPPORTED",
}

SUSPECTED_RISK_ERROR_CODES = {
    "PAYMENT_RISK",
    "FRAUD",
    "RISK_CHECK_FAILED",
    "SUSPECTED_FRAUD",
    "BLOCKED",
    "HIGH_RISK",
}


@dataclass(frozen=True)
class ClassificationResult:
    category: RiskCategory
    reason: str


def classify_payment_event(event: PaymentEventIn) -> ClassificationResult:
    """Deterministic MVP classifier. No LLM."""
    if event.status != "failed":
        return ClassificationResult(
            category=RiskCategory.UNKNOWN,
            reason="Payment is not in failed status; no failure category applies.",
        )

    code = (event.error_code or "").strip().upper()
    description = (event.error_description or "").lower()

    if code in TEMPORARY_ERROR_CODES or any(
        token in description for token in ("timeout", "temporarily", "gateway")
    ):
        if code in SUSPECTED_RISK_ERROR_CODES:
            return ClassificationResult(
                category=RiskCategory.SUSPECTED_RISK_FAILURE,
                reason=f"Error code {code} indicates a suspected risk or fraud failure.",
            )
        return ClassificationResult(
            category=RiskCategory.TEMPORARY_FAILURE,
            reason=f"Error code {code or 'n/a'} indicates a temporary or gateway failure.",
        )

    if code in INSUFFICIENT_FUNDS_ERROR_CODES or "insufficient" in description:
        return ClassificationResult(
            category=RiskCategory.INSUFFICIENT_FUNDS,
            reason=f"Error code {code or 'n/a'} indicates insufficient funds.",
        )

    if code in PAYMENT_METHOD_ERROR_CODES or any(
        token in description
        for token in ("expired card", "invalid card", "payment method", "invalid vpa")
    ):
        return ClassificationResult(
            category=RiskCategory.PAYMENT_METHOD_PROBLEM,
            reason=f"Error code {code or 'n/a'} indicates a payment-method problem.",
        )

    if code in SUSPECTED_RISK_ERROR_CODES or any(
        token in description for token in ("fraud", "risk", "blocked")
    ):
        return ClassificationResult(
            category=RiskCategory.SUSPECTED_RISK_FAILURE,
            reason=f"Error code {code or 'n/a'} indicates a suspected risk or fraud failure.",
        )

    return ClassificationResult(
        category=RiskCategory.UNKNOWN,
        reason=f"Error code {code or 'n/a'} could not be mapped to a known failure category.",
    )
