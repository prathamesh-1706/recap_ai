from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import HealthOut
from app.schemas.payment_event import PaymentEventIn
from app.schemas.recommendation import RecommendationOut
from app.services.event_service import PaymentEventService
from app.webhooks.razorpay import handle_razorpay_webhook

router = APIRouter()
_service = PaymentEventService()


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", service="recap-api")


@router.post(
    "/api/v1/events/payment",
    response_model=RecommendationOut,
)
def create_payment_event(
    payload: PaymentEventIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
) -> RecommendationOut:
    return _service.ingest_payment_event(
        db,
        payload,
        idempotency_key,
    )


@router.get(
    "/api/v1/recommendations/{payment_id}",
    response_model=RecommendationOut,
)
def get_recommendation(
    payment_id: str,
    db: Session = Depends(get_db),
) -> RecommendationOut:
    result = _service.get_latest_recommendation(
        db,
        payment_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    return result


@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    return await handle_razorpay_webhook(
        request,
        db,
    )