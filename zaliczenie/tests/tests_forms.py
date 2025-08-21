import pytest
pytestmark = pytest.mark.django_db

def test_register_success(client):
    data = {
        'username': 'test',
        'email': 'test@test.pl',
        'password': 'test',
        'password2': 'test',
    }
    response = client.post(reverse('register'), data=data)

    assert response.status_code == 302
    assert response.url == reverse('login')

    messages = list(get_messages(response.wsgi_request))
    assert any("Użytkownik dodany pomyślnie" in str(m) for m in messages)

    from django.contrib.auth.models import User
    user = User.objects.filter(username='test').first()
    assert user is not None
    assert user.email == 'test@test.pl'
    assert user.check_password('test')

def test_register_fail(client):
    #brak_danych
    data = {
        'username': '',
        'email': '',
        'password': '',
        'password2': '',
    }
    response = client.post(reverse('register'), data=data)

    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "To pole jest wymagane." in content

    #różne_hasła
    data = {
        'username': 'test',
        'email': 'test@test.pl',
        'password': 'test',
        'password2': 'test2',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Hasła muszą być takie same" in content

    #nazwa/mail już w bazie
    User.objects.create_user(username='test', email='test@test.pl', password='test')
    data = {
        'username': 'test',
        'email': 'test@test.pl',
        'password': 'test',
        'password2': 'test',
    }
    response = client.post(reverse('register'), data=data)
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Ta nazwa użytkownika jest już zajęta" in content or "Ten e-mail widnieje już w bazie" in content