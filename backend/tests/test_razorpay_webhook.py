import hashlib
import hmac
import json
from datetime import UTC, datetime

from app.webhooks.razorpay import verify_razorpay_signature
from tests.conftest import client


WEBHOOK_SECRET = "your_test_webhook_secret"


def make_signature(payload: bytes) -> str:
    return hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()


def razorpay_payload(
    event: str = "payment.failed",
) -> dict:
    return {
        "entity": "event",
        "event": event,
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_razorpay_001",
                    "entity": "payment",
                    "amount": 50000,
                    "currency": "INR",
                    "status": "failed",
                    "order_id": "order_razorpay_001",
                    "method": "card",
                    "error_code": "GATEWAY_ERROR",
                    "error_description": "Gateway timed out",
                    "created_at": int(datetime.now(UTC).timestamp()),
                    "notes": {
                        "customer_id": "cust_razorpay_001",
                    },
                },
            },
        },
    }


def test_signature_verification():
    payload = b'{"event":"payment.failed"}'

    signature = make_signature(payload)

    assert verify_razorpay_signature(
        payload,
        signature,
        WEBHOOK_SECRET,
    )

    assert not verify_razorpay_signature(
        payload,
        "invalid-signature",
        WEBHOOK_SECRET,
    )


def test_valid_payment_failed_webhook():
    api = client()

    payload = razorpay_payload()
    raw_body = json.dumps(payload).encode()

    signature = make_signature(raw_body)

    response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
            "x-razorpay-event-id": "evt_test_001",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "processed"
    assert body["event"] == "payment.failed"
    assert body["payment_id"] == "pay_razorpay_001"
    assert body["recommendation"] == "WAIT_AND_RETRY"


def test_invalid_signature():
    api = client()

    payload = razorpay_payload()
    raw_body = json.dumps(payload).encode()

    response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": "invalid",
            "x-razorpay-event-id": "evt_test_002",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Razorpay webhook signature"


def test_missing_signature():
    api = client()

    payload = razorpay_payload()
    raw_body = json.dumps(payload).encode()

    response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "x-razorpay-event-id": "evt_test_003",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing Razorpay signature"


def test_missing_event_id():
    api = client()

    payload = razorpay_payload()
    raw_body = json.dumps(payload).encode()

    signature = make_signature(raw_body)

    response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Missing Razorpay event ID"


def test_non_payment_failed_event_is_ignored():
    api = client()

    payload = razorpay_payload(event="payment.captured")
    raw_body = json.dumps(payload).encode()

    signature = make_signature(raw_body)

    response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
            "x-razorpay-event-id": "evt_test_004",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ignored"
    assert body["event"] == "payment.captured"

def test_duplicate_webhook_is_idempotent():
    api = client()

    payload = razorpay_payload()
    raw_body = json.dumps(payload).encode()

    signature = make_signature(raw_body)

    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "x-razorpay-event-id": "evt_duplicate_001",
    }

    first_response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers=headers,
    )

    second_response = api.post(
        "/webhooks/razorpay",
        content=raw_body,
        headers=headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_body = first_response.json()
    second_body = second_response.json()

    assert first_body["status"] == "processed"
    assert second_body["status"] == "processed"

    assert first_body["payment_id"] == second_body["payment_id"]
    assert first_body["recommendation"] == second_body["recommendation"]

   

