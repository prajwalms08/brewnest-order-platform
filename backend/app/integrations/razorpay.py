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

    def create_order(
        self,
        amount: int,
        currency: str = "INR",
    ):
        return self.client.order.create(
            {
                "amount": amount,
                "currency": currency,
            }
        )

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> None:
        self.client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )

    def refund_payment(
        self,
        razorpay_payment_id: str,
        amount: int,
    ):
        return self.client.payment.refund(
            razorpay_payment_id,
            {
                "amount": amount,
            },
        )

    def verify_webhook_signature(
        self,
        body: str,
        signature: str,
    ) -> None:
        self.client.utility.verify_webhook_signature(
            body,
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET,
        )