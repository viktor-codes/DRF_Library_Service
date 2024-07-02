from celery import shared_task
from datetime import timedelta
from django.utils.timezone import now
from .models import Borrowing
from helpers.telegram_helper import send_message


@shared_task
def check_borrowings_overdue():
    borrowings = Borrowing.objects.all()
    today = now().date()
    tomorrow = today + timedelta(days=1)
    overdue_borrowings = [
        borrowing
        for borrowing in borrowings
        if borrowing.expected_returning_date <= tomorrow
        and not borrowing.actual_returning_date
    ]

    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue Borrowing Alert:\n"
                f"Book: {borrowing.book.title}\n"
                f"User: {borrowing.user}\n"
                f"Borrowing Date: {borrowing.borrowing_date}\n"
                f"Expected Returning Date: {borrowing.expected_returning_date}\n"
                f"Status: Overdue"
            )
            send_message(message)
    else:
        send_message("No borrowings overdue today!")
