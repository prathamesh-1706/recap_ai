from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def payment_event_payload(**overrides) -> dict:
    payload = {
        "payment_id": "pay_test_001",
        "order_id": "order_test_001",
        "customer_id": "cust_test_001",
        "amount": 50000,
        "currency": "INR",
        "status": "failed",
        "method": "card",
        "error_code": "GATEWAY_ERROR",
        "error_description": "Gateway timed out",
        "retry_count": 0,
        "customer_previous_success_rate": 0.8,
        "created_at": datetime.now(UTC).isoformat(),
    }
    payload.update(overrides)
    return payload


def client() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
