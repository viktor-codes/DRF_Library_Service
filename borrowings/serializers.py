from rest_framework import serializers
from .models import Borrowing
from books.serializers import BookSerializer


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "user",
            "borrowing_date",
            "expected_returning_date",
            "actual_returning_date",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["book", "borrowing_date", "expected_returning_date"]

    def validate(self, data):
        book = data.get("book")
        if book.inventory <= 0:
            raise serializers.ValidationError("This book is out of stock.")
        return data

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(**validated_data)
        borrowing.user = self.context["request"].user
        borrowing.save()

        return borrowing
