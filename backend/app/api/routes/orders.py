from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.db.session import SessionLocal
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.websocket.manager import manager

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    return OrderService.create_order(db, order_data)

@router.get("/", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
):
    return OrderService.get_orders(db)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = OrderService.get_order_by_id(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order

@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    order = OrderService.update_order_status(
        db,
        order_id,
        status,
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

    return {
        "id": order.id,
        "status": order.status,
    }