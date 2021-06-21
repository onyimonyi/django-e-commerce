from django import forms
from .models import Item


class ProductForm(forms.ModelForm):
    price = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea(
        attrs={
            'placeholder': 'your description',
            "cols": 70,
            'rows': 8
        }
    ))

    class Meta:
        model = Item
        fields = [
            'price',
            'title',
            'discount_price',
            'category',
            'description',
            'picture',
            'label'
        ]


PAYMENT_CHOICES = (
    ('PS', 'PayStack'),
    ('BTC', 'Bitcoin')

)


class CheckoutForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'your first name',
        'class': 'form-control'

    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'another name',
        'class': 'form-control'
    }))
    street_or_office_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_or_suite = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'apartment / suite or office...',
        'class': 'form-control'
    }))
    zip = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Zip'
    }))
    phone_number = forms.CharField(widget=forms.NumberInput(attrs={
        'placeholder': 'your phone number',
        'class': 'form-control'

    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_options = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)



class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 3, }))
    email = forms.EmailField()
