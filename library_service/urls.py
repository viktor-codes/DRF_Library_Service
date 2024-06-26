from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/books/", include("books.urls")),
    path("api/borrowings/", include("borrowings.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/doc/swagger/",
         SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(
        "api/doc/redoc/",
        SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
