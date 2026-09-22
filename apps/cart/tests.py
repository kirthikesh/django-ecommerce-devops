from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Widget", slug="widget", price="10.00", stock=5)

    def test_add_to_cart(self):
        self.client.post(reverse("cart:cart_add", args=[self.product.id]), {"quantity": 2})
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "Widget")
        self.assertContains(response, "20.00")

    def test_remove_from_cart(self):
        self.client.post(reverse("cart:cart_add", args=[self.product.id]), {"quantity": 1})
        self.client.get(reverse("cart:cart_remove", args=[self.product.id]))
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "empty")
