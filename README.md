# ShopEase Ecommerce

Modern Django-based ecommerce app with accounts, catalog, cart, checkout, Stripe payments, order management, and password reset.

## Features
- User auth with email/username login, profile, order history, and email-based password reset
- Product catalog with categories, search-ready templates, and media assets
- Shopping cart + session persistence, coupon-ready hooks
- Checkout with Stripe (card) and webhook handler placeholder
- Order management with confirmation emails (templates in `templates/emails/`)
- Dashboard landing page and Bootstrap 5 UI with Crispy Forms

## Project Structure
- `config/` – Django settings, urls, ASGI/WSGI
- `apps/accounts` – auth views, custom backend, password reset URLs/templates
- `apps/products`, `apps/cart`, `apps/orders`, `apps/payments`, `apps/dashboard` – core ecommerce flows
- `templates/` – site templates (includes accounts/password reset pages)
- `static/` / `media/` – static assets and uploaded product images

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` for the storefront and `http://127.0.0.1:8000/admin/` for admin.

## Environment Variables (.env)
- `SECRET_KEY` – Django secret
- `DEBUG` – `True`/`False`
- `ALLOWED_HOSTS` – comma list (e.g., `localhost,127.0.0.1`)
- `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- Email (used for password reset / order emails):
  - `EMAIL_BACKEND` (dev: `django.core.mail.backends.console.EmailBackend`)
  - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
  - `DEFAULT_FROM_EMAIL`

## Password Reset Flow
- URLs are namespaced under `accounts`:
  - `accounts:password_reset`
  - `accounts:password_reset_done`
  - `accounts:password_reset_confirm`
  - `accounts:password_reset_complete`
- Email templates: `templates/accounts/password_reset_email.html` and subject `templates/accounts/password_reset_subject.txt`.
- To test locally without SMTP, set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`.

## Stripe & Payments
- Frontend uses Stripe public key from env; backend uses secret key and webhook secret.
- For local webhook testing, use the Stripe CLI to forward events.

## Running Tests
```bash
python manage.py test
```
Adds coverage for the password reset flow in `apps/accounts/tests.py`.

## Troubleshooting
- Git remote missing: add one with `git remote add origin <your-repo-url>` before pushing.
- Static files in dev are served from `static/`; media from `media/` when `DEBUG=True`.
