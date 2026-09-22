from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountTests(TestCase):
    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "SuperSecret123",
                "password2": "SuperSecret123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_view_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
