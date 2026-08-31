from pydantic import BaseModel, Field

from app.core.enums import RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn
from app.services.customer_context import CustomerContext


class AgentProposal(BaseModel):
    """Structured proposal produced by a recovery agent.

    The agent proposes an action only.
    It must never execute financial actions directly.
    """

    recommended_action: RecoveryAction
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    estimated_recovery_amount: int


class RecoveryAgent:
    """Interface for recovery decision agents.

    Implementations may use deterministic rules or AI/LLM reasoning.
    Agents only propose actions. The PolicyEngine remains the final
    authority over whether an action is allowed.
    """

    def propose(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        classifier_reason: str,
        customer_context: CustomerContext,
    ) -> AgentProposal:
        raise NotImplementedError