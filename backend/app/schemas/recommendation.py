from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import PolicyDecision, RecoveryAction, RiskCategory


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: str
    risk_category: RiskCategory
    recommended_action: RecoveryAction
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    estimated_recovery_amount: int
    policy_decision: PolicyDecision
    created_at: datetime
