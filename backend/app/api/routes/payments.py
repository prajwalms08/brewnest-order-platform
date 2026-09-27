from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    Request,
)
from sqlalchemy.orm import Session

import json

from app.db.session import SessionLocal
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)
from app.services.payment_service import (
    PaymentService,
)


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

    from app.integrations.razorpay import (
        RazorpayClient,
    )

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

    return {
        "status": "received",
        "event": payload.get("event"),
    }