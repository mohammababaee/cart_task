from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from cart.models import Cart, CartItem
from product.models import ProductInventory


@shared_task
def restore_cart_items_to_inventory():
    """
    Restore items from inactive carts back to inventory.
    A cart is considered inactive if it's been in ACTIVE status for more than 30 minutes.
    """
    # Get carts that have been active for more than 30 minutes
    inactive_threshold = timezone.now() - timedelta(minutes=30)
    inactive_carts = Cart.objects.filter(
        status=Cart.Status.ACTIVE,
        created_at__lt=inactive_threshold
    ).select_related('user').prefetch_related('items__product')

    for cart in inactive_carts:
        with transaction.atomic():
            # Get all items in the cart
            cart_items = cart.items.all()
            
            # Restore each item to inventory
            for item in cart_items:
                try:
                    inventory = ProductInventory.objects.get(product=item.product)
                    inventory.quantity_available += item.quantity
                    inventory.save()
                except ProductInventory.DoesNotExist:
                    continue

            # Mark cart as expired
            cart.is_expired = True
            cart.save()

    return f"Processed {inactive_carts.count()} inactive carts" 