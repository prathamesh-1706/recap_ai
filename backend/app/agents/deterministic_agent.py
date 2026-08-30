from app.agents.base import AgentProposal, RecoveryAgent
from app.core.enums import PaymentStatus, RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn


class DeterministicRecoveryAgent(RecoveryAgent):
    """Rule-based stub until LLM structured outputs are added. Does not execute."""

    def propose(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        classifier_reason: str,
    ) -> AgentProposal:
        if event.status != PaymentStatus.FAILED:
            return AgentProposal(
                recommended_action=RecoveryAction.NO_ACTION,
                confidence=1.0,
                reason="Payment is not failed; no recovery intervention is required.",
                estimated_recovery_amount=0,
            )

        estimated = event.amount

        if risk_category == RiskCategory.TEMPORARY_FAILURE:
            return AgentProposal(
                recommended_action=RecoveryAction.WAIT_AND_RETRY,
                confidence=0.78,
                reason=(
                    f"{classifier_reason} Temporary failures may recover after a short wait."
                ),
                estimated_recovery_amount=estimated,
            )

        if risk_category == RiskCategory.INSUFFICIENT_FUNDS:
            return AgentProposal(
                recommended_action=RecoveryAction.SEND_RECOVERY_MESSAGE,
                confidence=0.72,
                reason=(
                    f"{classifier_reason} Notify the customer to fund the account before retrying."
                ),
                estimated_recovery_amount=estimated,
            )

        if risk_category == RiskCategory.PAYMENT_METHOD_PROBLEM:
            return AgentProposal(
                recommended_action=RecoveryAction.REQUEST_PAYMENT_METHOD_UPDATE,
                confidence=0.86,
                reason=(
                    f"{classifier_reason} The customer should update the payment method."
                ),
                estimated_recovery_amount=estimated,
            )

        if risk_category == RiskCategory.SUSPECTED_RISK_FAILURE:
            return AgentProposal(
                recommended_action=RecoveryAction.ESCALATE,
                confidence=0.81,
                reason=(
                    f"{classifier_reason} Risk/fraud cases must not be auto-retried; escalate."
                ),
                estimated_recovery_amount=0,
            )

        return AgentProposal(
            recommended_action=RecoveryAction.ESCALATE,
            confidence=0.40,
            reason=(
                f"{classifier_reason} Unknown failures should not trigger an automatic "
                "financial action."
            ),
            estimated_recovery_amount=0,
        )
