from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.cart.cart import Cart
from apps.products.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm
from apps.core.security import log_security_event, sanitize_input


@login_required
def checkout(request):
    """Handle checkout process with validation - requires login"""
    cart = Cart(request)

    # Redirect to cart if empty
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty. Please add some products before checkout.')
        return redirect('cart:cart_detail')

    # Validate stock availability before checkout
    for item in cart:
        product = item['product']
        if item['quantity'] > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units of "{product.name}" are available.')
            return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)

            # Sanitize user inputs
            order.shipping_first_name = sanitize_input(form.cleaned_data['shipping_first_name'])
            order.shipping_last_name = sanitize_input(form.cleaned_data['shipping_last_name'])
            order.shipping_address1 = sanitize_input(form.cleaned_data['shipping_address1'])
            order.shipping_address2 = sanitize_input(form.cleaned_data.get('shipping_address2', ''))
            order.shipping_city = sanitize_input(form.cleaned_data['shipping_city'])
            order.notes = sanitize_input(form.cleaned_data.get('notes', ''))

            # Assign user if authenticated
            if request.user.is_authenticated:
                order.user = request.user

            # Calculate totals
            order.subtotal = cart.get_total_price()
            order.shipping_cost = 0  # Free shipping or calculate based on logic
            order.tax = order.subtotal * 0  # Add tax calculation if needed
            order.total = order.subtotal + order.shipping_cost + order.tax

            order.save()

            # Create order items and validate stock again (double-check)
            for item in cart:
                product = Product.objects.select_for_update().get(id=item['product'].id)
                if item['quantity'] > product.stock:
                    order.delete()
                    messages.error(request, f'Sorry, "{product.name}" is no longer available in the requested quantity.')
                    return redirect('cart:cart_detail')

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=item['price'],
                    quantity=item['quantity'],
                    subtotal=item['total_price']
                )

            # Store order ID in session for payment
            request.session['order_id'] = order.id

            log_security_event('ORDER_CREATED', f'Order {order.order_number} created', request)

            # Redirect to payment
            return redirect('payments:create_checkout_session')
    else:
        form = CheckoutForm(user=request.user)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


def order_detail(request, order_number):
    """Display order details with proper access control"""
    order = get_object_or_404(Order, order_number=order_number)

    # Access control: Check if user can view this order
    can_view = False

    if request.user.is_authenticated:
        # Staff can view any order
        if request.user.is_staff:
            can_view = True
        # Owner can view their own orders
        elif order.user and order.user == request.user:
            can_view = True

    # Guest orders: Allow if order was just created in this session
    if not order.user:
        session_order_id = request.session.get('order_id')
        last_order_number = request.session.get('last_order_number')
        if session_order_id == order.id or last_order_number == order.order_number:
            can_view = True

    if not can_view:
        log_security_event(
            'UNAUTHORIZED_ORDER_ACCESS',
            f'Attempted access to order {order_number}',
            request
        )
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('products:home')

    return render(request, 'orders/order_detail.html', {'order': order})

