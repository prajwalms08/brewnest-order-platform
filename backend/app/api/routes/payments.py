import json

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.integrations.razorpay import RazorpayClient
from app.models.order import Order
from app.models.payment import Payment
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)
from app.services.payment_service import (
    PaymentService,
)
from app.websocket.manager import manager
from backend.app.models import payment


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=PaymentResponse,
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
):
    return PaymentService.create_payment(
        db=db,
        payment_data=payment_data,
    )


@router.post(
    "/refund/{order_id}",
    response_model=PaymentResponse,
)
def refund_payment(
    order_id: int,
    db: Session = Depends(get_db),
):
    return PaymentService.refund_payment(
        db=db,
        order_id=order_id,
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
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    razorpay_order_id = payment_entity.get(
        "order_id"
    )

    razorpay_payment_id = payment_entity.get(
        "id"
    )

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

    # Duplicate webhook protection.
    if (
        payment.status == "PAID"
        and payment.razorpay_payment_id
        == razorpay_payment_id
    ):
        return {
            "status": "already_processed",
            "event": event,
        }

    if event == "payment.captured":
        payment.razorpay_payment_id = (
            razorpay_payment_id
        )

        payment.status = "PAID"

        order = (
            db.query(Order)
            .filter(
                Order.id == payment.order_id
            )
            .first()
        )

        if order:
            order.status = "PAID"

        db.commit()

        await manager.broadcast_barista(
            payment.order_id
        )

        return {
            "status": "processed",
            "event": event,
        "order_id": payment.order_id,
        }

    return {
        "status": "ignored",
        "event": event,
    }