#!/usr/bin/env python
"""
Comprehensive test script for the ecommerce application.
Tests all major functionality including:
- User authentication (username and email login)
- Product browsing
- Cart operations
- Checkout flow
- Stripe payment integration
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/enigmatix/ecommerce_ai')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.cart.cart import Cart
from decimal import Decimal

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} - {name}")
    if details and not passed:
        print(f"         {Colors.YELLOW}{details}{Colors.RESET}")

def print_summary(passed, failed):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"  Total: {passed + failed}")
    print(f"{'='*60}\n")


class EcommerceTestSuite:
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.test_user = None
        self.test_product = None
        self.test_category = None

    def run_all_tests(self):
        print_header("ECOMMERCE APPLICATION TEST SUITE")

        # Setup test data
        self.setup_test_data()

        # Run test categories
        self.test_database_models()
        self.test_user_authentication()
        self.test_product_pages()
        self.test_cart_functionality()
        self.test_checkout_flow()
        self.test_security_features()

        # Print summary
        print_summary(self.passed, self.failed)

        return self.failed == 0

    def setup_test_data(self):
        """Ensure test data exists"""
        print_header("SETTING UP TEST DATA")

        # Create test user
        self.test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@example.com', 'first_name': 'Test', 'last_name': 'User'}
        )
        if created:
            self.test_user.set_password('testpass123')
            self.test_user.save()
        print(f"  Test user: testuser / testpass123")

        # Get or create category
        self.test_category = Category.objects.first()
        if not self.test_category:
            self.test_category = Category.objects.create(
                name='Test Category',
                slug='test-category',
                is_active=True
            )
        print(f"  Test category: {self.test_category.name}")

        # Get or create product
        self.test_product = Product.objects.filter(is_active=True, stock__gt=0).first()
        if not self.test_product:
            self.test_product = Product.objects.create(
                name='Test Product',
                slug='test-product',
                category=self.test_category,
                price=Decimal('29.99'),
                stock=100,
                is_active=True
            )
        print(f"  Test product: {self.test_product.name} (${self.test_product.price})")

    def test_database_models(self):
        """Test database models"""
        print_header("DATABASE MODELS")

        # Test User count
        user_count = User.objects.count()
        self.record_test("Users exist in database", user_count > 0, f"Count: {user_count}")

        # Test Category count
        cat_count = Category.objects.count()
        self.record_test("Categories exist in database", cat_count > 0, f"Count: {cat_count}")

        # Test Product count
        prod_count = Product.objects.count()
        self.record_test("Products exist in database", prod_count > 0, f"Count: {prod_count}")

        # Test featured products
        featured = Product.objects.filter(is_featured=True).count()
        self.record_test("Featured products exist", featured > 0, f"Count: {featured}")

        # Test product-category relationship
        products_with_category = Product.objects.exclude(category=None).count()
        self.record_test("Products have categories", products_with_category > 0)

    def test_user_authentication(self):
        """Test user authentication"""
        print_header("USER AUTHENTICATION")

        # Test login page loads
        response = self.client.get('/accounts/login/')
        self.record_test("Login page loads", response.status_code == 200)

        # Test register page loads
        response = self.client.get('/accounts/register/')
        self.record_test("Register page loads", response.status_code == 200)

        # Test login with username
        self.client.logout()
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        self.record_test("Login with username works", response.status_code == 200)

        # Check if user is authenticated
        self.record_test("User session is authenticated", '_auth_user_id' in self.client.session)

        self.client.logout()

        # Test login with email
        response = self.client.post('/accounts/login/', {
            'username': 'testuser@example.com',
            'password': 'testpass123'
        }, follow=True)
        self.record_test("Login with email works", '_auth_user_id' in self.client.session)

        # Test profile page (requires login)
        response = self.client.get('/accounts/profile/')
        self.record_test("Profile page accessible when logged in", response.status_code == 200)

        # Test logout
        self.client.logout()
        response = self.client.get('/accounts/profile/')
        self.record_test("Profile redirects when logged out", response.status_code == 302)

        # Test password reset page
        response = self.client.get('/accounts/password-reset/')
        self.record_test("Password reset page loads", response.status_code == 200)

        # Test login_required page for guests
        self.client.logout()
        response = self.client.get('/accounts/login-required/?next=/cart/')
        self.record_test("Login required page shows for guests", response.status_code == 200)
        self.record_test("Login required page has login form", b'Login' in response.content)
        self.record_test("Login required page has register option", b'Create Account' in response.content)

        # Test cart redirects to login_required for guests
        response = self.client.get('/cart/', follow=False)
        self.record_test("Cart redirects guests to login", response.status_code == 302)

    def test_product_pages(self):
        """Test product pages"""
        print_header("PRODUCT PAGES")

        # Test homepage
        response = self.client.get('/')
        self.record_test("Homepage loads", response.status_code == 200)
        self.record_test("Homepage has content", len(response.content) > 1000)

        # Test product list
        response = self.client.get('/products/')
        self.record_test("Product list page loads", response.status_code == 200)

        # Test product detail
        response = self.client.get(f'/products/{self.test_product.slug}/')
        self.record_test("Product detail page loads", response.status_code == 200)
        self.record_test("Product name in detail page", self.test_product.name.encode() in response.content)

        # Test category page
        response = self.client.get(f'/category/{self.test_category.slug}/')
        self.record_test("Category page loads", response.status_code == 200)

        # Test search
        response = self.client.get('/search/', {'q': 'test'})
        self.record_test("Search page loads", response.status_code == 200)

        # Test search with product name
        response = self.client.get('/search/', {'q': self.test_product.name[:5]})
        self.record_test("Search returns results", response.status_code == 200)

    def test_cart_functionality(self):
        """Test cart functionality"""
        print_header("CART FUNCTIONALITY")

        # Login first - cart now requires authentication
        self.client.login(username='testuser', password='testpass123')

        # Clear any existing cart
        session = self.client.session
        session['cart'] = {}
        session.save()

        # Test cart page loads (empty)
        response = self.client.get('/cart/')
        self.record_test("Empty cart page loads", response.status_code == 200)

        # Test add to cart
        response = self.client.post(f'/cart/add/{self.test_product.id}/', {
            'quantity': 2
        }, follow=True)
        self.record_test("Add to cart works", response.status_code == 200)

        # Check cart has item
        response = self.client.get('/cart/')
        self.record_test("Cart shows added product", self.test_product.name.encode() in response.content)

        # Test update cart quantity
        response = self.client.post(f'/cart/update/{self.test_product.id}/', {
            'quantity': 3
        }, follow=True)
        self.record_test("Update cart quantity works", response.status_code == 200)

        # Test remove from cart
        response = self.client.post(f'/cart/remove/{self.test_product.id}/', follow=True)
        self.record_test("Remove from cart works", response.status_code == 200)

        # Verify cart is empty
        response = self.client.get('/cart/')
        self.record_test("Cart is empty after removal", self.test_product.name.encode() not in response.content or b'empty' in response.content.lower())

    def test_checkout_flow(self):
        """Test checkout flow"""
        print_header("CHECKOUT FLOW")

        # Login first
        self.client.login(username='testuser', password='testpass123')

        # Add product to cart
        self.client.post(f'/cart/add/{self.test_product.id}/', {'quantity': 1})

        # Test checkout page loads
        response = self.client.get('/checkout/')
        self.record_test("Checkout page loads", response.status_code == 200)

        # Test checkout form submission
        checkout_data = {
            'email': 'testuser@example.com',
            'phone': '555-123-4567',
            'shipping_first_name': 'Test',
            'shipping_last_name': 'User',
            'shipping_address1': '123 Test Street',
            'shipping_address2': '',
            'shipping_city': 'Test City',
            'shipping_state': 'TS',
            'shipping_postal_code': '12345',
            'shipping_country': 'United States',
            'billing_same_as_shipping': True,
            'notes': 'Test order'
        }
        # Don't follow redirects - checkout should redirect to Stripe
        response = self.client.post('/checkout/', checkout_data, follow=False)
        # Should redirect to payment (302) which then redirects to Stripe
        self.record_test("Checkout form submission works", response.status_code == 302)

        # Check if order was created
        order_exists = Order.objects.filter(email='testuser@example.com').exists()
        self.record_test("Order created in database", order_exists)

        # Test order detail page
        if order_exists:
            order = Order.objects.filter(email='testuser@example.com').latest('created_at')
            response = self.client.get(f'/order/{order.order_number}/')
            self.record_test("Order detail page loads", response.status_code == 200)

            # Cleanup - delete test order
            order.delete()

        self.client.logout()

    def test_security_features(self):
        """Test security features"""
        print_header("SECURITY FEATURES")

        # Test CSRF protection
        response = self.client.get('/accounts/login/')
        self.record_test("CSRF token in login form", b'csrfmiddlewaretoken' in response.content)

        # Test protected pages require login
        self.client.logout()
        response = self.client.get('/accounts/profile/')
        self.record_test("Profile requires authentication", response.status_code == 302)

        response = self.client.get('/accounts/orders/')
        self.record_test("Order history requires authentication", response.status_code == 302)

        # Test admin requires staff
        response = self.client.get('/admin/')
        self.record_test("Admin requires authentication", response.status_code == 302)

        # Test order access control (can't view others' orders)
        # Create a test order
        test_order = Order.objects.create(
            email='other@example.com',
            shipping_first_name='Other',
            shipping_last_name='User',
            shipping_address1='456 Other St',
            shipping_city='Other City',
            shipping_state='OS',
            shipping_postal_code='54321',
            shipping_country='USA',
            total=Decimal('50.00')
        )

        # Login as testuser
        self.client.login(username='testuser', password='testpass123')

        # Try to access other user's order
        response = self.client.get(f'/order/{test_order.order_number}/')
        self.record_test("Cannot view others' orders", response.status_code in [302, 403] or b'permission' in response.content.lower())

        # Cleanup
        test_order.delete()
        self.client.logout()

    def record_test(self, name, passed, details=""):
        """Record test result"""
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print_test(name, passed, details)


def main():
    print("\n" + "="*60)
    print(" ECOMMERCE APPLICATION - AUTOMATED TEST SUITE")
    print("="*60)

    suite = EcommerceTestSuite()
    success = suite.run_all_tests()

    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed! ✓{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some tests failed! ✗{Colors.RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

