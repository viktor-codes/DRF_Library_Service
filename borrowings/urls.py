from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BorrowingViewSet, PaymentViewSet

router = DefaultRouter()

router.register(r"borrowings", BorrowingViewSet, basename="borrowings")
router.register(r"payments", PaymentViewSet, basename="payments")

app_name = "borrowings"

urlpatterns = [
    path("", include(router.urls)),
]
