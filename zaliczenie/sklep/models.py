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

class ContactData(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='customer', null=True, blank=True)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class CartManager(models.Manager):
    def new_or_get_active_cart(self, user):
        cart = self.filter(customer=user, status=Cart.STATUS_NEW)

        if cart.exists():
            return cart.first(), False

        return self.create(customer=user, status=Cart.STATUS_NEW), True

class Cart(models.Model):
    STATUS_NEW = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SEND = 'send'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Nowe'),
        (STATUS_PAID, 'Opłacone'),
        (STATUS_SEND, 'Wysłane'),
        (STATUS_COMPLETED, 'Zakończone'),
        (STATUS_CANCELLED, 'Anulowane'),
    ]

    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    objects = CartManager()

    class Meta:
        unique_together = ('customer', 'status')

    def add_product(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        self.update_total_price()

    def remove_product(self, product, quantity=1):
        try:
            cart_item = self.cartitem_set.get(product=product)

            if cart_item.quantity > quantity:
                cart_item.quantity -= quantity
                cart_item.save()
            else:
                cart_item.delete()
            self.update_total_price()
        except CartItem.DoesNotExist:
            pass

    def get_items(self):
        return self.cartitem_set.all()

    def get_total_quantity(self):
        return sum(item.quantity for item in self.get_items())

    def update_total_price(self):
        total = sum((item.product.promo_price if item.product.promotion else item.product.price) * item.quantity for item in self.get_items())
        self.total_price = total
        self.save(update_fields=['total_price'])

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class Order(models.Model):
    STATUS_NEW = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SEND = 'send'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Nowe'),
        (STATUS_PAID, 'Opłacone'),
        (STATUS_SEND, 'Wysłane'),
        (STATUS_COMPLETED, 'Zakończone'),
        (STATUS_CANCELLED, 'Anulowane'),
    ]

    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    address = models.CharField(blank=True, null=True, max_length=128)
    payment_method = models.CharField(max_length=128)

    def get_items(self):
        return self.orderitem_set.all()

    def update_total_price(self):
        total = sum(item.price * item.quantity for item in self.get_items())
        self.total_price = total
        self.save(update_fields=['total_price'])

    def __str__(self):
        return f'Order #{self.pk} - {self.customer}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'