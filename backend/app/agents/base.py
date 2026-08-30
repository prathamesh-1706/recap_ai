from dataclasses import dataclass

from app.core.enums import RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn


@dataclass(frozen=True)
class AgentProposal:
    """Structured proposal produced by the recovery agent (stub or future LLM)."""

    recommended_action: RecoveryAction
    confidence: float
    reason: str
    estimated_recovery_amount: int


class RecoveryAgent:
    """Interface for future AI reasoning. Implementations must not execute actions."""

    def propose(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        classifier_reason: str,
    ) -> AgentProposal:
        raise NotImplementedError
