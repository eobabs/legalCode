from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Case, Donation


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'description', 'goal_amount', 'deadline', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a compelling case title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe the legal situation, why funding is needed, and how it will be used...'
            }),
            'goal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter funding goal (e.g., 5000)',
                'min': '1'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().strftime('%Y-%m-%d')
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now().date():
            raise forms.ValidationError("Deadline must be in the future.")
        return deadline

    def clean_goal_amount(self):
        amount = self.cleaned_data.get('goal_amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Goal amount must be greater than zero.")
        return amount


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount', 'message', 'is_anonymous']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter donation amount',
                'min': '1',
                'step': '0.01'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional message of support (visible to case creator)'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Donation amount must be greater than zero.")
        return amount