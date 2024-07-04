from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.create_user_url = reverse(
            "users:create"
        )  # URL name 'create' from urlpatterns
        self.manage_user_url = reverse(
            "users:manage"
        )  # URL name 'manage' from urlpatterns
        self.token_obtain_url = reverse(
            "users:token_obtain_pair"
        )  # URL name 'token_obtain_pair' from urlpatterns
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )

    def test_create_user(self):
        # Test user creation
        response = self.client.post(self.create_user_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.count(), 2
        )  # One user already exists from setUp
        self.assertEqual(User.objects.last().email, "testuser@example.com")

    def test_create_user_without_email(self):
        # Test user creation without email
        response = self.client.post(
            self.create_user_url, {"password": "testpassword123"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manage_user_view(self):
        # Test user management view
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.manage_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

        # Test updating user information
        new_user_data = {"email": "updateduser@example.com"}
        response = self.client.patch(self.manage_user_url, new_user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "updateduser@example.com")

    def test_manage_user_view_unauthenticated(self):
        # Test manage user view without authentication
        response = self.client.get(self.manage_user_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_obtain(self):
        # Test obtaining a JWT token
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(self.token_obtain_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        # Test refreshing a JWT token
        refresh_token = self.client.post(
            self.token_obtain_url,
            {
                "email": "test@example.com",
                "password": "testpassword123",
            },
        ).data["refresh"]

        refresh_url = reverse("users:token_refresh")
        response = self.client.post(refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
