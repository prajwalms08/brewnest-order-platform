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