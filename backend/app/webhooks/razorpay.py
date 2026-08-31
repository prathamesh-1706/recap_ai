import hashlib
import hmac
import json
from datetime import UTC, datetime

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.payment_event import PaymentEventIn
from app.services.event_service import PaymentEventService


def verify_razorpay_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


def build_payment_event(payload: dict) -> PaymentEventIn:
    payment = payload["payload"]["payment"]["entity"]

    created_at = payment.get("created_at")

    if isinstance(created_at, int | float):
        created_at = datetime.fromtimestamp(
            created_at,
            tz=UTC,
        )

    if created_at is None:
        created_at = datetime.now(UTC)

    return PaymentEventIn(
        payment_id=payment["id"],
        order_id=payment.get("order_id") or "unknown",
        customer_id=(
            payment.get("notes", {}).get("customer_id")
            or "unknown"
        ),
        amount=payment["amount"],
        currency=payment["currency"],
        status="failed",
        method=payment.get("method"),
        error_code=payment.get("error_code"),
        error_description=payment.get("error_description"),
        retry_count=0,
        customer_previous_success_rate=0.8,
        created_at=created_at,
    )


async def handle_razorpay_webhook(
    request: Request,
    db: Session,
) -> dict:
    settings = get_settings()

    raw_body = await request.body()

    signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay signature",
        )

    if not verify_razorpay_signature(
        raw_body,
        signature,
        settings.razorpay_webhook_secret,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature",
        )

    event_id = request.headers.get(
        "x-razorpay-event-id"
    )

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay event ID",
        )

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        ) from exc

    event_type = payload.get("event")

    if event_type != "payment.failed":
        return {
            "status": "ignored",
            "event": event_type,
        }

    payment_event = build_payment_event(payload)

    service = PaymentEventService()

    recommendation = service.ingest_payment_event(
        db=db,
        event=payment_event,
        idempotency_key=event_id,
    )

    return {
        "status": "processed",
        "event": event_type,
        "payment_id": recommendation.payment_id,
        "recommendation": recommendation.recommended_action,
    }