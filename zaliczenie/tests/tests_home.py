import pytest
pytestmark = pytest.mark.django_db

from django.urls import reverse
from sklep.models import Product, Genre, Platform, Producer
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