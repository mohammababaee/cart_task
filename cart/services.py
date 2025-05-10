from django.db import transaction
from django.utils import timezone
from cart.models import Cart, CartItem
from product.models import Product, ProductInventory


class CartService:
    @staticmethod
    def get_or_create_active_cart(user):
        return Cart.objects.get_or_create(
            user=user,
            status=Cart.Status.ACTIVE,
            is_expired=False
        )

    @staticmethod
    def get_cart_by_id(cart_id):
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def add_item_to_cart(cart, product_id, quantity):
        # Check if cart is expired
        if cart.is_expired:
            raise ValueError("Cart has expired")

        product = Product.objects.get(id=product_id)
        product_inventory = ProductInventory.objects.get(product=product)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        product_inventory.quantity_available -= quantity
        product_inventory.save()

        # Update cart's created_at to reset the expiration timer
        cart.created_at = timezone.now()
        cart.save()

        return cart_item

    @staticmethod
    def get_cart_items(cart):
        return CartItem.objects.filter(cart=cart).select_related('product') 