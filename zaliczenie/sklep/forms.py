from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from sklep.models import Product

###

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

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'image', 'slug', 'price', 'genres', 'platform', 'producer', 'description', 'year_of_premiere', 'is_published', 'stock', 'promotion', 'promo_price']
        labels = {
            'name': 'Nazwa gry',
            'image': 'Okładka',
            'slug': 'Adres URL',
            'price': 'Cena podstawowa',
            'genres': 'Gatunki',
            'platform': 'Platforma',
            'producer': 'Producent',
            'description': 'Opis',
            'year_of_premiere': 'Rok premiery',
            'is_published': 'Czy opublikowany?',
            'stock': 'Stan w magazynie',
            'promotion': 'Czy promocja?',
            'promo_price': 'Cena promocyjna',
        }
        widgets = {
            'genres': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['genres'].queryset = self.fields['genres'].queryset.order_by('name')
        self.fields['producer'].queryset = self.fields['producer'].queryset.order_by('name')
        self.fields['platform'].queryset = self.fields['platform'].queryset.order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        promo_price = cleaned_data.get('promo_price')
        promotion = cleaned_data.get('promotion')

        if price and promo_price and price < promo_price:
            self.add_error('promo_price', "Cena promocyjna nie może być większa od ceny podstawowej.")

        if promotion and not promo_price:
            self.add_error('promo_price', "Brak ceny promocyjnej.")

        if not promotion and promo_price:
            self.add_error('promo_price', "Brak promocji, cena promocyjna powinna być pusta.")

        if price is not None and price <= 0:
            self.add_error('price', "Cena powinna być większa od zera.")

        if promotion and promo_price is not None and promo_price <= 0:
            self.add_error('promo_price', "Cena promocyjna powinna być większa od zera.")

        return cleaned_data