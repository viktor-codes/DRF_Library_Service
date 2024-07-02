from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BorrowingViewSet,
    PaymentListCreateView,
    PaymentDetailView,
    payment_success,
    payment_cancel,
)

router = DefaultRouter()
router.register(r"borrowings", BorrowingViewSet, basename="borrowings")

app_name = "borrowings"

urlpatterns = [
    path("", include(router.urls)),
    path("payments/", PaymentListCreateView.as_view(), name="payment-list"),
    path(
        "payments/<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),
    path("success/", payment_success, name="payment-success"),
    path("cancel/", payment_cancel, name="payment-cancel"),
]
