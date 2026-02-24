from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from apps.orders.models import Order
from apps.core.security import simple_rate_limit, log_security_event, sanitize_input


def ratelimited_error(request, exception=None):
    """View for rate limit exceeded errors"""
    return HttpResponse(
        'Too many requests. Please wait a moment and try again.',
        status=429
    )


def login_required_page(request):
    """Show login/register page for guests trying to access protected features"""
    if request.user.is_authenticated:
        # If already logged in, redirect to the next page or home
        next_url = request.GET.get('next', '/')
        return redirect(next_url)

    next_url = request.GET.get('next', '/')
    return render(request, 'accounts/login_required.html', {'next': next_url})


@simple_rate_limit('register', limit=5, period=300)  # 5 registrations per 5 minutes per IP
def register(request):
    """Handle user registration with rate limiting"""
    if request.user.is_authenticated:
        return redirect('products:home')

    # Get the next URL to redirect after registration
    next_url = request.GET.get('next', request.POST.get('next', ''))

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Sanitize inputs
            user = form.save(commit=False)
            user.first_name = sanitize_input(form.cleaned_data['first_name'])
            user.last_name = sanitize_input(form.cleaned_data['last_name'])
            user.save()

            # Specify backend since we have multiple authentication backends
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')
            log_security_event('USER_REGISTERED', f'New user registered: {user.username}', request)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')

            # Redirect to next URL if provided, otherwise to home
            if next_url:
                return redirect(next_url)
            return redirect('products:home')
        else:
            log_security_event('REGISTRATION_FAILED', f'Registration failed: {form.errors}', request)
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form, 'next': next_url})


@login_required
def profile(request):
    """Handle user profile viewing and updating"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})

