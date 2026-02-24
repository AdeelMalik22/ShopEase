from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Form for adding/editing products"""

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'category', 'description',
            'price', 'compare_price', 'stock',
            'image', 'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'product-slug'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'compare_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Original price (optional)'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['compare_price'].required = False
        self.fields['image'].required = False
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'Leave blank to auto-generate from name'


class CategoryForm(forms.ModelForm):
    """Form for adding/editing categories"""

    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'category-slug'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['image'].required = False
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'Leave blank to auto-generate from name'

