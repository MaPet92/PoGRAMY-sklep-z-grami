import pytest
pytestmark = pytest.mark.django_db

from django.urls import reverse
from sklep.models import Product, Genre, Platform, Producer
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile

###

def test_home_page_status_code(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200

def test_home_page_games_lists(client):
    response = client.get(reverse('home'))
    context = response.context
    assert 'random_promo_games' in context
    assert 'random_coming_games' in context
    assert 'random_pc_games' in context
    assert 'random_playstation_games' in context
    assert 'random_xbox_games' in context
    assert 'random_switch_games' in context
    for key in ['random_promo_games', 'random_coming_games', 'random_pc_games', 'random_playstation_games', 'random_xbox_games', 'random_switch_games']:
        assert isinstance(context[key], list)

def test_home_page_five_games(client):
    response = client.get(reverse('home'))
    context = response.context
    for key in ['random_promo_games', 'random_coming_games', 'random_pc_games', 'random_playstation_games', 'random_xbox_games', 'random_switch_games']:
        assert len(context[key]) <= 5

def test_create_product(client):
    genre = Genre.objects.create(name='Test')
    platform = Platform.objects.create(name='Test')
    producer = Producer.objects.create(name='Test')

    product = Product.objects.create(
        name='Test',
        price=100,
        platform=platform,
        producer=producer,
        description='Test',
        year_of_premiere=2025,
        stock=10,
        promotion=True,
        promo_price=50)
    product.genres.add(genre)

    assert Product.objects.count() == 1
    saved_product = Product.objects.first()
    assert saved_product.name == 'Test'
    assert saved_product.price == 100
    assert genre in saved_product.genres.all()
    assert saved_product.platform == platform
    assert saved_product.producer == producer
    assert saved_product.description == 'Test'
    assert saved_product.year_of_premiere == 2025
    assert saved_product.stock == 10
    assert saved_product.promo_price == 50
    assert saved_product.promotion == True

def test_coming_games_page(client):
    image = SimpleUploadedFile(name='test.jpg', content=b'\x47\x49\x46\x38\x39\x61', content_type='image/gif')
    game = Product.objects.create(
        name='Test',
        price=100,
        platform=Platform.objects.create(name='Test'),
        producer=Producer.objects.create(name='Test'),
        description='Test',
        year_of_premiere=2025,
        stock=10,
        promotion=True,
        promo_price=50,
        is_published=False,
        image=image)
    response = client.get(reverse('home'))
    coming_games = response.context['random_coming_games']
    assert game in coming_games
    assert all(not g.is_published for g in coming_games)

def test_logout_page(client):
    user = User.objects.create_user(username='test', password='test')
    client.login(username='test', password='test')

    response = client.get(reverse('home'))
    assert response.wsgi_request.user.is_authenticated

    response = client.get(reverse('logout_page'))

    assert response.status_code == 302
    assert response.url == reverse('home')

    response = client.get(reverse('home'))
    assert not response.wsgi_request.user.is_authenticated

def test_game_page(client):
    platform = Platform.objects.create(name='Test', slug='test')
    producer = Producer.objects.create(name='Test', slug='test')
    image = SimpleUploadedFile(name='test.jpg', content=b'\x47\x49\x46\x38\x39\x61', content_type='image/gif')
    game = Product.objects.create(
        name='Test',
        slug='test',
        price=10,
        stock=10,
        promotion=True,
        promo_price=5,
        is_published=True,
        platform=platform,
        producer=producer,
        description='Test',
        year_of_premiere=2025,
        image=image,
    )

    response = client.get(reverse('game_page', args=[game.slug]))
    assert response.status_code == 200
    assert 'game.html' in (t.name for t in response.templates)

def test_not_found_game_page(client):
    response = client.get(reverse('game_page', args=['test']))
    assert response.status_code == 404

def test_create_game():
    platform = Platform.objects.create(name='Test')
    producer = Producer.objects.create(name='Test')
    image = SimpleUploadedFile(name='test.jpg', content=b'\x47\x49\x46\x38\x39\x61', content_type='image/gif')

    game = Product.objects.create(
        name='Test',
        price=100,
        platform=platform,
        producer=producer,
        description='Test',
        year_of_premiere=2025,
        image=image,
        stock=0,
        promotion=False,
        promo_price=0,
        is_published=True,
    )

    game.refresh_from_db()
    saved_game = Product.objects.first()

    assert Product.objects.count() == 1
    assert saved_game.name == 'Test'
    assert saved_game.price == 100
    assert saved_game.platform == platform
    assert saved_game.producer == producer
    assert saved_game.description == 'Test'
    assert saved_game.year_of_premiere == 2025
    assert saved_game.stock == 0
    assert saved_game.promo_price == 0

def test_remind_password(client):
    response = client.post(reverse('remind_password'))
    assert response.status_code == 200
    assert 'id="id_email"' in response.content.decode('utf-8')
    assert 'name="email"' in response.content.decode('utf-8')

def test_remind_password_wrong_email(client):
    response = client.post(reverse('remind_password'), data={'email': 'wrong@email.com'})
    assert response.status_code == 302
    assert response.url == reverse('remind_password')

def test_register(client):
    response = client.get(reverse('register'))
    assert response.status_code == 200
    assert 'id="id_username"' in response.content.decode('utf-8')
    assert 'name="username"' in response.content.decode('utf-8')
    assert 'id="id_email"' in response.content.decode('utf-8')
    assert 'name="email"' in response.content.decode('utf-8')
    assert 'id="id_password"' in response.content.decode('utf-8')
    assert 'name="password"' in response.content.decode('utf-8')
    assert 'id="id_password2"' in response.content.decode('utf-8')
    assert 'name="password2"' in response.content.decode('utf-8')

def test_search(client):
    image = SimpleUploadedFile(name='test.jpg', content=b'\x47\x49\x46\x38\x39\x61', content_type='image/gif')
    game = Product.objects.create(
        name='Test',
        price=100,
        platform=Platform.objects.create(name='Test'),
        producer=Producer.objects.create(name='Test'),
        description='Test',
        year_of_premiere=2025,
        stock=10,
        promotion=True,
        promo_price=50,
        is_published=True,
        image=image)

    #z_ustalonym_query
    response = client.get(reverse('search'), {'q': 'Test'})
    assert response.status_code == 200
    assert 'games' in response.context
    assert game in response.context['games']

    #bez_ustalonego_query
    response = client.get(reverse('search'), {'q': ''})
    assert response.status_code == 200
    assert 'games' in response.context
    assert game in response.context['games']

    #z_nieistniejacym_query
    response = client.get(reverse('search'), {'q': 'Test2'})
    assert response.status_code == 200
    assert 'games' in response.context
    assert game not in response.context['games']