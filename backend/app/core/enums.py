from enum import StrEnum


class PaymentStatus(StrEnum):
    FAILED = "failed"
    CAPTURED = "captured"


class RiskCategory(StrEnum):
    TEMPORARY_FAILURE = "temporary_failure"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    PAYMENT_METHOD_PROBLEM = "payment_method_problem"
    SUSPECTED_RISK_FAILURE = "suspected_risk_failure"
    UNKNOWN = "unknown"


class RecoveryAction(StrEnum):
    RETRY = "RETRY"
    WAIT_AND_RETRY = "WAIT_AND_RETRY"
    REQUEST_PAYMENT_METHOD_UPDATE = "REQUEST_PAYMENT_METHOD_UPDATE"
    SEND_RECOVERY_MESSAGE = "SEND_RECOVERY_MESSAGE"
    ESCALATE = "ESCALATE"
    NO_ACTION = "NO_ACTION"


class PolicyDecision(StrEnum):
    """Milestone 1 uses APPROVED/DENIED (architecture docs say approved/rejected)."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
