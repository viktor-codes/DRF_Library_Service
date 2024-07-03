from django.test import TestCase
from django.db.utils import IntegrityError
from books.models import Book
from django.contrib.auth import get_user_model
from borrowings.models import Borrowing, Payment
from rest_framework.test import APIClient
from rest_framework import status


BORROWINGS_URL = "/api/borrowings/"
PAYMENTS_URL = "/api/payments/"


class BorrowingModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password="userpass", email="user@example.com"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author Name",
            cover=Book.HARD,
            inventory=10,
            daily_fee="2.50",
        )

    def test_borrowing_creation(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_returning_date="2024-07-10",
        )
        self.assertEqual(str(borrowing), f"{self.user} borrowed {self.book}")

    def test_invalid_borrowing_dates(self):
        with self.assertRaises(IntegrityError) as context:
            Borrowing.objects.create(
                book=self.book,
                user=self.user,
                borrowing_date="2024-07-10",
                expected_returning_date="2024-07-02",
            )
        self.assertIn(
            "borrow_date_before_or_equal_expected", str(context.exception)
        )

    def test_actual_return_date_check(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_returning_date="2024-07-10",
        )
        borrowing.actual_returning_date = "2024-07-02"
        with self.assertRaises(IntegrityError) as context:
            borrowing.save()
        self.assertIn(
            "actual_return_date_after_borrow_date", str(context.exception)
        )


class BorrowingViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            password="adminpass", email="admin@example.com"
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
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.regular_user,
            expected_returning_date="2024-07-10",
        )

    def test_list_borrowings_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_borrowings_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_borrowing(self):
        initial_inventory = self.book.inventory

        self.client.force_authenticate(user=self.regular_user)
        data = {"book": self.book.id, "expected_returning_date": "2024-07-20"}
        response = self.client.post(BORROWINGS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory - 1)

    def test_return_borrowing(self):
        initial_inventory = self.book.inventory

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f"{BORROWINGS_URL}{self.borrowing.id}/return/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_returning_date)
        self.assertEqual(self.book.inventory, initial_inventory + 1)


class PaymentViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            password="adminpass", email="admin@example.com"
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
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.regular_user,
            expected_returning_date="2024-07-10",
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_url="http://example.com/session",
            session_id="session_12345",
            money_to_pay="10.00",
            user=self.regular_user,
            type=Payment.Type.PAYMENT,
        )

    def test_list_payments_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_payments_as_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(PAYMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 1
        )  # Regular user can only see their own payments

    def test_payment_success(self):
        response = self.client.get(
            f"{PAYMENTS_URL}success/", {"session_id": "session_12345"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.PAID)

    def test_payment_cancel(self):
        response = self.client.get(
            f"{PAYMENTS_URL}cancel/", {"session_id": "session_12345"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.PENDING)
