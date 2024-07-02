from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Borrowing
from helpers.telegram_helper import send_message


@receiver(post_save, sender=Borrowing)
def send_notification_on_borrowing_creation(
    sender, instance, created, **kwargs
):
    if created:
        message = (
            f"New borrowing created:\n"
            f"Book: {instance.book.title}\n"
            f"User: {instance.user}\n"
            f"Borrowing Date: {instance.borrowing_date}\n"
            f"Expected Returning Date: {instance.expected_returning_date}"
        )

        send_message(message)
