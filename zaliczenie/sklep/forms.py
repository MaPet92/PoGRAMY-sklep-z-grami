from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Login:", widget=forms.TextInput(attrs={'placeholder': 'Wpisz login'}))
    password = forms.CharField(max_length=100, label="Hasło:", widget=forms.PasswordInput(attrs={'placeholder': 'Wpisz hasło'}))

class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=100, label="E-mail:", widget=forms.EmailInput(attrs={'placeholder': 'Wpisz e-mail'}))
    username = forms.CharField(max_length=100, label="Login:", widget=forms.TextInput(attrs={'placeholder': 'Wpisz login'}))
    password = forms.CharField(max_length=100, label="Hasło:", widget=forms.PasswordInput(attrs={'placeholder': 'Wpisz hasło'}))
    password2 = forms.CharField(max_length=100, label="Powtórz hasło:", widget=forms.PasswordInput(attrs={'placeholder': 'Wpisz hasło'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ten e-mail widnieje już w bazie")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ta nazwa użytkownika jest już zajęta")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError("Hasła muszą być takie same")
        return cleaned_data

class RemindPasswordForm(forms.Form):
    email = forms.EmailField(max_length=100, label="E-mail:", widget=forms.EmailInput(attrs={'placeholder': 'Wpisz e-mail'}))