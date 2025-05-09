from datetime import timezone
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart, CartItem
from product.models import Product, ProductInventory


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id or quantity <= 0:
            return Response({"error": "داده اشتباه است"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
            product_inventory = ProductInventory.objects.get(product=product)
        except (Product.DoesNotExist, ProductInventory.DoesNotExist):
            return Response({"error": "محصول یافت نشد"}, status=404)

        if product_inventory.quantity_available < quantity:
            return Response({"error": "تعداد مورد نظر موجود نیست"}, status=400)

        user = request.user
        cart, created = Cart.objects.get_or_create(
            user=user,
            status=Cart.Status.ACTIVE,
            is_expired=False
        )

        # Check if product already exists in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not item_created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
            product_inventory.quantity_available -= quantity
            product_inventory.save()

        return Response({
            "message": "آیتم به سبد اضافه شد",
            "cart_id": cart.id,
            "item": {
                "product_id": product.id,
                "product_name": product.name,
                "quantity": cart_item.quantity,
                "price": float(product.price)
            }
        }, status=201)