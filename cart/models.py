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
        
        
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_expired = models.BooleanField(default=False)
    
    def expire_if_needed(self):
        if timezone.now() - self.created_at > timedelta(minutes=30):
            self.is_expired = True
            for item in self.items.all():
                item.product.inventory += item.quantity
                item.product.save()
            self.save()

    def __str__(self):
        return f"Cart ({self.user.username})"

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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