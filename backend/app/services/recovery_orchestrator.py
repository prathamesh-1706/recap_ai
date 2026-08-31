from dataclasses import dataclass

from app.agents.ai_agent import AIRecoveryAgent
from app.agents.base import AgentProposal
from app.agents.deterministic_agent import DeterministicRecoveryAgent
from app.core.enums import PolicyDecision, RiskCategory
from app.policies.engine import PolicyEngine, PolicyResult
from app.schemas.payment_event import PaymentEventIn
from app.services.customer_context import CustomerContext


@dataclass(frozen=True)
class RecoveryDecision:
    proposal: AgentProposal
    policy_result: PolicyResult
    agent_used: str
    fallback_used: bool


class RecoveryOrchestrator:
    """Coordinates AI recovery, deterministic fallback, and policy validation.

    The orchestrator never executes financial actions.
    The PolicyEngine remains the final authority.
    """

    def __init__(
        self,
        ai_agent: AIRecoveryAgent | None = None,
        deterministic_agent: DeterministicRecoveryAgent | None = None,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        self._ai_agent = ai_agent
        self._deterministic_agent = (
            deterministic_agent or DeterministicRecoveryAgent()
        )
        self._policy_engine = policy_engine or PolicyEngine()

    def decide(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        classifier_reason: str,
        customer_context: CustomerContext,
    ) -> RecoveryDecision:

        fallback_used = False

        # Try AI first when available.
        if self._ai_agent is not None:
            try:
                proposal = self._ai_agent.propose(
                    event=event,
                    risk_category=risk_category,
                    classifier_reason=classifier_reason,
                    customer_context=customer_context,
                )

                agent_used = "ai"

            except Exception:
                # AI failure must never stop recovery processing.
                proposal = self._deterministic_agent.propose(
                    event=event,
                    risk_category=risk_category,
                    classifier_reason=classifier_reason,
                    customer_context=customer_context,
                )

                agent_used = "deterministic"
                fallback_used = True

        else:
            proposal = self._deterministic_agent.propose(
                event=event,
                risk_category=risk_category,
                classifier_reason=classifier_reason,
                customer_context=customer_context,
            )

            agent_used = "deterministic"
            fallback_used = True

        # PolicyEngine is ALWAYS applied after the agent proposes.
        policy_result = self._policy_engine.evaluate(
            event=event,
            risk_category=risk_category,
            proposal=proposal,
        )

        return RecoveryDecision(
            proposal=proposal,
            policy_result=policy_result,
            agent_used=agent_used,
            fallback_used=fallback_used,
        )