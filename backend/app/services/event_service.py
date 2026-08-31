from sqlalchemy.orm import Session

from app.agents.base import RecoveryAgent
from app.agents.deterministic_agent import DeterministicRecoveryAgent
from app.models.audit_log import AuditLog
from app.models.payment_event import PaymentEvent
from app.models.recommendation import Recommendation
from app.policies.engine import PolicyEngine
from app.schemas.payment_event import PaymentEventIn
from app.schemas.recommendation import RecommendationOut
from app.services.customer_context import build_customer_context
from app.services.risk_classifier import classify_payment_event


class PaymentEventService:
    def __init__(
        self,
        agent: RecoveryAgent | None = None,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        self._agent = agent or DeterministicRecoveryAgent()
        self._policy = policy_engine or PolicyEngine()

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

        proposal = self._agent.propose(
            event,
            classification.category,
            classification.reason,
            customer_context,
        )

        policy_result = self._policy.evaluate(
            event,
            classification.category,
            proposal,
        )

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