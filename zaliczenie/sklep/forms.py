from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm


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

class EditAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if not username:
            self.add_error('username', "Nazwa użytkownika jest wymagana.")
        if not email:
            self.add_error('email', "E-mail jest wymagany.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
             field.widget.attrs['readonly'] = True

        self.fields['first_name'].required = False
        self.fields['last_name'].required = False

        self.fields['username'].widget.attrs['placeholder'] = ' Nic tu nie ma'
        self.fields['email'].widget.attrs['placeholder'] = ' Nic tu nie ma'
        self.fields['first_name'].widget.attrs['placeholder'] = ' Nic tu nie ma'
        self.fields['last_name'].widget.attrs['placeholder'] = ' Nic tu nie ma'