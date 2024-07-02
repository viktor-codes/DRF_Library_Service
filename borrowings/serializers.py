from rest_framework import serializers
from .models import Borrowing, Payment
from books.serializers import BookSerializer


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payments = PaymentSerializer(
        many=True, read_only=True, source="payment_set"
    )

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "user",
            "borrowing_date",
            "expected_returning_date",
            "actual_returning_date",
            "payments",
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
