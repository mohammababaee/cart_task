
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from cart.models import Cart, CartItem
from product.models import Product, ProductInventory
from cart.serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer
)
from cart.services import CartService


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = CartService.get_or_create_active_cart(request.user)
        cart_item = CartService.add_item_to_cart(
            cart=cart,
            product_id=serializer.validated_data['product_id'],
            quantity=serializer.validated_data['quantity']
        )

        return Response({
            "message": "Item added to cart successfully",
            "cart_id": cart.id,
            "item": CartItemSerializer(cart_item).data
        }, status=status.HTTP_201_CREATED)


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get(self, request, cart_id):
        cart = CartService.get_cart_by_id(cart_id)
        if not cart:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if cart.user != request.user:
            return Response(
                {"error": "You don't have permission to view this cart"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.serializer_class(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

        