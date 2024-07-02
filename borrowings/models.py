from django.db import models
from django.db.models import Q, CheckConstraint, F
from books.models import Book
from users.models import User


from django.dispatch import receiver
from django.db.models.signals import post_save

from helpers.telegram_helper import send_message


class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowing_date = models.DateField(auto_now_add=True)
    expected_returning_date = models.DateField()
    actual_returning_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(borrowing_date__lte=F("expected_returning_date")),
                name="borrow_date_before_or_equal_expected",
            ),
            CheckConstraint(
                check=Q(actual_returning_date__gte=F("borrowing_date")),
                name="actual_return_date_after_borrow_date",
            ),
        ]

    def __str__(self):
        return f"{self.user} borrowed {self.book}"


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
