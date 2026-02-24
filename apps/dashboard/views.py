from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from django.contrib.auth.models import User


def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with overview statistics"""
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    # Statistics
    stats = {
        'total_orders': Order.objects.count(),
        'total_revenue': Order.objects.filter(status='processing').aggregate(Sum('total'))['total__sum'] or 0,
        'total_products': Product.objects.count(),
        'total_users': User.objects.filter(is_staff=False).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'processing_orders': Order.objects.filter(status='processing').count(),
        'shipped_orders': Order.objects.filter(status='shipped').count(),
        'delivered_orders': Order.objects.filter(status='delivered').count(),
        'low_stock_products': Product.objects.filter(stock__lte=5, is_active=True).count(),
    }

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]

    # Low stock products
    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True)[:5]

    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboard/index.html', context)


# ============== PRODUCT MANAGEMENT ==============

@login_required
@user_passes_test(is_admin)
def product_list(request):
    """List all products for admin"""
    products = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'dashboard/products/list.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def product_add(request):
    """Add a new product"""
    from apps.products.forms import ProductForm

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()

    return render(request, 'dashboard/products/form.html', {
        'form': form,
        'title': 'Add New Product',
        'button_text': 'Add Product'
    })


@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    """Edit an existing product"""
    from apps.products.forms import ProductForm

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/products/form.html', {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.name}',
        'button_text': 'Update Product'
    })


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('dashboard:product_list')

    return render(request, 'dashboard/products/delete.html', {'product': product})


# ============== CATEGORY MANAGEMENT ==============

@login_required
@user_passes_test(is_admin)
def category_list(request):
    """List all categories"""
    # Don't use annotate - Category model already has product_count property
    categories = Category.objects.order_by('name')
    return render(request, 'dashboard/categories/list.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
def category_add(request):
    """Add a new category"""
    from apps.products.forms import CategoryForm

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()

    return render(request, 'dashboard/categories/form.html', {
        'form': form,
        'title': 'Add New Category',
        'button_text': 'Add Category'
    })


@login_required
@user_passes_test(is_admin)
def category_edit(request, pk):
    """Edit an existing category"""
    from apps.products.forms import CategoryForm

    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'dashboard/categories/form.html', {
        'form': form,
        'category': category,
        'title': f'Edit Category: {category.name}',
        'button_text': 'Update Category'
    })


@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/categories/delete.html', {'category': category})


# ============== ORDER MANAGEMENT ==============

@login_required
@user_passes_test(is_admin)
def order_list(request):
    """List all orders"""
    status_filter = request.GET.get('status', '')

    orders = Order.objects.order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/orders/list.html', context)


@login_required
@user_passes_test(is_admin)
def order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'dashboard/orders/detail.html', {'order': order})


@login_required
@user_passes_test(is_admin)
def order_update_status(request, pk):
    """Update order status"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order.order_number} status updated from "{old_status}" to "{new_status}"')
        else:
            messages.error(request, 'Invalid status')

    return redirect('dashboard:order_detail', pk=pk)


# ============== USER MANAGEMENT ==============

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users"""
    users = User.objects.order_by('-date_joined')
    return render(request, 'dashboard/users/list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    """View user details"""
    user_obj = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=user_obj).order_by('-created_at')
    return render(request, 'dashboard/users/detail.html', {
        'user_obj': user_obj,
        'orders': orders,
    })

