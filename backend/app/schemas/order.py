from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    item_name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: Decimal

    class Config:
        from_attributes = True