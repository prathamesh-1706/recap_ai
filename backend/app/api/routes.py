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
from app.schemas.dashboard import DashboardOut
from app.schemas.simulator import SimulatorRequest
from app.schemas.audit_log import AuditLogOut

from app.services.event_service import PaymentEventService
from app.services.dashboard_service import DashboardService
from app.services.audit_log_service import AuditLogService

from app.simulator.generator import PaymentEventGenerator
from app.webhooks.razorpay import handle_razorpay_webhook


router = APIRouter()


_service = PaymentEventService()
_dashboard_service = DashboardService()
_audit_log_service = AuditLogService()
_simulator_service = PaymentEventGenerator()


def get_dashboard_service() -> DashboardService:
    return _dashboard_service


def get_event_service() -> PaymentEventService:
    return _service


@router.get(
    "/health",
    response_model=HealthOut,
)
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        service="recap-api",
    )


@router.get(
    "/dashboard",
    response_model=DashboardOut,
)
def get_dashboard(
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOut:
    return service.get_dashboard(db)


@router.get(
    "/api/v1/audit-logs",
    response_model=list[AuditLogOut],
)
def get_audit_logs(
    db: Session = Depends(get_db),
) -> list[AuditLogOut]:
    return _audit_log_service.get_audit_logs(db)


@router.post(
    "/api/v1/events/payment",
    response_model=RecommendationOut,
)
def create_payment_event(
    payload: PaymentEventIn,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
    ),
    db: Session = Depends(get_db),
    service: PaymentEventService = Depends(get_event_service),
) -> RecommendationOut:
    return service.ingest_payment_event(
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
    service: PaymentEventService = Depends(get_event_service),
) -> RecommendationOut | None:
    result = service.get_latest_recommendation(
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


@router.post("/api/v1/simulator/generate")
def simulate_payment(
    payload: SimulatorRequest,
    db: Session = Depends(get_db),
    service: PaymentEventService = Depends(get_event_service),
):
    event = _simulator_service.generate_payment_event(
        scenario=payload.scenario,
    )

    idempotency_key = f"sim_{event.payment_id}"

    return service.ingest_payment_event(
        db,
        event,
        idempotency_key,
    )