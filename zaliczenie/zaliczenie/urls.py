"""
URL configuration for zaliczenie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sklep.views import OrderView, CartView, ProductsAdminView, GamesView, home_page, search, game_page, login, register, account, logout_page, remind_password
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_page, name='home'),
    path('search/', search, name='search'),
    path('account/', account, name='account'),
    path('logout/', logout_page, name='logout_page'),
    path('remind_password/', remind_password, name='remind_password'),
    path('admin/', admin.site.urls, name='admin'),
    path('game/<slug:slug>/', game_page, name='game_page'),
    path('games/', GamesView.as_view(), name='games'),
    path('games/coming_soon/', GamesView.as_view(coming_soon=True), name='incoming_games'),
    path('games/platform/<slug:platform_slug>/', GamesView.as_view(filter_by='platform'), name='games_by_platform'),
    path('games/producer/<slug:producer_slug>/', GamesView.as_view(filter_by='producer'), name='games_by_producer'),
    path('games/genre/<slug:genre_slug>/', GamesView.as_view(filter_by='genre'), name='games_by_genre'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('panel/add_product/', ProductsAdminView.as_view(action='add'), name='add_product'),
    path('panel/edit_product/<int:product_id>/', ProductsAdminView.as_view(action='edit'), name='edit_product'),
    path('panel/delete_product/<int:product_id>/', ProductsAdminView.as_view(action='delete'), name='delete_product'),
    path('panel/products_list/', ProductsAdminView.as_view(action='list'), name='products_list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', CartView.as_view(), {'action': 'add'}, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', CartView.as_view(), {'action': 'remove'}, name='remove_from_cart'),
    path('order/', OrderView.as_view(), {'action': 'place'}, name='place_order'),
    path('order/history/', OrderView.as_view(), {'action': 'history'}, name='order_history'),
    path('order/<int:order_id>/', OrderView.as_view(), {'action': 'view'}, name='order_view')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
