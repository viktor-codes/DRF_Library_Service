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
