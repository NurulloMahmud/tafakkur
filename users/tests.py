from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.core.management import call_command
from .documents import UserDocument

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def create_user(self, email="user@example.com", password="StrongPass123!", **extra):
        user = User.objects.create_user(email=email, password=password, **extra)
        return user, password

    def test_register_creates_user_and_returns_minimal_profile(self):
        payload = {
            "email": "abdulloh@example.com",
            "password": "StrongPass123!",
            "first_name": "Abdulloh",
            "last_name": "Mahmud",
        }
        res = self.client.post("/users/auth/register/", payload, format="json")
        self.assertEqual(res.status_code, 201, msg=res.data)
        data = res.json()
        self.assertIn("id", data)
        self.assertTrue(data["id"])
        self.assertEqual(data["email"], payload["email"])
        self.assertEqual(data["first_name"], "Abdulloh")
        self.assertEqual(data["last_name"], "Mahmud")
        self.assertNotIn("password", data)

        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_register_requires_unique_email(self):
        self.create_user(email="taken@example.com")
        res = self.client.post(
            "/users/auth/register/",
            {"email": "taken@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)

    def test_login_returns_tokens_and_user_fields(self):
        user, password = self.create_user(
            email="login@example.com", is_staff=False, is_superuser=False
        )
        res = self.client.post(
            "/users/auth/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        self.assertEqual(res.status_code, 200, msg=res.data)
        data = res.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["id"], str(user.id))
        self.assertEqual(data["user"]["email"], user.email)
        self.assertFalse(data["user"]["is_superuser"])
        self.assertFalse(data["user"]["is_staff"])

    def test_login_with_wrong_password_fails(self):
        self.create_user(email="badlogin@example.com", password="CorrectPass123!")
        res = self.client.post(
            "/users/auth/login/",
            {"email": "badlogin@example.com", "password": "WrongPass123!"},
            format="json",
        )
        self.assertEqual(res.status_code, 401)

    def test_token_refresh_returns_new_access(self):
        user, password = self.create_user(email="refresh@example.com")
        login = self.client.post(
            "/users/auth/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        self.assertEqual(login.status_code, 200, msg=login.data)
        refresh = login.json()["refresh"]

        res = self.client.post("/users/auth/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(res.status_code, 200, msg=res.data)
        data = res.json()
        self.assertIn("access", data)

    def test_me_requires_auth_and_returns_user_info(self):
        user, password = self.create_user(email="me@example.com", is_staff=True)

        # Unauthenticated
        res = self.client.get("/users/auth/me/")
        self.assertEqual(res.status_code, 401)

        # Authenticate via login
        login = self.client.post(
            "/users/auth/login/", {"email": user.email, "password": password}, format="json"
        )
        self.assertEqual(login.status_code, 200, msg=login.data)
        token = login.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        res = self.client.get("/users/auth/me/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], str(user.id))
        self.assertEqual(data["email"], user.email)
        self.assertTrue(data["is_staff"])
        self.assertIn("first_name", data)
        self.assertIn("last_name", data)
