from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:

    @staticmethod
    def create_payment(
        db: Session,
        payment: Payment,
    ) -> Payment:
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment