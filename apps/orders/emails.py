"""
Email utilities for sending order confirmations and notifications
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    try:
        subject = f'Order Confirmation - {order.order_number} | ShopEase'

        # Debug logging
        print(f"[EMAIL] Attempting to send order confirmation email")
        print(f"[EMAIL] Order: {order.order_number}")
        print(f"[EMAIL] Recipient: {order.email}")
        print(f"[EMAIL] From: {settings.DEFAULT_FROM_EMAIL}")

        # Render HTML email template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'site_name': 'ShopEase',
            'support_email': 'support@shopease.com',
        })

        # Create plain text version
        text_content = strip_tags(html_content)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send(fail_silently=False)

        print(f"[EMAIL] ✓ Email sent successfully to {order.email}")
        logger.info(f'Order confirmation email sent for order {order.order_number} to {order.email}')
        return True

    except Exception as e:
        print(f"[EMAIL] ✗ Failed to send email: {e}")
        logger.error(f'Failed to send order confirmation email for {order.order_number}: {e}')
        return False


def send_order_shipped_email(order, tracking_number=None):
    """
    Send shipping notification email to customer
    """
    try:
        subject = f'Your Order Has Shipped - {order.order_number} | ShopEase'

        html_content = render_to_string('emails/order_shipped.html', {
            'order': order,
            'tracking_number': tracking_number,
            'site_name': 'ShopEase',
        })

        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f'Shipping notification email sent for order {order.order_number}')
        return True

    except Exception as e:
        logger.error(f'Failed to send shipping email for {order.order_number}: {e}')
        return False


def send_payment_failed_email(order, error_message=None):
    """
    Send payment failed notification email to customer
    """
    try:
        subject = f'Payment Issue - {order.order_number} | ShopEase'

        html_content = render_to_string('emails/payment_failed.html', {
            'order': order,
            'error_message': error_message,
            'site_name': 'ShopEase',
            'support_email': 'support@shopease.com',
        })

        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f'Payment failed email sent for order {order.order_number}')
        return True

    except Exception as e:
        logger.error(f'Failed to send payment failed email for {order.order_number}: {e}')
        return False

