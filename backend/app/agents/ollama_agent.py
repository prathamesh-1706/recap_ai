import json
import urllib.request

from app.agents.base import AgentProposal, RecoveryAgent
from app.core.config import get_settings
from app.core.enums import RiskCategory, RecoveryAction
from app.schemas.payment_event import PaymentEventIn
from app.services.customer_context import CustomerContext


class OllamaRecoveryAgent(RecoveryAgent):
    """Local LLM recovery agent powered by Ollama."""

    def __init__(self) -> None:
        settings = get_settings()

        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    def propose(
        self,
        event: PaymentEventIn,
        risk_category: RiskCategory,
        classifier_reason: str,
        customer_context: CustomerContext,
    ) -> AgentProposal:

        prompt = f"""
You are RECAP, a conservative fintech payment recovery decision engine.

You ONLY propose an action. You NEVER execute payments.

Allowed actions:
- RETRY
- WAIT_AND_RETRY
- REQUEST_PAYMENT_METHOD_UPDATE
- SEND_RECOVERY_MESSAGE
- ESCALATE
- NO_ACTION

Payment:
payment_id: {event.payment_id}
amount: {event.amount}
currency: {event.currency}
status: {event.status}
method: {event.method}
error_code: {event.error_code}
error_description: {event.error_description}
retry_count: {event.retry_count}

Risk:
category: {risk_category.value}
reason: {classifier_reason}

Customer:
success_rate: {customer_context.success_rate}
reliability: {customer_context.reliability}
retry_pressure: {customer_context.retry_pressure}
amount_segment: {customer_context.amount_segment}
payment_method: {customer_context.payment_method}

Rules:
- Never RETRY suspected risk/fraud.
- Never RETRY payment-method problems.
- Unknown failures must not trigger financial action.
- Consider retry count.
- Prefer NO_ACTION or ESCALATE when uncertain.
- confidence must be between 0 and 1.
- estimated_recovery_amount must be 0 when recovery should not occur.

Return ONLY valid JSON:

{{
  "recommended_action": "ONE_ALLOWED_ACTION",
  "confidence": 0.0,
  "reason": "brief explanation",
  "estimated_recovery_amount": 0
}}
"""

        request_body = json.dumps(
            {
                "model": self._model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self._base_url}/api/generate",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))

        raw_response = payload.get("response")

        if not raw_response:
            raise RuntimeError("Ollama returned an empty response.")

        try:
            proposal_data = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc

        return AgentProposal.model_validate(proposal_data)