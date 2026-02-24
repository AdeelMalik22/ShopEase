from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['product_name', 'product_price', 'quantity', 'subtotal']
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'email', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['order_number', 'email', 'shipping_first_name', 'shipping_last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'subtotal', 'shipping_cost', 'tax', 'total']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'stripe_payment_intent', 'stripe_checkout_session_id')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Shipping Address', {
            'fields': (
                ('shipping_first_name', 'shipping_last_name'),
                'shipping_address1', 'shipping_address2',
                ('shipping_city', 'shipping_state'),
                ('shipping_postal_code', 'shipping_country')
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_same_as_shipping',
                ('billing_first_name', 'billing_last_name'),
                'billing_address1', 'billing_address2',
                ('billing_city', 'billing_state'),
                ('billing_postal_code', 'billing_country')
            ),
            'classes': ('collapse',)
        }),
        ('Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    @admin.action(description='Mark selected orders as processing')
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')

    @admin.action(description='Mark selected orders as shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description='Mark selected orders as delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description='Mark selected orders as cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_price', 'quantity', 'subtotal']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['product_name', 'order__order_number']

