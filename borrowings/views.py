from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from .models import Borrowing
from .serializers import BorrowingReadSerializer, BorrowingCreateSerializer


class BorrowingListView(generics.ListAPIView):
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]

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


class BorrowingDetailView(generics.RetrieveAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReadSerializer
    permission_classes = [IsAuthenticated]


class BorrowingCreateView(generics.CreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["PATCH"])
def return_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)

    if request.method == "PATCH":
        # Check if borrowing has already been returned
        if borrowing.actual_returning_date:
            return Response(
                {"detail": "Borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Update the borrowing instance
        borrowing.actual_returning_date = timezone.now().date()
        borrowing.save()

        # Add 1 to book inventory
        borrowing.book.inventory += 1
        borrowing.book.save()

        # Serialize and return response
        serializer = BorrowingReadSerializer(borrowing)
        return Response(serializer.data)
