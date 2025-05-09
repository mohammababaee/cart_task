from rest_framework import serializers
from cart.models import Cart, CartItem
from product.models import Product, ProductInventory
from django.utils.translation import gettext_lazy as _


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'category_name']
        read_only_fields = ['id']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def get_total_price(self, obj):
        return float(obj.product.price * obj.quantity)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_email', 'status', 'is_expired', 
            'created_at', 'items', 'total_items', 'total_price'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'created_at']
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    
    def get_total_price(self, obj):
        return sum(float(item.product.price * item.quantity) for item in obj.items.all())


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product_id = data['product_id']
        quantity = data['quantity']

        try:
            product = Product.objects.get(id=product_id)
            product_inventory = ProductInventory.objects.get(product=product)
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': _('Product with this ID does not exist.')
            })
        except ProductInventory.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': _('Product inventory not found.')
            })

        if product_inventory.quantity_available < quantity:
            raise serializers.ValidationError({
                'quantity': _('Requested quantity exceeds available stock. Available: %(available)s') % {
                    'available': product_inventory.quantity_available
                }
            })

        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        quantity = data['quantity']
        cart_item = self.context.get('cart_item')
        
        if not cart_item:
            raise serializers.ValidationError(_('Cart item not found.'))

        product_inventory = ProductInventory.objects.get(product=cart_item.product)
        
        if product_inventory.quantity_available < quantity:
            raise serializers.ValidationError({
                'quantity': _('Requested quantity exceeds available stock. Available: %(available)s') % {
                    'available': product_inventory.quantity_available
                }
            })

        return data 