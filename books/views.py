from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAdminUser()]
        elif self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()
