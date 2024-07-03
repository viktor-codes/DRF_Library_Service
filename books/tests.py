from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import TestCase
from books.models import Book
from django.urls import reverse

BOOKS_URL = reverse("books:book-list")


class BookModelTest(TestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Author Name",
            cover=Book.HARD,
            inventory=10,
            daily_fee="2.50",
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Author Name")
        self.assertEqual(self.book.cover, Book.HARD)
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(str(self.book.daily_fee), "2.50")

    def test_book_str(self):
        self.assertEqual(str(self.book), "Test Book")


class BookViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            password="adminpass", email="admin@example.com", is_staff=True
        )
        self.regular_user = get_user_model().objects.create_user(
            password="userpass", email="user@example.com"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author Name",
            cover=Book.HARD,
            inventory=10,
            daily_fee="2.50",
        )

    def test_list_books(self):
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        response = self.client.get(f"{BOOKS_URL}{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(self.admin_user)
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": Book.SOFT,
            "inventory": 5,
            "daily_fee": "1.50",
        }
        response = self.client.post(BOOKS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_book_as_non_admin(self):
        self.client.force_authenticate(self.regular_user)
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": Book.SOFT,
            "inventory": 5,
            "daily_fee": "1.50",
        }
        response = self.client.post(BOOKS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_as_admin(self):
        self.client.force_authenticate(self.admin_user)
        data = {
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": Book.SOFT,
            "inventory": 8,
            "daily_fee": "3.00",
        }
        response = self.client.put(
            f"{BOOKS_URL}{self.book.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_book_as_non_admin(self):
        self.client.force_authenticate(self.regular_user)
        data = {
            "title": "Updated Book",
            "author": "Updated Author",
            "cover": Book.SOFT,
            "inventory": 8,
            "daily_fee": "3.00",
        }
        response = self.client.put(
            f"{BOOKS_URL}{self.book.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_as_admin(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.delete(f"{BOOKS_URL}{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_book_as_non_admin(self):
        self.client.force_authenticate(self.regular_user)
        response = self.client.delete(f"{BOOKS_URL}{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
