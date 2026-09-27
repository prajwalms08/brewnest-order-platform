from fastapi import HTTPException
from sqlalchemy.orm import Session

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

        payment = Payment(
            order_id=payment_data.order_id,
            razorpay_order_id="TEMP_ORDER_ID",
            amount=payment_data.amount,
            status="CREATED",
        )

        return PaymentRepository.create_payment(
            db=db,
            payment=payment,
        )