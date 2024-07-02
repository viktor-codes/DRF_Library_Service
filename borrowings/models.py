from django.db import models
from django.db.models import Q, CheckConstraint, F
from books.models import Book
from users.models import User


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.actual_returning_date and self.expected_returning_date:
            if self.actual_returning_date > self.expected_returning_date:
                # Calculate fine amount based on days overdue
                days_overdue = (
                    self.actual_returning_date - self.expected_returning_date
                ).days
                fine_amount = (
                    days_overdue * self.book.daily_fee * 2
                )  # Assuming FINE_MULTIPLIER is 2

                # Create fine payment
                Payment.objects.create(
                    status=Payment.Status.PENDING,
                    type=Payment.Type.FINE,
                    borrowing_id=self.id,
                    session_url="",
                    session_id="",
                    money_to_pay=fine_amount,
                    user=self.user,
                )


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.get_type_display()} - {self.borrowing_id} - {self.status}"
        )
