from rest_framework import serializers
from .models import Borrowing
from books.serializers import BookSerializer


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = ['id', 'book', 'user', 'borrowing_date',
                  'expected_returning_date', 'actual_returning_date']
