from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations.razorpay import RazorpayClient
from app.models.order import Order
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentVerify


class PaymentService:

    @staticmethod
    def create_payment(
        db: Session,
        payment_data: PaymentCreate,
    ) -> Payment:

        order = (
            db.query(Order)
            .filter(Order.id == payment_data.order_id)
            .first()
        )

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        amount_in_paise = int(payment_data.amount * 100)

        razorpay_client = RazorpayClient()

        razorpay_order = razorpay_client.create_order(
            amount=amount_in_paise,
            currency="INR",
        )

        payment = Payment(
            order_id=payment_data.order_id,
            razorpay_order_id=razorpay_order["id"],
            amount=payment_data.amount,
            status="CREATED",
        )

        return PaymentRepository.create_payment(
            db=db,
            payment=payment,
        )

    @staticmethod
    def verify_payment(
        db: Session,
        payment_data: PaymentVerify,
    ) -> Payment:

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_order_id
                == payment_data.razorpay_order_id
            )
            .first()
        )

        if payment is None:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        razorpay_client = RazorpayClient()

        try:
            razorpay_client.verify_payment_signature(
                razorpay_order_id=payment_data.razorpay_order_id,
                razorpay_payment_id=payment_data.razorpay_payment_id,
                razorpay_signature=payment_data.razorpay_signature,
            )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Payment verification failed",
            )

        payment.razorpay_payment_id = (
            payment_data.razorpay_payment_id
        )
        payment.status = "PAID"

        db.commit()
        db.refresh(payment)

        return payment


    @staticmethod
    def refund_payment(
        db: Session,
        order_id: int,
    ) -> Payment:

        payment = (
            db.query(Payment)
            .filter(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc())
            .first()
        )

        if payment is None:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        if payment.status != "PAID":
            raise HTTPException(
                status_code=400,
                detail="Payment must be PAID before refund",
            )

        if payment.razorpay_payment_id is None:
            raise HTTPException(
                status_code=400,
                detail="Razorpay payment ID not found",
            )

        razorpay_client = RazorpayClient()

        try:
            refund = razorpay_client.refund_payment(
                razorpay_payment_id=payment.razorpay_payment_id,
                amount=int(payment.amount * 100),
            )
        except Exception as exc:
            print("Razorpay refund error:", exc)

            raise HTTPException(
                status_code=400,
                detail=f"Refund failed: {exc}",
            )

        payment.refund_id = refund["id"]
        payment.status = "REFUNDED"

        db.commit()
        db.refresh(payment)

        return payment