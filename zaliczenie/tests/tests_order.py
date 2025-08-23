import pytest
pytestmark = pytest.mark.django_db

from django.contrib.auth.models import User
from sklep.models import Order, Cart, Product, CartItem, Platform, OrderItem
from sklep.views import OrderView


def test_create_order_from_cart():
    user = User.objects.create_user(username='test', password='test')
    view = OrderView()

    # nie_istnieje_order
    assert view.get_user_cart(user) is None

    # gdy_istnieje_order
    platform = Platform.objects.create(name='Test')
    p1 = Product.objects.create(name='Test', price=100, promo_price=50, promotion=True, stock=5, year_of_premiere=2025, platform=platform)
    p2 = Product.objects.create(name='Test2', price=150, promotion=False, stock=5, year_of_premiere=2025, platform=platform)
    cart = Cart.objects.create(customer=user, status=Cart.STATUS_NEW)
    CartItem.objects.create(cart=cart, product=p1, quantity=1)
    CartItem.objects.create(cart=cart, product=p2, quantity=2)
    assert view.get_user_cart(user) == cart

    form_data = {
        'first_name': 'test',
        'last_name': 'test',
        'street': 'Test',
        'house_number': '1',
        'apartment_number': '',
        'city': 'Test',
        'zip_code': '12345',
        'email': 'test@test.pl',
        'phone': '123456789',
        'status': Order.STATUS_NEW,
        'payment_method': Order.PAYMENT_CASH_ON_DELIVERY,
    }
    order = view.create_order_from_cart(cart, form_data)
    assert Order.objects.filter(id=order.id).exists()
    order.refresh_from_db()
    assert order.status == Order.STATUS_NEW
    assert order.customer == user

    p1.refresh_from_db()
    p2.refresh_from_db()
    assert p1.stock == 4
    assert p2.stock == 3

    cart.refresh_from_db()
    assert cart.cartitem_set.count() == 0
    assert cart.status == Cart.STATUS_COMPLETED