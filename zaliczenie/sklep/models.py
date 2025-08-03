from django.core.validators import MinValueValidator
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