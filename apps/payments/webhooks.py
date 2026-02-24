import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.orders.models import Order
from apps.cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Retrieve the order
        try:
            order = Order.objects.get(stripe_checkout_session_id=session['id'])

            # Update order status
            order.status = 'processing'
            order.stripe_payment_intent = session.get('payment_intent', '')
            order.save()

            # Reduce stock for each item
            for item in order.items.all():
                if item.product:
                    item.product.stock -= item.quantity
                    if item.product.stock < 0:
                        item.product.stock = 0
                    item.product.save()

        except Order.DoesNotExist:
            return HttpResponse(status=404)

    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']

        # Optionally handle expired sessions
        try:
            order = Order.objects.get(stripe_checkout_session_id=session['id'])
            order.status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)

