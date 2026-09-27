from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate
from app.services.payment_service import PaymentService


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
            modifier_total = sum(
                (
                    modifier.price
                    for modifier in item.modifiers
                ),
                Decimal("0.00"),
            )

            item_price = (
                item.unit_price
                + modifier_total
            )

            subtotal = (
                item_price
                * item.quantity
            )

            total_amount += subtotal

            order_items.append(
                OrderItem(
                    item_name=item.item_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=subtotal,
                    modifiers=[
                        {
                            "name": modifier.name,
                            "price": float(
                                modifier.price
                            ),
                        }
                        for modifier in item.modifiers
                    ],
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
    def get_paid_orders(
        db: Session,
    ) -> list[Order]:
        return OrderRepository.get_paid_orders(db)

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

        if order is None:
            return None

        if status == "PREPARING":

            if order.status != "PAID":
                raise ValueError(
                    "Only paid orders can start preparation"
                )

        elif status == "READY":

            if order.status != "PREPARING":
                raise ValueError(
                    "Only preparing orders can be marked ready"
                )

        else:
            raise ValueError(
                "Invalid order status"
            )

        order.status = status

        db.commit()
        db.refresh(order)

        return order

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

        if order.status not in (
            "CREATED",
            "PAID",
        ):
            raise ValueError(
                "Order can only be cancelled before preparation starts"
            )

        if order.status == "PAID":
            PaymentService.refund_payment(
                db=db,
                order_id=order.id,
            )

        order.status = "CANCELLED"

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def cancel_order_by_barista(
        db: Session,
        order_id: int,
        reason: str,
    ) -> Order | None:

        order = OrderRepository.get_order_by_id(
            db,
            order_id,
        )

        if order is None:
            return None

        if order.status not in (
            "PREPARING",
            "READY",
        ):
            raise ValueError(
                "Barista can cancel only after preparation has started"
            )

        if not reason.strip():
            raise ValueError(
                "Cancellation reason is required"
            )

        order.status = "CANCELLED"
        order.cancellation_reason = reason.strip()

        db.commit()
        db.refresh(order)

        return order