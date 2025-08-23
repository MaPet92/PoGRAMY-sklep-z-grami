import random
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Case, When, F, DecimalField
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.views.generic import ListView, View
from sklep.models import Product, Platform, Genre, Producer, Order, OrderItem, Cart
from sklep.forms import LoginForm, RegisterForm, RemindPasswordForm, EditAccountForm, AddProductForm, OrderForm


# Create your views here.

def home_page(request):
    promo_games = list(Product.objects.filter(promotion=True))
    random_promo_games = random.sample(promo_games, min(len(promo_games), 5))
    for game in random_promo_games:
        game.discount = round(100 - ((game.promo_price / game.price) * 100), 0)
    coming_games = list(Product.objects.filter(is_published=False))
    random_coming_games = random.sample(coming_games, min(len(coming_games), 5))
    pc_games = list(Product.objects.filter(platform_id=1, is_published=True))
    random_pc_games = random.sample(pc_games, min(len(pc_games), 5))
    playstation_games = list(Product.objects.filter(platform_id=2, is_published=True))
    random_playstation_games = random.sample(playstation_games, min(len(playstation_games), 5))
    xbox_games = list(Product.objects.filter(platform_id=3, is_published=True))
    random_xbox_games = random.sample(xbox_games, min(len(xbox_games), 5))
    switch_games = list(Product.objects.filter(platform_id=4, is_published=True))
    random_switch_games = random.sample(switch_games, min(len(switch_games), 5))
    return render(request, 'home.html', {'random_promo_games': random_promo_games, 'random_coming_games': random_coming_games, 'random_pc_games': random_pc_games, 'random_playstation_games': random_playstation_games, 'random_xbox_games': random_xbox_games, 'random_switch_games': random_switch_games})

def login(request, *args, **kwargs):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                auth_login(request, user)
                messages.success(request, "Zalogowano poprawnie")
                return redirect('home')
            else:
                messages.error(request, "Nieprawidłowy login lub hasło")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_page(request):
    logout(request)
    return redirect('home')

def game_page(request, slug):
    game = get_object_or_404(Product, slug=slug)
    if game.promotion:
        game.discount = round(100 - ((game.promo_price / game.price) * 100), 0)
    platform = get_object_or_404(Platform, id=game.platform_id)
    gameset = Product.objects.filter(platform_id=game.platform_id).exclude(id=game.id)
    return render(request, 'game.html', {'game': game, 'platform': platform, 'gameset': gameset})

class GamesView(ListView):
    model = Product
    template_name = 'games.html'
    context_object_name =  'games'
    filter_by = None
    coming_soon = False
    paginate_by = 24

    def get_sorted_by(self):
        return self.request.GET.get('sorted', 'name')

    def get_queryset(self):
        qs = Product.objects.all().select_related('platform', 'producer').prefetch_related('genres')

        if self.filter_by == 'platform':
            platform_slug = self.kwargs.get('platform_slug')
            self.platform = get_object_or_404(Platform, slug=platform_slug)
            qs = qs.filter(platform=self.platform)

        elif self.filter_by == 'producer':
            producer_slug = self.kwargs.get('producer_slug')
            self.producer = get_object_or_404(Producer, slug=producer_slug)
            qs = qs.filter(producer=self.producer)

        elif self.filter_by == 'genre':
            genre_slug = self.kwargs.get('genre_slug')
            self.genre = get_object_or_404(Genre, slug=genre_slug)
            qs = qs.filter(genres=self.genre).distinct()

        if self.coming_soon:
            qs = qs.filter(is_published=False)

        return sortings(qs, self.get_sorted_by())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sorted'] = self.get_sorted_by()

        if hasattr(self, 'platform'):
            ctx.update({'platform': self.platform, 'slug': self.platform.slug, 'filter_by': 'platform'})
        if hasattr(self, 'producer'):
            ctx.update({'producer': self.producer, 'slug': self.producer.slug, 'filter_by': 'producer'})
        if hasattr(self, 'genre'):
            ctx.update({'genre': self.genre, 'slug': self.genre.slug, 'filter_by': 'genre'})

        if self.coming_soon:
            ctx['coming_soon'] = True

        return ctx

def sortings(queryset, sorted_by):
    if sorted_by == 'name_up':
        return queryset.order_by('name')
    if sorted_by == 'name_down':
        return queryset.order_by('-name')
    elif sorted_by == 'price_up':
        annotated_qs = queryset.annotate(
            price_to_sort=Case(
                When(promotion=True, then=F('promo_price')),
                default=F('price'),
                output_field=DecimalField()
            )
        ).order_by('price_to_sort')
        return annotated_qs
    elif sorted_by == 'price_down':
        annotated_qs = queryset.annotate(
            price_to_sort=Case(
                When(promotion=True, then=F('promo_price')),
                default=F('price'),
                output_field=DecimalField()
            )
        ).order_by('-price_to_sort')
        return annotated_qs
    elif sorted_by == 'year_of_premiere_up':
        return queryset.order_by('year_of_premiere')
    elif sorted_by == 'year_of_premiere_down':
        return queryset.order_by('-year_of_premiere')
    else:
        return queryset.order_by('name')

def remind_password(request, *args, **kwargs):
    if request.method == 'POST':
        form = RemindPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            exists = User.objects.filter(email=email).exists()
            if exists:
                messages.success(request, "Link do zresetowania hasła wysłany na podany e-mail")
            else:
                messages.error(request, "Nie znaleziono użytkownika o podanym e-mailu")
            return redirect('remind_password')
    else:
        form = RemindPasswordForm()
    return render(request, 'remind_password.html', {'form': form})

def register(request, *args, **kwargs):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'], email=form.cleaned_data['email'])
            messages.success(request, "Użytkownik dodany pomyślnie")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        games = Product.objects.filter(name__icontains=query)
    else:
        games = Product.objects.all()
    return render(request, 'search_games.html', {'games': games})

def account(request):
    if not request.user.is_authenticated:
        messages.error(request, "Musisz być zalogowany")
        return redirect('login')

    if request.method == 'POST':
        form = EditAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Zaktualizowano dane.")
            return redirect('account')
    else:
        form = EditAccountForm(instance=request.user)

    return render(request, 'account.html', {'form': form})

class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'login'
    raise_exception = False

    def test_func(self):
        return bool(self.request.user and self.request.user.is_superuser)

    def handle_no_permission(self):
        messages.error(self.request, "Nie masz uprawnień do tej strony")
        return redirect('home')

class ProductsAdminView(SuperUserRequiredMixin, View):
    action = 'list'

    def get(self, request, *args, **kwargs):
        action = getattr(self, 'action', 'list')
        product_id = kwargs.get('product_id')

        if action == 'list':
            products = Product.objects.all().order_by('name')
            platforms = Platform.objects.all()
            producers = Producer.objects.all()
            return render(request, 'products_list.html', {'products': products, 'platforms': platforms, 'producers': producers})

        if action == 'add':
            form = AddProductForm()
            return render(request, 'add_product.html', {'form': form})

        if action == 'edit':
            product = get_object_or_404(Product, id=product_id)
            form = AddProductForm(instance=product)
            return render(request, 'edit_product.html', {'form': form, 'product': product})

        return redirect('products_list')

    def post(self, request, *args, **kwargs):
        action = getattr(self, 'action', 'list')
        product_id = kwargs.get('product_id')

        if action == 'add':
            form = AddProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Zapisano poprawnie")
                return redirect('add_product')
            return render(request, 'products_list.html', {'form': form})

        if action == 'edit':
            product = get_object_or_404(Product, id=product_id)
            form = AddProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Zapisano poprawnie")
                return redirect('edit_product', product_id=product.id)
            return render(request, 'edit_product.html', {'form': form, 'product': product})

        if action == 'delete':
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, "Produkt usunięty poprawnie")
            return redirect('products_list')

        return redirect('products_list')

class CartView(LoginRequiredMixin, View):

    def get_cart(self, user):
        cart, _ = Cart.objects.new_or_get_active_cart(user)
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_cart(request.user)
        items = cart.get_items() if cart else []
        return render(request, 'cart.html', {'cart': cart, 'items': items})

    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = self.get_cart(request.user)

        if action == 'add':
            cart.add_product(product, quantity=1)
            messages.success(request, f'Produkt <strong>{product.name}</strong> dodany do koszyka.')
        elif action == 'remove':
            cart.remove_product(product, quantity=1)
            messages.success(request, f'Produkt <strong>{product.name}</strong> usunięty z koszyka.')

        return redirect(request.META.get('HTTP_REFERER', '/'))

class OrderView(LoginRequiredMixin, View):
    login_url = 'login'

    def get_user_cart(self, user):
        try:
            return Cart.objects.get(customer=user, status=Cart.STATUS_NEW)
        except Cart.DoesNotExist:
            return None

    @transaction.atomic
    def create_order_from_cart(self, cart, form_data):
        address = f'{form_data["street"]}, {form_data["house_number"]}'
        if form_data["apartment_number"]:
            address += f' {form_data["apartment_number"]}'
        address += f', {form_data["city"]}, {form_data["zip_code"]}'

        order = Order.objects.create(
            customer=cart.customer,
            first_name=form_data['first_name'],
            last_name=form_data['last_name'],
            phone=form_data['phone'],
            email=form_data['email'],
            address=address,
            payment_method=form_data['payment_method'],
            status=Order.STATUS_NEW
        )

        for cart_item in cart.get_items():
            product = cart_item.product
            if product.stock < cart_item.quantity:
                raise ValueError(f'Nie ma wystarczającej liczby kopii {product.name} w magazynie.')

            price = product.promo_price if product.promotion else product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=price
            )

            product.stock = max(product.stock - cart_item.quantity, 0)
            product.save(update_fields=['stock'])

        order.update_total_price()
        cart.cartitem_set.all().delete()
        cart.status = Cart.STATUS_COMPLETED
        cart.save()

        return order

    def get(self, request, *args, **kwargs):
        action = kwargs.get('action')
        order_id = kwargs.get('order_id')

        if action == 'place':
            cart = self.get_user_cart(request.user)
            if not cart or not cart.get_items():
                messages.error(request, "Twój koszyk jest pusty")
                return redirect('cart')

            form = OrderForm()
            return render(request, 'order_form.html', {'cart': cart, 'form': form, 'items': cart.get_items()})

        elif action == 'view' and order_id:
            order = get_object_or_404(Order, id=order_id)
            if order.customer != request.user:
                return HttpResponseForbidden("Nie masz dostępu do tej strony.")
            return render(request, 'order_view.html', {'order': order})

        elif action == 'history':
            orders = Order.objects.filter(customer=request.user).order_by('-date')
            return render(request, 'history.html', {'orders': orders})

        return redirect('home')

    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')

        if action != 'place':
            return redirect('home')

        cart = self.get_user_cart(request.user)
        if not cart or not cart.get_items():
            messages.error(request, "Twój koszyk jest pusty")
            return redirect('cart')

        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = self.create_order_from_cart(cart, form.cleaned_data)
                return redirect('order_view', order_id=order.id)
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'order_form.html', {'form': form, 'cart': cart, 'items': cart.get_items()})

        return render(request, 'order_form.html', {'cart': cart, 'form': form, 'items': cart.get_items()})

class OrdersAdminView(SuperUserRequiredMixin, View):
    action = 'list'

    def get(self, request, *args, **kwargs):
        action = getattr(self, 'action', 'list')
        order_id = kwargs.get('order_id')

        if action == 'list':
            orders = Order.objects.all().order_by('-date')
            return render(request, 'orders_list.html', {'orders': orders})

        return redirect('orders_list')

    def post(self, request, *args, **kwargs):
        action = getattr(self, 'action', 'list')
        order_id = kwargs.get('order_id')

        if action == 'delete':
            order = get_object_or_404(Order, id=order_id)
            with transaction.atomic():
                for item in order.orderitem_set.all():
                    item.product.stock += item.quantity
                    item.product.save(update_fields=['stock'])
                order.delete()
            messages.success(request, "Zamówienie usunięte poprawnie")
            return redirect('orders_list')

        if action == 'list':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            if order_id and new_status:
                order = get_object_or_404(Order, id=order_id)
                if new_status in dict(Order.STATUS_CHOICES).keys():
                    order.status = new_status
                    order.save(update_fields=['status'])
                    messages.success(request, f"Status zamówienia nr {order.id} zmieniony na {order.get_status_display()}")
                else:
                    messages.error(request, "Nie udało się zmienić statusu. Wybierz poprawny status z listy")

        return redirect('orders_list')
