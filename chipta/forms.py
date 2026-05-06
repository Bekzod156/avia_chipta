from django import forms
from django.contrib.auth.models import User
from .models import Passenger, Ticket


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="Ism")
    last_name = forms.CharField(max_length=50, label="Familiya")
    email = forms.EmailField(label="Elektron pochta")
    passport_number = forms.CharField(max_length=20, label="Pasport raqami")
    phone_number = forms.CharField(max_length=20, label="Telefon raqami")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Parol")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Parolni tasdiqlang")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan!")
        return email

    def clean_passport_number(self):
        passport = self.cleaned_data.get('passport_number')
        if Passenger.objects.filter(passport_number=passport).exists():
            raise forms.ValidationError("Bu pasport raqami allaqachon ro'yxatdan o'tgan!")
        return passport

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Parollar mos kelmadi!")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label="Elektron pochta")
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['seat_number']