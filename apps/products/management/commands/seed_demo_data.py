from django.core.management.base import BaseCommand

from apps.products.models import Category, Product


class Command(BaseCommand):
    help = "Seed a handful of demo categories/products so the storefront isn't empty."

    def handle(self, *args, **options):
        categories = {
            "keyboards": "Keyboards",
            "monitors": "Monitors",
            "accessories": "Accessories",
        }
        cat_objs = {}
        for slug, name in categories.items():
            cat_objs[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})

        products = [
            ("Mechanical Keyboard", "mechanical-keyboard", "keyboards", "89.99", 12,
             "A tactile 75% mechanical keyboard with hot-swappable switches."),
            ("Wireless Keyboard", "wireless-keyboard", "keyboards", "49.99", 20,
             "Slim wireless keyboard with a 6-month battery life."),
            ("27-inch 4K Monitor", "27-inch-4k-monitor", "monitors", "329.00", 8,
             "27-inch IPS panel, 4K resolution, USB-C with 90W power delivery."),
            ("Ultrawide Monitor", "ultrawide-monitor", "monitors", "459.00", 4,
             "34-inch curved ultrawide for coding and multitasking."),
            ("USB-C Hub", "usb-c-hub", "accessories", "34.99", 30,
             "7-in-1 USB-C hub with HDMI, SD card reader, and 100W passthrough."),
            ("Laptop Stand", "laptop-stand", "accessories", "24.50", 0,
             "Aluminium adjustable laptop stand — currently out of stock."),
        ]
        for name, slug, cat_slug, price, stock, desc in products:
            Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": cat_objs[cat_slug],
                    "price": price,
                    "stock": stock,
                    "description": desc,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {Product.objects.count()} products."))
