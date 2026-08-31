from sqlalchemy.orm import Session

from app.agents.base import RecoveryAgent
from app.agents.deterministic_agent import DeterministicRecoveryAgent
from app.agents.ai_agent import AIRecoveryAgent
from app.core.config import get_settings
from app.models.audit_log import AuditLog
from app.models.payment_event import PaymentEvent
from app.models.recommendation import Recommendation
from app.policies.engine import PolicyEngine
from app.schemas.payment_event import PaymentEventIn
from app.schemas.recommendation import RecommendationOut
from app.services.customer_context import build_customer_context
from app.services.recovery_orchestrator import RecoveryOrchestrator
from app.services.risk_classifier import classify_payment_event

class PaymentEventService:
    def __init__(
        self,
        agent: RecoveryAgent | None = None,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        settings = get_settings()

        ai_agent = None

        if agent is not None:
            self._agent = agent
            ai_agent = agent

        elif settings.ai_agent_enabled:
            try:
                if settings.ai_provider.lower() == "ollama":
                    from app.agents.ollama_agent import OllamaRecoveryAgent

                    self._agent = OllamaRecoveryAgent()
                else:
                    self._agent = AIRecoveryAgent()

                ai_agent = self._agent

            except Exception:
                self._agent = DeterministicRecoveryAgent()

        else:
            self._agent = DeterministicRecoveryAgent()

        self._fallback_agent = DeterministicRecoveryAgent()
        self._policy = policy_engine or PolicyEngine()

        self._orchestrator = RecoveryOrchestrator(
            ai_agent=ai_agent,
            deterministic_agent=self._fallback_agent,
            policy_engine=self._policy,
        )

    def ingest_payment_event(
        self,
        db: Session,
        event: PaymentEventIn,
        idempotency_key: str,
    ) -> RecommendationOut:

        existing_event = (
            db.query(PaymentEvent)
            .filter(
                PaymentEvent.idempotency_key == idempotency_key
            )
            .first()
        )

        if existing_event is not None:
            existing_recommendation = (
                db.query(Recommendation)
                .filter(
                    Recommendation.payment_id
                    == existing_event.payment_id
                )
                .order_by(
                    Recommendation.created_at.desc(),
                    Recommendation.id.desc(),
                )
                .first()
            )

            if existing_recommendation is not None:
                return RecommendationOut.model_validate(
                    existing_recommendation
                )

        stored_event = PaymentEvent(
            **event.model_dump(),
            idempotency_key=idempotency_key,
        )

        db.add(stored_event)
        db.flush()

        classification = classify_payment_event(event)

        customer_context = build_customer_context(event)

        decision = self._orchestrator.decide(
            event=event,
            risk_category=classification.category,
            classifier_reason=classification.reason,
            customer_context=customer_context,
        )

        proposal = decision.proposal
        policy_result = decision.policy_result

        recommendation = Recommendation(
            payment_id=event.payment_id,
            risk_category=classification.category.value,
            recommended_action=proposal.recommended_action.value,
            confidence=proposal.confidence,
            reason=(
                f"{proposal.reason} "
                f"Policy: {policy_result.reason}"
            ),
            estimated_recovery_amount=(
                proposal.estimated_recovery_amount
            ),
            policy_decision=policy_result.decision.value,
        )

        db.add(recommendation)

        audit = AuditLog(
            payment_id=event.payment_id,
            event_type=f"payment.{event.status}",
            risk_category=classification.category.value,
            proposed_action=proposal.recommended_action.value,
            policy_decision=policy_result.decision.value,
            reason=(
                f"{proposal.reason} "
                f"Policy: {policy_result.reason}"
            ),
        )

        db.add(audit)

        db.commit()
        db.refresh(recommendation)

        return RecommendationOut.model_validate(
            recommendation
        )

    def get_latest_recommendation(
        self,
        db: Session,
        payment_id: str,
    ) -> RecommendationOut | None:

        row = (
            db.query(Recommendation)
            .filter(
                Recommendation.payment_id == payment_id
            )
            .order_by(
                Recommendation.created_at.desc(),
                Recommendation.id.desc(),
            )
            .first()
        )

        if row is None:
            return None

        return RecommendationOut.model_validate(row)