from django.utils import timezone
from django.conf import settings
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import action
from helpers.stripe_helper import create_payment_session
from helpers.telegram_helper import send_message

from .models import Borrowing, Payment

from .serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    PaymentSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowingReadSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        borrowing.book.save()

        create_payment_session(borrowing, self.request)

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        user_id = self.request.query_params.get("user_id")
        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_returning_date__isnull=is_active)

        return queryset

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_returning_date:
            return Response(
                {"detail": "Borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_returning_date = timezone.now().date()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()

        fine_amount = 0

        if borrowing.actual_returning_date > borrowing.expected_returning_date:
            days_overdue = (
                borrowing.actual_returning_date
                - borrowing.expected_returning_date
            ).days
            fine_amount = (
                days_overdue
                * borrowing.book.daily_fee
                * settings.FINE_MULTIPLIER
            )

            if fine_amount > 0:
                create_payment_session(
                    borrowing,
                    request,
                    payment_type=Payment.Type.FINE,
                    fine_amount=fine_amount,
                )

        serializer = BorrowingReadSerializer(borrowing)
        return Response(serializer.data)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="success")
    def payment_success(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = Payment.Status.PAID
            payment.save()
            message = (
                f"Payment successful for borrowing"
                f" of book {payment.borrowing.book.title}"
            )
            send_message(message)
            return Response(message, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Invalid session ID"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["GET"], url_path="cancel")
    def payment_cancel(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Session ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = Payment.Status.PENDING
            payment.save()
            message = (
                "Payment has been cancelled. "
                "You can complete the payment within "
                "the next 24 hours using the same session link."
            )
            return Response(message, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Invalid session ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
