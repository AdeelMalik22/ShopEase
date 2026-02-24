"""
Security utilities for the ecommerce application
"""
import re
import html
import logging
from functools import wraps
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings

security_logger = logging.getLogger('django.security')


def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return text
    # HTML escape
    text = html.escape(str(text))
    # Remove any script tags that might have been encoded
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    return text


def validate_image_file(file):
    """Validate uploaded image files"""
    if not file:
        return True

    # Check file extension
    ext = file.name.split('.')[-1].lower()
    allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
    if ext not in allowed_extensions:
        raise ValidationError(f'File extension "{ext}" is not allowed. Allowed: {", ".join(allowed_extensions)}')

    # Check file size
    max_size = getattr(settings, 'MAX_IMAGE_SIZE', 5 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(f'File size exceeds maximum allowed ({max_size // (1024*1024)} MB)')

    # Check MIME type
    import magic
    try:
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        allowed_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if mime not in allowed_mimes:
            raise ValidationError(f'Invalid file type: {mime}')
    except ImportError:
        # python-magic not installed, skip MIME check
        pass

    return True


def validate_order_number(order_number):
    """Validate order number format"""
    pattern = r'^ORD-[A-F0-9]{8}$'
    if not re.match(pattern, order_number):
        raise ValidationError('Invalid order number format')
    return True


def validate_phone_number(phone):
    """Validate phone number format"""
    if not phone:
        return True
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if it's a valid phone number (digits only, 10-15 chars)
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        raise ValidationError('Invalid phone number format')
    return True


def validate_postal_code(postal_code, country='US'):
    """Validate postal code format based on country"""
    if not postal_code:
        return True

    patterns = {
        'US': r'^\d{5}(-\d{4})?$',
        'UK': r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$',
        'CA': r'^[A-Z]\d[A-Z] ?\d[A-Z]\d$',
        'DEFAULT': r'^[\w\s-]{3,10}$',
    }

    pattern = patterns.get(country.upper(), patterns['DEFAULT'])
    if not re.match(pattern, postal_code.upper()):
        raise ValidationError(f'Invalid postal code format for {country}')
    return True


def log_security_event(event_type, message, request=None, user=None):
    """Log security-related events"""
    extra = {
        'event_type': event_type,
        'user': user or (request.user if request and request.user.is_authenticated else 'anonymous'),
        'ip': get_client_ip(request) if request else 'unknown',
    }
    security_logger.info(f'{event_type}: {message}', extra=extra)


def get_client_ip(request):
    """Get the client's IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def owner_required(model, pk_url_kwarg='pk', owner_field='user'):
    """
    Decorator to ensure the requesting user owns the object
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            pk = kwargs.get(pk_url_kwarg)
            obj = get_object_or_404(model, pk=pk)
            owner = getattr(obj, owner_field, None)

            if owner != request.user and not request.user.is_staff:
                log_security_event(
                    'UNAUTHORIZED_ACCESS',
                    f'User {request.user} attempted to access {model.__name__} {pk}',
                    request
                )
                return HttpResponseForbidden('You do not have permission to access this resource.')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


def simple_rate_limit(key_prefix, limit=5, period=60):
    """
    Simple rate limiting decorator using Django cache

    Args:
        key_prefix: Prefix for the cache key
        limit: Maximum number of requests
        period: Time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from django.core.cache import cache

            # Create a unique key based on IP
            ip = get_client_ip(request)
            cache_key = f'ratelimit:{key_prefix}:{ip}'

            # Get current count
            current = cache.get(cache_key, 0)

            if current >= limit:
                log_security_event(
                    'RATE_LIMIT_EXCEEDED',
                    f'Rate limit exceeded for {key_prefix}',
                    request
                )
                from django.http import HttpResponse
                return HttpResponse(
                    'Rate limit exceeded. Please try again later.',
                    status=429
                )

            # Increment counter
            cache.set(cache_key, current + 1, period)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

