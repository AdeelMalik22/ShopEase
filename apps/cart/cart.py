from decimal import Decimal
from django.conf import settings
from apps.products.models import Product
import copy


class Cart:
    """Session-based shopping cart"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Ensure existing cart data is JSON serializable
        self._sanitize_cart()

    def _sanitize_cart(self):
        """Ensure all cart data is JSON serializable"""
        for product_id in list(self.cart.keys()):
            item = self.cart[product_id]
            # Convert price to string if it's not
            if 'price' in item:
                item['price'] = str(item['price'])
            # Convert quantity to int
            if 'quantity' in item:
                item['quantity'] = int(item['quantity'])

    def add(self, product, quantity=1, update_quantity=False):
        """Add a product to the cart or update its quantity"""
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)  # Store as string for JSON serialization
            }

        if update_quantity:
            self.cart[product_id]['quantity'] = int(quantity)
        else:
            self.cart[product_id]['quantity'] = int(self.cart[product_id]['quantity']) + int(quantity)

        # Ensure price is always a string
        self.cart[product_id]['price'] = str(self.cart[product_id]['price'])

        self.save()

    def remove(self, product):
        """Remove a product from the cart"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Mark the session as modified to save changes"""
        self._sanitize_cart()
        self.session.modified = True

    def clear(self):
        """Remove cart from session"""
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def __iter__(self):
        """Iterate over the items in the cart and get products from the database"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        # Create a deep copy so we don't modify session data
        cart_copy = copy.deepcopy(self.cart)

        for product in products:
            cart_copy[str(product.id)]['product'] = product

        for item in cart_copy.values():
            item['price'] = Decimal(str(item['price']))
            item['total_price'] = item['price'] * int(item['quantity'])
            yield item

    def __len__(self):
        """Count all items in the cart"""
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_total_price(self):
        """Calculate the total price of all items in the cart"""
        return sum(
            Decimal(str(item['price'])) * int(item['quantity'])
            for item in self.cart.values()
        )

    def get_item_count(self):
        """Get total number of items"""
        return len(self)

