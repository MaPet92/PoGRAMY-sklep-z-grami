from .models import Cart

def cart_counter(request):
    quantity = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(customer=request.user, status=Cart.STATUS_NEW).first()
        if cart:
            quantity = cart.get_total_quantity()

    return {
        'cart_quantity': quantity
    }

def cart(request):
    cart = get_cart_from_session_or_db(request)  # Twój kod pobierający koszyk
    return {'cart': cart}