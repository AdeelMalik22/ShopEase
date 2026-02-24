from django.urls import path
from . import views
from . import webhooks

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', webhooks.stripe_webhook, name='webhook'),
]

