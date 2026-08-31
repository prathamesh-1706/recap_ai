from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    __table_args__ = (
        UniqueConstraint(
            "idempotency_key",
            name="uq_payment_events_idempotency_key",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    payment_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    order_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    customer_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    method: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    error_code: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    error_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    customer_previous_success_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )