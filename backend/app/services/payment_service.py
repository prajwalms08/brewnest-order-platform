from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations.razorpay import RazorpayClient
from app.models.order import Order
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentCreate


class PaymentService:

    @staticmethod
    def create_payment(
        db: Session,
        payment_data: PaymentCreate,
    ) -> Payment:

        order = (
            db.query(Order)
            .filter(
                Order.id == payment_data.order_id
            )
            .first()
        )

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        if order.status not in (
            "CREATED",
            "PAID",
        ):
            raise HTTPException(
                status_code=400,
                detail="Order is not available for payment",
            )

        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.order_id
                == payment_data.order_id
            )
            .order_by(
                Payment.created_at.desc()
            )
            .first()
        )

        if existing_payment:

            if existing_payment.status == "PAID":
                raise HTTPException(
                    status_code=400,
                    detail="Order is already paid",
                )

            if existing_payment.status == "REFUNDED":
                raise HTTPException(
                    status_code=400,
                    detail="Refunded order cannot be paid again",
                )

            return existing_payment

        # The amount comes from PostgreSQL,
        # never from the frontend.
        amount = order.total_amount

        amount_in_paise = int(
            amount * 100
        )

        razorpay_client = RazorpayClient()

        razorpay_order = (
            razorpay_client.create_order(
                amount=amount_in_paise,
                currency="INR",
            )
        )

        payment = Payment(
            order_id=order.id,
            razorpay_order_id=razorpay_order["id"],
            amount=amount,
            status="CREATED",
        )

        return PaymentRepository.create_payment(
            db=db,
            payment=payment,
        )

    @staticmethod
    def refund_payment(
        db: Session,
        order_id: int,
    ) -> Payment:

        payment = (
            db.query(Payment)
            .filter(
                Payment.order_id == order_id
            )
            .order_by(
                Payment.created_at.desc()
            )
            .first()
        )

        if payment is None:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        if payment.status == "REFUNDED":
            return payment

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
                razorpay_payment_id=(
                    payment.razorpay_payment_id
                ),
                amount=int(
                    payment.amount * 100
                ),
            )
        except Exception as exc:
            print(
                "Razorpay refund error:",
                exc,
            )

            raise HTTPException(
                status_code=400,
                detail="Refund failed",
            )

        payment.refund_id = refund["id"]
        payment.status = "REFUNDED"

        db.commit()
        db.refresh(payment)

        return payment