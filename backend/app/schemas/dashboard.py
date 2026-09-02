from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_payments: int
    failed_payments: int
    recovered_amount: int
    recovery_rate: float


class RecoveryTrendPoint(BaseModel):
    day: str
    recovered: int
    attempts: int


class DecisionOut(BaseModel):
    payment_id: str
    customer_id: str
    risk: str
    action: str
    confidence: float
    amount: int
    status: str


class RiskBreakdown(BaseModel):
    category: str
    count: int


class DashboardOut(BaseModel):
    stats: DashboardStats
    recovery_trend: list[RecoveryTrendPoint]
    decisions: list[DecisionOut]
    risk_breakdown: list[RiskBreakdown]
