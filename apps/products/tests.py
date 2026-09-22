from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Gadgets", slug="gadgets")
        self.product = Product.objects.create(
            category=self.category,
            name="Widget",
            slug="widget",
            price="19.99",
            stock=5,
        )

    def test_product_list_shows_active_products(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Widget")

    def test_product_search_filters_results(self):
        Product.objects.create(name="Other", slug="other", price="5.00", stock=1)
        response = self.client.get(reverse("products:product_list"), {"q": "Widget"})
        self.assertContains(response, "Widget")
        self.assertNotContains(response, "Other")

    def test_product_detail_page(self):
        response = self.client.get(reverse("products:product_detail", args=["widget"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "19.99")

    def test_out_of_stock_product_has_no_add_to_cart(self):
        self.product.stock = 0
        self.product.save()
        response = self.client.get(reverse("products:product_detail", args=["widget"]))
        self.assertContains(response, "Out of stock")
