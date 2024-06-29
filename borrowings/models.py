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
                check=Q(borrowing_date__lte=F('expected_returning_date')),
                name='borrow_date_before_or_equal_expected'
            ),
            CheckConstraint(
                check=Q(actual_returning_date__gte=F('borrowing_date')),
                name='actual_return_date_after_borrow_date'
            )
        ]

    def __str__(self):
        return f"{self.user} borrowed {self.book}"
