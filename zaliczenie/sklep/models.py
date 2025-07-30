from decimal import Decimal
from token import MINUS

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Producer(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='games/', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    genres = models.ManyToManyField(Genre)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    year_of_premiere = models.IntegerField()
    is_published = models.BooleanField(default=True)
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    rating = models.DecimalField(null=True, blank=True, max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)])
    promotion = models.BooleanField(default=False)
    promo_price = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='customer', null=True, blank=True)
    name = models.CharField(max_length=64)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    date_added = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    STATUS_OPTIONS = [
        ('new', 'Nowe'),
        ('processing', 'W trakcie'),
        ('completed', 'Zakończone'),
        ('cancelled', 'Anulowane'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_OPTIONS, default='new')

    def add_to_cart(self, product, quantity=1):
        if product.stock < quantity:
            raise ValueError('Brak wystarczającej liczby produktów w magazynie')

        product.stock -= quantity
        product.save()

        item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        self.update_total_price()

    def remove_from_cart(self, product, quantity=1):
        try:
            item = CartItem.objects.get(cart=self, product=product)
        except CartItem.DoesNotExist:
            return

        if quantity >= item.quantity:
            product.stock += item.quantity
            item.delete()
        else:
            item.quantity -= quantity
            product.stock += quantity
            item.save()

        product.save()
        self.update_total_price()

    def update_total_price(self):
        total = 0
        for item in self.cartitem_set.select_related('product'):
            price = item.product.promo_price if item.product.promotion else item.product.price
            total += price * item.quantity
        self.total_price = total
        self.save()