from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem


class OrderRepository:

    @staticmethod
    def create_order(
        db: Session,
        order: Order,
        items: list[OrderItem],
    ) -> Order:

        db.add(order)
        db.flush()

        for item in items:
            item.order_id = order.id
            db.add(item)

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def get_orders(
        db: Session,
    ) -> list[Order]:

        return (
            db.query(Order)
            .order_by(Order.created_at.desc())
            .all()
        )

    @staticmethod
    def get_paid_orders(
        db: Session,
    ) -> list[Order]:

        return (
            db.query(Order)
            .options(
                joinedload(Order.items)
            )
            .filter(
                Order.status.in_(
                    [
                        "PAID",
                        "PREPARING",
                        "READY",
                    ]
                )
            )
            .order_by(
                Order.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_order_by_id(
        db: Session,
        order_id: int,
    ) -> Order | None:

        return (
            db.query(Order)
            .options(
                joinedload(Order.items)
            )
            .filter(
                Order.id == order_id
            )
            .first()
        )