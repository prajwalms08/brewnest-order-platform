import json

from app.integrations.razorpay import RazorpayClient
from app.models.payment import Payment
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentVerify


router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PaymentResponse)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
):
    return PaymentService.create_payment(
        db=db,
        payment_data=payment_data,
    )

@router.post("/verify", response_model=PaymentResponse)
def verify_payment(
    payment_data: PaymentVerify,
    db: Session = Depends(get_db),
):
    return PaymentService.verify_payment(
        db=db,
        payment_data=payment_data,
    )

@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_razorpay_signature: str = Header(
        ...,
        alias="X-Razorpay-Signature",
    ),
    db: Session = Depends(get_db),
):
    body = await request.body()
    body_text = body.decode("utf-8")

    razorpay_client = RazorpayClient()

    try:
        razorpay_client.verify_webhook_signature(
            body_text,
            x_razorpay_signature,
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature",
        )

    try:
        payload = json.loads(body_text)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        )

    event = payload.get("event")

    payment_entity = (
        payload.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    razorpay_order_id = payment_entity.get("order_id")
    razorpay_payment_id = payment_entity.get("id")

    if not razorpay_order_id or not razorpay_payment_id:
        return {
            "status": "ignored",
            "message": "Payment information not found",
        }

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_order_id
            == razorpay_order_id
        )
        .first()
    )

    if payment is None:
        return {
            "status": "ignored",
            "message": "Payment record not found",
        }

    if event in (
        "payment.captured",
        "payment.authorized",
    ):
        payment.razorpay_payment_id = (
            razorpay_payment_id
        )
        payment.status = "PAID"

        db.commit()

    return {
        "status": "processed",
        "event": event,
    }