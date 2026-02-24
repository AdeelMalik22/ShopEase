from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active', 'is_featured', 'image_preview']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'compare_price', 'stock')
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="object-fit: contain;" />', obj.image.url)
        return 'No image'
    image_preview_large.short_description = 'Image Preview'

    actions = ['make_active', 'make_inactive', 'make_featured', 'remove_featured']

    @admin.action(description='Mark selected products as active')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Mark selected products as inactive')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Mark selected products as featured')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Remove featured status from selected products')
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)

