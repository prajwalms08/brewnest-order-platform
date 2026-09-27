from fastapi import APIRouter, Depends
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