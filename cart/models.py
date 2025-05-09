import uuid
from django.db import models

from django.contrib.auth.models import User
from product.models import Product
from django.utils import timezone
from datetime import timedelta


class Cart(models.Model):
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAIED = 'paied', 'Paied'
        INITIALIZED = 'initialized', 'Initialized'
        CANCELED = 'canceled', 'Canceled'
        
        
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart ({self.user.username})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"