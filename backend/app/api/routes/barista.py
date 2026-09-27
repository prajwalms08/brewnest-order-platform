from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.order import OrderResponse
from app.services.order_service import OrderService
from app.websocket.manager import manager


router = APIRouter(
    prefix="/barista",
    tags=["Barista"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/orders/",
    response_model=list[OrderResponse],
)
def get_paid_orders(
    db: Session = Depends(get_db),
):
    return OrderService.get_paid_orders(db)


@router.patch(
    "/orders/{order_id}/cancel",
    response_model=OrderResponse,
)
async def cancel_order(
    order_id: int,
    reason: str,
    db: Session = Depends(get_db),
):
    try:
        order = OrderService.cancel_order_by_barista(
            db=db,
            order_id=order_id,
            reason=reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    await manager.send_status(
        order.id,
        order.status,
    )

    return order