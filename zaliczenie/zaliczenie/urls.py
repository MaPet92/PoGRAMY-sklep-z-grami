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
from sklep.views import home_page, search, game_page, games, login, register, games_by_platform, incoming_games, account, logout_page, remind_password
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
    path('games/', games, name='games'),
    path('games/coming_soon/', incoming_games, name='incoming_games'),
    path('games/<slug:platform_slug>/', games_by_platform, name='games_by_platform'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
