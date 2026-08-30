from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.enums import PaymentStatus


class PaymentEventIn(BaseModel):
    payment_id: str
    order_id: str
    customer_id: str
    amount: int = Field(..., gt=0)
    currency: str
    status: str
    method: str | None = None
    error_code: str | None = None
    error_description: str | None = None
    retry_count: int = Field(..., ge=0)
    customer_previous_success_rate: float = Field(..., ge=0.0, le=1.0)
    created_at: datetime

    @field_validator("currency")
    @classmethod
    def currency_must_be_iso_code(cls, value: str) -> str:
        if len(value) != 3 or not value.isalpha() or value != value.upper():
            raise ValueError("currency must be a 3-character uppercase currency code")
        return value

    @field_validator("status")
    @classmethod
    def status_must_be_supported(cls, value: str) -> str:
        allowed = {item.value for item in PaymentStatus}
        if value not in allowed:
            raise ValueError(f"status must be one of: {sorted(allowed)}")
        return value
