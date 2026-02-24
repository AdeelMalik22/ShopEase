#!/usr/bin/env python
"""Test email sending functionality"""
import os
import sys

# Setup Django
sys.path.insert(0, '/home/enigmatix/ecommerce_ai')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.orders.emails import send_order_confirmation_email
from decimal import Decimal

print("=" * 60)
print("TESTING ORDER CONFIRMATION EMAIL")
print("=" * 60)

# Get a product
product = Product.objects.first()
print(f"Using product: {product.name}")

# Create test order
order = Order.objects.create(
    email='customer@example.com',
    shipping_first_name='John',
    shipping_last_name='Doe',
    shipping_address1='123 Test Street',
    shipping_city='New York',
    shipping_state='NY',
    shipping_postal_code='10001',
    shipping_country='USA',
    subtotal=Decimal('49.99'),
    total=Decimal('49.99')
)
print(f"Created order: {order.order_number}")

# Add order item
OrderItem.objects.create(
    order=order,
    product=product,
    product_name=product.name,
    product_price=product.price,
    quantity=2,
    subtotal=product.price * 2
)
print(f"Added item: {product.name} x 2")

print(f"\nSending email to: {order.email}")
print("-" * 60)

# Send email (will print to console with console backend)
result = send_order_confirmation_email(order)

print("-" * 60)
print(f"Email sent successfully: {result}")

# Cleanup
order.delete()
print("\nTest order cleaned up.")
print("=" * 60)

