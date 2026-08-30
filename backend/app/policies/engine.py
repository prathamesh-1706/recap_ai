from dataclasses import dataclass

from app.agents.base import AgentProposal
from app.core.enums import PolicyDecision, RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn

POLICY_VERSION = "v1"
MAX_RETRIES = 3
FINANCIAL_ACTIONS = {RecoveryAction.RETRY, RecoveryAction.WAIT_AND_RETRY}


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    reason: str


class PolicyEngine:
    """Deterministic guardrail layer. Independent of the recovery agent / LLM."""

    def evaluate(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        proposal: AgentProposal,
    ) -> PolicyResult:
        action = proposal.recommended_action

        if event.retry_count >= MAX_RETRIES and action in FINANCIAL_ACTIONS:
            return PolicyResult(
                decision=PolicyDecision.DENIED,
                reason=f"Retry limit exceeded: retry_count={event.retry_count} (max {MAX_RETRIES}).",
            )

        if risk_category == RiskCategory.SUSPECTED_RISK_FAILURE and action in FINANCIAL_ACTIONS:
            return PolicyResult(
                decision=PolicyDecision.DENIED,
                reason="Risk/fraud failures must not automatically retry.",
            )

        if (
            risk_category == RiskCategory.PAYMENT_METHOD_PROBLEM
            and action in FINANCIAL_ACTIONS
        ):
            return PolicyResult(
                decision=PolicyDecision.DENIED,
                reason="Payment-method problems must request a payment-method update, not retry.",
            )

        if (
            risk_category == RiskCategory.PAYMENT_METHOD_PROBLEM
            and action != RecoveryAction.REQUEST_PAYMENT_METHOD_UPDATE
            and action != RecoveryAction.NO_ACTION
        ):
            if action != RecoveryAction.ESCALATE:
                return PolicyResult(
                    decision=PolicyDecision.DENIED,
                    reason="Payment-method problems should request a payment-method update.",
                )

        if risk_category == RiskCategory.UNKNOWN and action in FINANCIAL_ACTIONS:
            return PolicyResult(
                decision=PolicyDecision.DENIED,
                reason="Unknown failures must not automatically execute a financial action.",
            )

        if (
            risk_category == RiskCategory.TEMPORARY_FAILURE
            and action == RecoveryAction.WAIT_AND_RETRY
            and event.retry_count < MAX_RETRIES
        ):
            return PolicyResult(
                decision=PolicyDecision.APPROVED,
                reason="Temporary failures may use WAIT_AND_RETRY within the retry limit.",
            )

        return PolicyResult(
            decision=PolicyDecision.APPROVED,
            reason=f"Proposed action {action.value} is permitted for {risk_category.value}.",
        )
