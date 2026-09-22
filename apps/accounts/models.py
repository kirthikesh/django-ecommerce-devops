from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model so we can extend it later without a costly migration."""

    phone_number = models.CharField(max_length=30, blank=True)
    shipping_address = models.TextField(blank=True)

    def __str__(self):
        return self.get_username()
