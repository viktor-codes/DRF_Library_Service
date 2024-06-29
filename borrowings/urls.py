from django.urls import path
from .views import (
    BorrowingListView,
    BorrowingDetailView,
    BorrowingCreateView,
    return_borrowing,

)


urlpatterns = [
    path("",
         BorrowingListView.as_view(), name="borrowing-list"),
    path("create/",
         BorrowingCreateView.as_view(), name="borrowing-create"),
    path("<int:pk>/",
         BorrowingDetailView.as_view(), name="borrowing-detail"),
    path('<int:pk>/return/',
         return_borrowing, name='borrowing-return'),
]
