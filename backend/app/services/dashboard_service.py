from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.payment_event import PaymentEvent
from app.models.recommendation import Recommendation
from app.schemas.dashboard import (
    DashboardOut,
    DashboardStats,
    DecisionOut,
    RecoveryTrendPoint,
    RiskBreakdown,
)


class DashboardService:
    def get_dashboard(self, db: Session) -> DashboardOut:
        total_payments = (
            db.query(func.count(PaymentEvent.id)).scalar() or 0
        )

        failed_payments = (
            db.query(func.count(PaymentEvent.id))
            .filter(PaymentEvent.status == "failed")
            .scalar()
            or 0
        )

        recovered_amount = (
            db.query(
                func.coalesce(
                    func.sum(Recommendation.estimated_recovery_amount),
                    0,
                )
            )
            .filter(Recommendation.policy_decision == "APPROVED")
            .scalar()
            or 0
        )

        actionable_recommendations = (
            db.query(func.count(Recommendation.id))
            .join(
                PaymentEvent,
                Recommendation.payment_id == PaymentEvent.payment_id,
            )
            .filter(
                PaymentEvent.status == "failed",
                Recommendation.policy_decision == "APPROVED",
                Recommendation.recommended_action.notin_(
                    ["ESCALATE", "NO_ACTION"]
                ),
            )
            .scalar()
            or 0
        )

        recovery_rate = (
            (actionable_recommendations / failed_payments) * 100
            if failed_payments
            else 0.0
        )

        recent_recommendations = (
            db.query(Recommendation, PaymentEvent)
            .join(
                PaymentEvent,
                Recommendation.payment_id == PaymentEvent.payment_id,
            )
            .order_by(
                Recommendation.created_at.desc(),
                Recommendation.id.desc(),
            )
            .limit(10)
            .all()
        )

        decisions = [
            DecisionOut(
                payment_id=recommendation.payment_id,
                customer_id=payment.customer_id,
                risk=recommendation.risk_category,
                action=recommendation.recommended_action,
                confidence=recommendation.confidence,
                amount=payment.amount,
                status=recommendation.policy_decision,
            )
            for recommendation, payment in recent_recommendations
        ]

        risk_rows = (
            db.query(
                Recommendation.risk_category,
                func.count(Recommendation.id),
            )
            .group_by(Recommendation.risk_category)
            .all()
        )

        risk_breakdown = [
            RiskBreakdown(
                category=category,
                count=count,
            )
            for category, count in risk_rows
        ]

        recovery_trend = self._get_recovery_trend(db)

        return DashboardOut(
            stats=DashboardStats(
                total_payments=total_payments,
                failed_payments=failed_payments,
                recovered_amount=int(recovered_amount),
                recovery_rate=round(recovery_rate, 2),
            ),
            recovery_trend=recovery_trend,
            decisions=decisions,
            risk_breakdown=risk_breakdown,
        )

    def _get_recovery_trend(
        self,
        db: Session,
    ) -> list[RecoveryTrendPoint]:
        now = datetime.now(timezone.utc)

        points: list[RecoveryTrendPoint] = []

        for offset in range(6, -1, -1):
            day = (now - timedelta(days=offset)).date()
            next_day = day + timedelta(days=1)

            attempts = (
                db.query(func.count(Recommendation.id))
                .filter(
                    Recommendation.created_at >= day,
                    Recommendation.created_at < next_day,
                )
                .scalar()
                or 0
            )

            recovered = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Recommendation.estimated_recovery_amount
                        ),
                        0,
                    )
                )
                .filter(
                    Recommendation.created_at >= day,
                    Recommendation.created_at < next_day,
                    Recommendation.policy_decision == "APPROVED",
                )
                .scalar()
                or 0
            )

            points.append(
                RecoveryTrendPoint(
                    day=day.strftime("%a"),
                    recovered=int(recovered),
                    attempts=int(attempts),
                )
            )

        return points