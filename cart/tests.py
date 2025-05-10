from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from cart.services import CartService
from cart.models import Cart, CartItem
from product.models import Product, ProductInventory, Category


class CartServiceTests(TestCase):
    def setUp(self):
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            priority=1
        )
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category
        )
        
        # Create product inventory
        self.product_inventory = ProductInventory.objects.create(
            product=self.product,
            quantity_available=10
        )

    def test_get_or_create_active_cart(self):
        # Test creating a new cart
        cart, created = CartService.get_or_create_active_cart(self.user)
        self.assertTrue(created)
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.status, Cart.Status.ACTIVE)
        self.assertFalse(cart.is_expired)

        # Test getting existing cart
        cart2, created = CartService.get_or_create_active_cart(self.user)
        self.assertFalse(created)
        self.assertEqual(cart.id, cart2.id)

    def test_get_cart_by_id(self):
        # Create a cart
        cart, _ = CartService.get_or_create_active_cart(self.user)
        
        # Test getting existing cart
        retrieved_cart = CartService.get_cart_by_id(cart.id)
        self.assertEqual(retrieved_cart, cart)
        
        # Test getting non-existent cart
        non_existent_cart = CartService.get_cart_by_id(99999)
        self.assertIsNone(non_existent_cart)

    def test_add_item_to_cart(self):
        cart, _ = CartService.get_or_create_active_cart(self.user)
        
        # Test adding item to cart
        cart_item = CartService.add_item_to_cart(cart, self.product.id, 2)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.product, self.product)
        
        # Verify inventory was updated
        self.product_inventory.refresh_from_db()
        self.assertEqual(self.product_inventory.quantity_available, 8)
        
        # Test adding more of the same item
        cart_item = CartService.add_item_to_cart(cart, self.product.id, 3)
        self.assertEqual(cart_item.quantity, 5)
        
        # Verify inventory was updated again
        self.product_inventory.refresh_from_db()
        self.assertEqual(self.product_inventory.quantity_available, 5)

    def test_add_item_to_expired_cart(self):
        cart, _ = CartService.get_or_create_active_cart(self.user)
        cart.is_expired = True
        cart.save()
        
        with self.assertRaises(ValueError):
            CartService.add_item_to_cart(cart, self.product.id, 1)

    def test_get_cart_items(self):
        cart, _ = CartService.get_or_create_active_cart(self.user)
        
        # Add items to cart
        CartService.add_item_to_cart(cart, self.product.id, 2)
        
        # Test getting cart items
        cart_items = CartService.get_cart_items(cart)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2)
        self.assertEqual(cart_items.first().product, self.product)
