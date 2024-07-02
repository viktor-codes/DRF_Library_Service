from django.urls import path
from .views import (
    BorrowingListView,
    BorrowingDetailView,
    BorrowingCreateView,
    return_borrowing,
    PaymentListCreateView,
    PaymentDetailView,
    payment_success,
    payment_cancel,
)


urlpatterns = [
    path("", BorrowingListView.as_view(), name="borrowing-list"),
    path("create/", BorrowingCreateView.as_view(), name="borrowing-create"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return/", return_borrowing, name="borrowing-return"),
    path("payments/", PaymentListCreateView.as_view(), name="payment-list"),
    path(
        "payments/<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),
    path("payment/success/", payment_success, name="payment-success"),
    path("payment/cancel/", payment_cancel, name="payment-cancel"),
]
