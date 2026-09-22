from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product

User = get_user_model()


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        self.product = Product.objects.create(name="Widget", slug="widget", price="10.00", stock=5)
        self.client.force_login(self.user)
        self.client.post(reverse("cart:cart_add", args=[self.product.id]), {"quantity": 2})

    def test_successful_checkout_creates_paid_order(self):
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Test Buyer",
                "shipping_address": "1 Test Street",
                "card_number": "4242424242424242",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = self.user.orders.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, "paid")
        self.assertEqual(order.items.count(), 1)

    def test_declined_card_marks_order_failed(self):
        self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Test Buyer",
                "shipping_address": "1 Test Street",
                "card_number": "4242424242420000",
            },
        )
        order = self.user.orders.first()
        self.assertEqual(order.status, "failed")

    def test_checkout_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)
