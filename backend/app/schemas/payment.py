from decimal import Decimal

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_id: int


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    razorpay_order_id: str
    razorpay_payment_id: str | None = None
    refund_id: str | None = None
    amount: Decimal
    status: str

    class Config:
        from_attributes = True