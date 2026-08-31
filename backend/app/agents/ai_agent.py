from openai import OpenAI

from app.agents.base import AgentProposal, RecoveryAgent
from app.core.config import get_settings
from app.core.enums import RecoveryAction, RiskCategory
from app.schemas.payment_event import PaymentEventIn
from app.services.customer_context import CustomerContext


class AIRecoveryAgent(RecoveryAgent):
    """LLM-based recovery agent.

    The agent proposes an action only.
    It never executes financial operations.
    """

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self._client = OpenAI(
            api_key=settings.openai_api_key,
        )
        self._model = settings.openai_model

    def propose(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        classifier_reason: str,
        customer_context: CustomerContext,
    ) -> AgentProposal:

        prompt = f"""
You are the recovery decision engine for RECAP,
a payment recovery intelligence system.

You MUST ONLY recommend one of these actions:

- RETRY
- WAIT_AND_RETRY
- REQUEST_PAYMENT_METHOD_UPDATE
- SEND_RECOVERY_MESSAGE
- ESCALATE
- NO_ACTION

You are NOT allowed to execute any payment action.

Payment information:
payment_id: {event.payment_id}
amount: {event.amount}
currency: {event.currency}
status: {event.status}
method: {event.method}
error_code: {event.error_code}
error_description: {event.error_description}
retry_count: {event.retry_count}

Risk classification:
category: {risk_category.value}
classifier_reason: {classifier_reason}

Customer context:
success_rate: {customer_context.success_rate}
reliability: {customer_context.reliability}
retry_pressure: {customer_context.retry_pressure}
amount_segment: {customer_context.amount_segment}
payment_method: {customer_context.payment_method}

Choose the safest recovery action.

Important rules:
- Never recommend RETRY for suspected risk/fraud.
- Never recommend RETRY for payment-method problems.
- Do not recommend financial action for unknown failures.
- Consider retry count carefully.
- Prefer NO_ACTION or ESCALATE when uncertain.
- Confidence must be between 0 and 1.
- Explain the decision briefly.
- estimated_recovery_amount must be 0 when no recovery should occur.
"""

        response = self._client.responses.parse(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a conservative fintech recovery "
                        "decision agent."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            text_format=AgentProposal,
        )

        proposal = response.output_parsed

        if proposal is None:
            raise RuntimeError(
                "AI agent returned no structured proposal."
            )

        return proposal