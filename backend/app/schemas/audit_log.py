from datetime import datetime

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    payment_id: str
    event_type: str
    risk_category: str
    proposed_action: str
    policy_decision: str
    reason: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }