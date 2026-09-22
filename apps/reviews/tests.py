from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product

User = get_user_model()


class ReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="pass12345")
        self.product = Product.objects.create(name="Widget", slug="widget", price="10.00", stock=5)

    def test_logged_in_user_can_review_once(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("products:product_detail", args=["widget"]),
            {"rating": 5, "comment": "Great!"},
        )
        self.assertEqual(self.product.reviews.count(), 1)

        # Second submission should not create a duplicate (form isn't shown again).
        self.client.post(
            reverse("products:product_detail", args=["widget"]),
            {"rating": 3, "comment": "Again"},
        )
        self.assertEqual(self.product.reviews.count(), 1)

    def test_average_rating(self):
        self.product.reviews.create(user=self.user, rating=4, comment="Good")
        self.assertEqual(self.product.average_rating, 4)
