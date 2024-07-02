import stripe
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from borrowings.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_session(
    borrowing, request, payment_type=Payment.Type.PAYMENT, fine_amount=None
):
    try:
        if payment_type == Payment.Type.FINE and fine_amount is not None:
            total_price = fine_amount
        else:
            days_borrowed = (
                borrowing.expected_returning_date - borrowing.borrowing_date
            ).days
            total_price = Decimal(borrowing.book.daily_fee) * Decimal(
                days_borrowed
            )

        success_url = (
            request.build_absolute_uri(reverse("payment-success"))
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = (
            request.build_absolute_uri(reverse("payment-cancel"))
            + "?session_id={CHECKOUT_SESSION_ID}"
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
            success_url=success_url,
            cancel_url=cancel_url,
        )

        payment = Payment.objects.create(
            status=Payment.Status.PENDING,
            type=payment_type,
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
