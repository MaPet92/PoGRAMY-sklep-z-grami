import random

from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, F, DecimalField
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.views.decorators.http import require_POST
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

def logout_page(request):
    logout(request)
    return redirect('home')

def game_page(request, slug):
    game = get_object_or_404(Product, slug=slug)
    if game.promotion:
        game.discount = round(100 - ((game.promo_price / game.price) * 100), 0)
    platform = get_object_or_404(Platform, id=game.platform_id)
    gameset = Product.objects.filter(platform_id=game.platform_id)
    return render(request, 'game.html', {'game': game, 'platform': platform, 'gameset': gameset})

def games(request):
    sorted_by = request.GET.get('sorted', 'name')
    games = Product.objects.all()
    games = sortings(games, sorted_by)
    return render(request, 'games.html', {'games': games, 'sorted': sorted_by})

def games_by_platform(request, platform_slug):
    sorted_by = request.GET.get('sorted', 'name')
    platform = get_object_or_404(Platform, slug=platform_slug)
    games = Product.objects.filter(platform=platform)
    games = sortings(games, sorted_by)
    return render(request, 'games.html', {'sorted': sorted_by, 'platform': platform, 'slug': platform_slug, 'games': games})

def games_by_producer(request, producer_slug):
    sorted_by = request.GET.get('sorted', 'name')
    producer = get_object_or_404(Producer, slug=producer_slug)
    games = Product.objects.filter(producer=producer)
    games = sortings(games, sorted_by)
    return render(request, 'games.html', {'sorted': sorted_by, 'producer': producer, 'slug': producer_slug, 'games': games})

def games_by_genre(request, genre_slug):
    sorted_by = request.GET.get('sorted', 'name')
    genre = get_object_or_404(Genre, slug=genre_slug)
    games = Product.objects.filter(genres=genre)
    games = sortings(games, sorted_by)
    return render(request, 'games.html', {'sorted': sorted_by, 'genre': genre, 'slug': genre_slug, 'games': games})

def incoming_games(request):
    sorted_by = request.GET.get('sorted', 'name')
    games = Product.objects.filter(is_published=False)
    games = sortings(games, sorted_by)
    return render(request, 'games.html', {'games': games, 'sorted': sorted_by, 'coming_soon': True})

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

def add_product(request, *args, **kwargs):
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień.")
        return redirect('home')

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Zapisano poprawnie")
            return redirect('add_product')

    else:
        form = AddProductForm()

    return render(request, 'add_product.html', {'form': form})

def products_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień.")
        return redirect('home')

    products = Product.objects.all().order_by('name')
    platform = Platform.objects.all()
    producer = Producer.objects.all()
    return render(request, 'products_list.html', {'products': products, 'platform': platform, 'producer': producer})

def edit_product(request, product_id, *args, **kwargs):

    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień.")
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Zapisano poprawnie")
            return redirect('edit_product', product_id=product_id)

    else:
        form = AddProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

@require_POST
def delete_product(request, product_id, *args, **kwargs):
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień.")
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produkt usunięty pomyślnie.")
        return redirect('products_list')

    return redirect('products_list')

def create_cart(request):
    cart = Cart.objects.create(customer=request.user)
    return cart

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.new_or_get_active_cart(request.user)
    cart.add_product(product, quantity=1)

    messages.success(request, f'Produkt <strong>{product.name}</strong> dodany do koszyka.')
    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
def remove_from_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.new_or_get_active_cart(request.user)
    cart.remove_product(product, quantity=1)

    messages.success(request, f'Produkt <strong>{product.name}</strong> usunięty z koszyka.')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart, _ = Cart.objects.new_or_get_active_cart(request.user)
    items = cart.get_items() if cart else []
    return render(request, 'cart.html', {'cart': cart, 'items': items})

def get_user_cart(user):
    try:
        return Cart.objects.get(customer=user, status=Cart.STATUS_NEW)
    except Cart.DoesNotExist:
        return None

def create_order_from_cart(cart, form_data):
    address = f"{form_data['street']} {form_data['house_number']}"
    if form_data.get('apartment_number'):
        address += f"/{form_data['apartment_number']}"
    address += f", {form_data['city']}, {form_data['zip_code']}"

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
    cart.status = cart.STATUS_COMPLETED
    cart.save()

    return order

def place_order(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart = get_user_cart(request.user)
    if not cart or not cart.get_items():
        messages.error(request, "Twój koszyk jest pusty.")
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = create_order_from_cart(cart, form.cleaned_data)
                return render(request, 'order.html', {'order': order})
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart')
    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'form': form, 'cart': cart, 'items': cart.get_items()})

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'history.html', {'orders': orders})

def order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.customer != request.user:
        return HttpResponseForbidden("Nie masz dostępu do tego zamówienia.")

    return render(request, 'order_view.html', {'order': order})