from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""

    class Meta:
        model = Order
        fields = [
            'email', 'phone',
            'shipping_first_name', 'shipping_last_name',
            'shipping_address1', 'shipping_address2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'billing_same_as_shipping',
            'billing_first_name', 'billing_last_name',
            'billing_address1', 'billing_address2',
            'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
            'notes',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'shipping_first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'shipping_last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'shipping_address1': forms.TextInput(attrs={'placeholder': 'Street address'}),
            'shipping_address2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, etc. (optional)'}),
            'shipping_city': forms.TextInput(attrs={'placeholder': 'City'}),
            'shipping_state': forms.TextInput(attrs={'placeholder': 'State/Province'}),
            'shipping_postal_code': forms.TextInput(attrs={'placeholder': 'ZIP/Postal code'}),
            'shipping_country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'billing_first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'billing_last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'billing_address1': forms.TextInput(attrs={'placeholder': 'Street address'}),
            'billing_address2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, etc. (optional)'}),
            'billing_city': forms.TextInput(attrs={'placeholder': 'City'}),
            'billing_state': forms.TextInput(attrs={'placeholder': 'State/Province'}),
            'billing_postal_code': forms.TextInput(attrs={'placeholder': 'ZIP/Postal code'}),
            'billing_country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Order notes (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Pre-fill form if user is authenticated
        if user and user.is_authenticated:
            self.fields['email'].initial = user.email
            self.fields['shipping_first_name'].initial = user.first_name
            self.fields['shipping_last_name'].initial = user.last_name

            if hasattr(user, 'profile'):
                profile = user.profile
                self.fields['phone'].initial = profile.phone
                self.fields['shipping_address1'].initial = profile.address_line1
                self.fields['shipping_address2'].initial = profile.address_line2
                self.fields['shipping_city'].initial = profile.city
                self.fields['shipping_state'].initial = profile.state
                self.fields['shipping_postal_code'].initial = profile.postal_code
                self.fields['shipping_country'].initial = profile.country

