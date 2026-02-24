import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Order(models.Model):
    """Order model"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, editable=False)

    # Contact info
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    # Shipping address
    shipping_first_name = models.CharField(max_length=100)
    shipping_last_name = models.CharField(max_length=100)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='United States')

    # Billing address
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_first_name = models.CharField(max_length=100, blank=True)
    billing_last_name = models.CharField(max_length=100, blank=True)
    billing_address1 = models.CharField(max_length=255, blank=True)
    billing_address2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)

    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status and payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate a unique order number"""
        return f'ORD-{uuid.uuid4().hex[:8].upper()}'

    @property
    def shipping_full_name(self):
        return f'{self.shipping_first_name} {self.shipping_last_name}'

    @property
    def billing_full_name(self):
        if self.billing_same_as_shipping:
            return self.shipping_full_name
        return f'{self.billing_first_name} {self.billing_last_name}'

    def get_shipping_address(self):
        """Get formatted shipping address"""
        address_parts = [
            self.shipping_address1,
            self.shipping_address2 if self.shipping_address2 else None,
            f'{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}',
            self.shipping_country
        ]
        return '\n'.join(filter(None, address_parts))


class OrderItem(models.Model):
    """Order item model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity}x {self.product_name}'

    def save(self, *args, **kwargs):
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)

