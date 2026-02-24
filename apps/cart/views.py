from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.products.models import Product
from .cart import Cart


@login_required
def cart_detail(request):
    """Display the shopping cart"""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@login_required
@require_POST
def cart_add(request, product_id):
    """Add a product to the cart - requires login"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    quantity = int(request.POST.get('quantity', 1))
    update = request.POST.get('update', False)

    # Check stock availability
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
        return redirect('cart:cart_detail')

    cart.add(product=product, quantity=quantity, update_quantity=bool(update))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_update(request, product_id):
    """Update product quantity in the cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))

    # Check stock availability
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
        return redirect('cart:cart_detail')

    if quantity > 0:
        cart.add(product=product, quantity=quantity, update_quantity=True)
        messages.success(request, 'Cart updated successfully.')
    else:
        cart.remove(product)
        messages.success(request, f'{product.name} has been removed from your cart.')

    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
        })

    messages.success(request, f'{product.name} has been removed from your cart.')
    return redirect('cart:cart_detail')

