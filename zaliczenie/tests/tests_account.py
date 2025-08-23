import pytest
pytestmark = pytest.mark.django_db

from django.urls import reverse
from django.contrib.messages import get_messages
from sklep.models import Product, Genre, Platform, Producer
from django.contrib.auth.models import User

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

def test_register(client):
    data = {
        'email': 'test@test.pl',
        'username': 'test',
        'password': 'test',
        'password2': 'test',
    }
    response = client.post(reverse('register'), data=data)

    assert response.status_code == 302
    assert response.url == reverse('login')

    user = User.objects.filter(username='test').first()
    assert user is not None
    assert user.email == 'test@test.pl'
    assert user.check_password('test') is True

def test_remind_password(client):

    #dla_nieistniejącego_uzytkownika

    response = client.post(reverse('remind_password'), data={'email': 'test@test.pl'}, follow=True)
    assert response.status_code == 200
    assert response.resolver_match.view_name == 'remind_password'
    messages = list(get_messages(response.wsgi_request))
    assert any("Nie znaleziono użytkownika o podanym e-mailu" in str(m) for m in messages)

    #dla_istniejącego_uzytkownika

    User.objects.create_user(email='test@test.pl', username='test', password='test')
    response = client.post(reverse('remind_password'), data={'email': 'test@test.pl'}, follow=True)
    assert response.status_code == 200
    assert response.resolver_match.view_name == 'remind_password'
    messages = list(get_messages(response.wsgi_request))
    assert any("Link do zresetowania hasła wysłany na podany e-mail" in str(m) for m in messages)

def test_account(client):

    #z_zalogowanym_uzytkownikiem

    user = User.objects.create_user(username='test', password='test')
    client.login(username='test', password='test')
    response = client.get(reverse('account'))
    assert response.status_code == 200
    client.logout()

    #bez_zalogowanego_uzytkownika

    response = client.get(reverse('account'))
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))