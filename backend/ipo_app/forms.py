# ipo_app/forms.py

from django import forms
from .models import IPO, Document
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class IPOLoginForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if username and email:
            try:
                user = User.objects.get(username=username)
                if user.email.lower() != email.lower():
                    raise ValidationError("Invalid email address for the given username.")
            except User.DoesNotExist:
                raise ValidationError("No such user exists.")

        return cleaned_data

class IPOForm(forms.ModelForm):
    # Plain text input for company name
    company = forms.CharField(
        label='Company',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Company Name'
        })
    )

    class Meta:
        model = IPO
        exclude = ['company']  # handled manually in views
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price_band': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_size': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_type': forms.TextInput(attrs={'class': 'form-control'}),
            'ipo_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'listing_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_market_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'open_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'close_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'listing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'company_logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class RHPForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'file': 'Upload RHP PDF'
        }

class DRHPForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'file': 'Upload DRHP PDF'
        }
