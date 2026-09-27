import razorpay

from app.core.config import settings


class RazorpayClient:

    def __init__(self):
        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

    def create_order(self, amount: int, currency: str = "INR"):
        return self.client.order.create(
            {
                "amount": amount,
                "currency": currency,
            }
        )