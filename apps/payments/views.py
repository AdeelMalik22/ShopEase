import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from apps.orders.models import Order
from apps.cart.cart import Cart


@login_required
def create_checkout_session(request):
    """Create a Stripe Checkout Session - requires login"""
    # Configure Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'No order found. Please try again.')
        return redirect('cart:cart_detail')

    order = get_object_or_404(Order, id=order_id)

    # Build line items for Stripe
    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product_name,
                },
                'unit_amount': int(item.product_price * 100),  # Stripe expects cents
            },
            'quantity': item.quantity,
        })

    # Add shipping cost if any
    if order.shipping_cost > 0:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Shipping',
                },
                'unit_amount': int(order.shipping_cost * 100),
            },
            'quantity': 1,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payments:success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payments:cancel')),
            customer_email=order.email,
            metadata={
                'order_id': order.id,
                'order_number': order.order_number,
            }
        )

        # Save checkout session ID to order
        order.stripe_checkout_session_id = checkout_session.id
        order.save()

        return redirect(checkout_session.url)

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('cart:cart_detail')


@login_required
def payment_success(request):
    """Handle successful payment - requires login"""
    # Configure Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session_id = request.GET.get('session_id')
    print(f"[PAYMENT] Payment success called with session_id: {session_id}")

    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            print(f"[PAYMENT] Stripe session retrieved: {session.id}")

            order = Order.objects.get(stripe_checkout_session_id=session_id)
            print(f"[PAYMENT] Order found: {order.order_number}, Email: {order.email}")

            # Update order status
            order.status = 'processing'
            order.stripe_payment_intent = session.payment_intent
            order.save()
            print(f"[PAYMENT] Order status updated to: {order.status}")

            # Reduce stock for each item
            for item in order.items.all():
                if item.product:
                    item.product.stock -= item.quantity
                    item.product.save()

            # Clear the cart
            cart = Cart(request)
            cart.clear()

            # Clear order_id from session
            if 'order_id' in request.session:
                del request.session['order_id']

            # Send order confirmation email
            print(f"[PAYMENT] Sending confirmation email to: {order.email}")
            from apps.payments.tasks import send_order_confirmation_email_task

            send_order_confirmation_email_task.delay(order.id)

            return render(request, 'payments/success.html', {'order': order})

        except (stripe.error.StripeError, Order.DoesNotExist) as e:
            print(f"[PAYMENT] Error: {e}")
            pass

    messages.error(request, 'There was an issue with your payment. Please contact support.')
    return redirect('products:home')


def payment_cancel(request):
    """Handle cancelled payment"""
    order_id = request.session.get('order_id')

    if order_id:
        # Optionally delete the pending order or keep it
        try:
            order = Order.objects.get(id=order_id)
            # You can choose to delete or keep the order
            # order.delete()  # Uncomment to delete cancelled orders
        except Order.DoesNotExist:
            pass

    messages.warning(request, 'Payment was cancelled. Your cart items are still available.')
    return render(request, 'payments/cancel.html')

