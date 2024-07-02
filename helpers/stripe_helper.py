import stripe
from decimal import Decimal
from django.conf import settings
from borrowings.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_session(borrowing):
    try:
        days_borrowed = (
            borrowing.expected_returning_date - borrowing.borrowing_date
        ).days
        total_price = Decimal(borrowing.book.daily_fee) * Decimal(
            days_borrowed
        )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": borrowing.book.title,
                        },
                        "unit_amount": int(total_price * 100),
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )

        payment = Payment.objects.create(
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
            borrowing=borrowing,
            session_url=checkout_session.url,
            session_id=checkout_session.id,
            money_to_pay=total_price,
            user=borrowing.user,
        )

        return payment

    except Exception as e:
        print(f"Error creating Stripe session: {str(e)}")
        return None
