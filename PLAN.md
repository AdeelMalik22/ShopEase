# Django Ecommerce Application Development Plan

## Project Overview

A full-featured ecommerce platform built with Django, featuring user authentication,
product catalog, shopping cart, order management, and Stripe payments. The frontend uses Django's Jinja2-like templating
with Bootstrap 5 for a responsive design.

---

## Project Structure

```
ecommerce_ai/
├── manage.py
├── requirements.txt
├── README.md
├── PLAN.md
├── .env.example
├── .gitignore
├── config/                    # Project settings
│   ├── __init__.py
│   ├── settings.py           # Main settings
│   ├── urls.py               # Root URL config
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/             # User authentication & profiles
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── products/             # Product catalog & categories
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── cart/                 # Shopping cart (session-based)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── cart.py
│   │   ├── context_processors.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── orders/               # Order management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   └── payments/             # Stripe integration
│       ├── __init__.py
│       ├── apps.py
│       ├── urls.py
│       ├── views.py
│       └── webhooks.py
├── templates/                # Global templates
│   ├── base.html
│   ├── includes/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── messages.html
│   ├── accounts/
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── logout.html
│   │   ├── profile.html
│   │   ├── order_history.html
│   │   ├── password_reset.html
│   │   ├── password_reset_done.html
│   │   ├── password_reset_confirm.html
│   │   └── password_reset_complete.html
│   ├── products/
│   │   ├── home.html
│   │   ├── product_list.html
│   │   ├── product_detail.html
│   │   └── search_results.html
│   ├── cart/
│   │   └── cart_detail.html
│   ├── orders/
│   │   ├── checkout.html
│   │   └── order_detail.html
│   └── payments/
│       ├── payment.html
│       ├── success.html
│       └── cancel.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   └── cart.js
│   └── images/
│       └── placeholder.png
└── media/                    # User uploaded files
    └── products/
```

---

## Phase 1: Project Setup & Configuration (Days 1-2)

### Milestone

Django project scaffolded with settings, database configured, and admin accessible.

### Tasks

1. Initialize Django project with proper structure
2. Create requirements.txt with all dependencies
3. Configure environment variables with .env file
4. Set up static/media file handling
5. Create all 5 Django apps: accounts, products, cart, orders, payments
6. Configure database (SQLite for development)

### Dependencies

- Django 4.2+
- Pillow (image handling)
- stripe (payment processing)
- python-dotenv (environment variables)
- django-crispy-forms & crispy-bootstrap5 (form styling)

---

## Phase 2: Database Models (Days 3-5)

### Milestone

All models created with migrations applied, visible in Django admin.

### Models

#### accounts/models.py

- **UserProfile** — extends User via OneToOne
    - `phone`, `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`, `created_at`

#### products/models.py

- **Category**
    - `name`, `slug`, `description`, `image`, `is_active`, `created_at`
- **Product**
    - `name`, `slug`, `description`, `price`, `compare_price`, `category` (FK), `stock`, `image`, `is_active`,
      `is_featured`, `created_at`, `updated_at`

#### orders/models.py

- **Order**
    - `user` (FK, nullable for guest), `order_number`, `email`, `phone`
    - Shipping: `shipping_address1`, `shipping_address2`, `shipping_city`, `shipping_state`, `shipping_postal_code`,
      `shipping_country`
    - Billing: `billing_address1`, `billing_address2`, `billing_city`, `billing_state`, `billing_postal_code`,
      `billing_country`
    - `subtotal`, `shipping_cost`, `tax`, `total`, `status`, `stripe_payment_intent`, `created_at`, `updated_at`
- **OrderItem**
    - `order` (FK), `product` (FK), `product_name`, `product_price`, `quantity`, `subtotal`

---

## Phase 3: User Authentication (Days 6-8)

### Milestone

Users can register, login, logout, reset password, and manage profile.

### URL Routing

| URL                         | View              | Description          |
|-----------------------------|-------------------|----------------------|
| `/accounts/register/`       | register          | User registration    |
| `/accounts/login/`          | LoginView         | User login           |
| `/accounts/logout/`         | LogoutView        | User logout          |
| `/accounts/password-reset/` | PasswordResetView | Password reset       |
| `/accounts/profile/`        | profile           | View/edit profile    |
| `/accounts/orders/`         | order_history     | User's order history |

### Features

- Custom registration form with email field
- Auto-create UserProfile via signals
- Django's built-in auth views with custom templates
- Profile editing with user and address information
- Order history with pagination

---

## Phase 4: Product Catalog (Days 9-12)

### Milestone

Products browsable by category, searchable, with detail pages.

### URL Routing

| URL                 | View              | Description                     |
|---------------------|-------------------|---------------------------------|
| `/`                 | home              | Homepage with featured products |
| `/products/`        | product_list      | All products listing            |
| `/products/<slug>/` | product_detail    | Product detail page             |
| `/category/<slug>/` | category_products | Products by category            |
| `/search/`          | search            | Search results                  |

### Features

- Product listing with pagination (12 per page)
- Filtering by category, price range
- Sorting by price, name, newest
- Search functionality using Q objects
- Category navigation
- Related products on detail page
- Featured products on homepage

---

## Phase 5: Shopping Cart & Checkout (Days 13-17)

### Milestone

Functional cart with add/update/remove, checkout flow leading to payment.

### Cart Implementation (Session-based)

```python
# cart/cart.py
class Cart:
    def add(product, quantity)

        def remove(product_id)

        def update(product_id, quantity)

        def clear()

        def get_total()

        def __iter__()

        def __len__()
```

### URL Routing - Cart

| URL                          | View        | Description            |
|------------------------------|-------------|------------------------|
| `/cart/`                     | cart_detail | View cart              |
| `/cart/add/<product_id>/`    | cart_add    | Add to cart (POST)     |
| `/cart/update/<product_id>/` | cart_update | Update quantity (POST) |
| `/cart/remove/<product_id>/` | cart_remove | Remove item (POST)     |

### URL Routing - Orders

| URL                      | View         | Description        |
|--------------------------|--------------|--------------------|
| `/checkout/`             | checkout     | Checkout form      |
| `/order/<order_number>/` | order_detail | Order confirmation |

### Features

- Session-based cart storage
- Dynamic quantity updates
- Cart item count in navbar
- Guest checkout with email
- Shipping/billing address forms
- Order creation with stock validation

---

## Phase 6: Stripe Payment Integration (Days 18-22)

### Milestone

Secure payment flow with Stripe Checkout, webhook handling.

### URL Routing

| URL                                 | View                    | Description             |
|-------------------------------------|-------------------------|-------------------------|
| `/payment/create-checkout-session/` | create_checkout_session | Create Stripe session   |
| `/payment/success/`                 | payment_success         | Payment success page    |
| `/payment/cancel/`                  | payment_cancel          | Payment cancelled       |
| `/payment/webhook/`                 | stripe_webhook          | Stripe webhook endpoint |

### Integration Flow

1. User completes checkout form → Order created with "pending" status
2. Redirect to Stripe Checkout session
3. Stripe handles payment UI, card validation, 3D Secure
4. On success, webhook updates order status to "processing"
5. User redirected to success page

### Webhook Events Handled

- `checkout.session.completed` — Update order status, clear cart

---

## Phase 7: Admin Dashboard (Days 23-25)

### Milestone

Admin can efficiently manage products, orders, view sales.

### Customizations

- **ProductAdmin**: Image preview, bulk actions (activate/deactivate)
- **OrderAdmin**: Status filters, inline OrderItems, bulk status updates
- **CategoryAdmin**: Nested display, ordering

---

## Phase 8: Frontend & Polish (Days 26-30)

### Milestone

Responsive, polished UI with consistent styling.

### Technical Stack

- Bootstrap 5 (via CDN)
- django-crispy-forms with crispy-bootstrap5
- Custom CSS for overrides
- JavaScript for cart interactions

### Features

- Responsive product grid (3 cols desktop, 2 tablet, 1 mobile)
- Cart AJAX updates
- Form validation feedback
- Loading states for payment
- Django messages with Bootstrap alerts
- Mobile-friendly navigation

---

## Key Features Summary

### Customer Features

- [x] User registration & authentication
- [x] Password reset via email
- [x] Product browsing & search
- [x] Category filtering
- [x] Shopping cart management
- [x] Secure checkout with Stripe
- [x] Order history & tracking
- [x] Responsive design

### Admin Features

- [x] Product management (CRUD)
- [x] Category management
- [x] Order management & status updates
- [x] User management
- [x] Inventory tracking

### Technical Features

- [x] Session-based cart
- [x] Stripe Checkout integration
- [x] Webhook handling
- [x] Environment-based configuration
- [x] Image upload handling
- [x] Pagination
- [x] Search functionality

---

## Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Email (for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Testing Checklist

### User Authentication

- [ ] User can register with email
- [ ] User can login/logout
- [ ] Password reset works
- [ ] Profile can be updated

### Products

- [ ] Products display correctly
- [ ] Categories filter products
- [ ] Search returns relevant results
- [ ] Pagination works

### Cart

- [ ] Products can be added to cart
- [ ] Quantities can be updated
- [ ] Items can be removed
- [ ] Cart persists in session

### Checkout & Payment

- [ ] Checkout form validates
- [ ] Order is created correctly
- [ ] Stripe payment processes
- [ ] Webhook updates order status
- [ ] Success/cancel pages work

---

## Future Enhancements (Post-MVP)

1. **Product Reviews & Ratings**
2. **Wishlist functionality**
3. **Coupon/Discount codes**
4. **Multiple product images**
5. **Email notifications (order confirmation, shipping)**
6. **Inventory management alerts**
7. **Product variants (size, color)**
8. **Social login (Google, Facebook)**
9. **Advanced search with filters**
10. **Sales analytics dashboard**

