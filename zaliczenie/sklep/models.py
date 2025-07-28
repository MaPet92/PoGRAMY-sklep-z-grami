from token import MINUS

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

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
    name = models.CharField(max_length=64)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.customer.name} cart'

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.name} order'