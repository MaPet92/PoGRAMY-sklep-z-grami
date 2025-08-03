import random
from django.db.models import Case, When, F, DecimalField
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from sklep.models import Product, Platform, Genre, Producer, Cart, CartItem
from sklep.forms import LoginForm, RegisterForm, RemindPasswordForm, EditAccountForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.templatetags.static import static

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

def search(request):
    query = request.GET.get('q')
    return render(request, 'search.html', {'query': query})

def account(request):
    return render(request, 'account.html')

def logout_page(request):
    logout(request)
    return redirect('home')

def game_page(request, slug):
    game = get_object_or_404(Product, slug=slug)
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