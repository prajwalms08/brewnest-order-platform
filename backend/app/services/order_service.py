from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate


class OrderService:

    @staticmethod
    def create_order(
        db: Session,
        order_data: OrderCreate,
    ) -> Order:

        if not order_data.items:
            raise ValueError(
                "Order must contain at least one item"
            )

        total_amount = Decimal("0.00")
        order_items = []

        for item in order_data.items:
            subtotal = (
                item.unit_price * item.quantity
            )

            total_amount += subtotal

            order_items.append(
                OrderItem(
                    item_name=item.item_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=subtotal,
                )
            )

        order = Order(
            status="CREATED",
            total_amount=total_amount,
        )

        return OrderRepository.create_order(
            db=db,
            order=order,
            items=order_items,
        )

    @staticmethod
    def get_orders(
        db: Session,
    ) -> list[Order]:

        return OrderRepository.get_orders(db)

    @staticmethod
    def get_order_by_id(
        db: Session,
        order_id: int,
    ) -> Order | None:

        return OrderRepository.get_order_by_id(
            db,
            order_id,
        )

    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        status: str,
    ) -> Order | None:

        order = OrderRepository.get_order_by_id(
            db,
            order_id,
        )

    @staticmethod
    def cancel_order(
        db: Session,
        order_id: int,
    ) -> Order | None:

        order = OrderRepository.get_order_by_id(
            db,
            order_id,
        )

        if order is None:
            return None

        if order.status != "CREATED":
            raise ValueError(
                "Order cannot be cancelled after preparation has started"
            )

        order.status = "CANCELLED"

        db.commit()
        db.refresh(order)

        return order    

        if order is None:  
            return None

        allowed_statuses = [
            "CREATED",
            "PREPARING",
            "READY",
        ]

        if status not in allowed_statuses:
            raise ValueError(
                "Invalid order status"
            )

        order.status = status

        db.commit()
        db.refresh(order)

        return order