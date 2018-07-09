"""battlesheep URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from battlesheep import views


urlpatterns = [
    path('', views.home, name='home'),
    path('games/', views.GameListView.as_view(), name='games'),
    path('games/random/', views.GameRandomView.as_view(), name='new_random_game'),
    path('games/<game_id>/', views.GameDetailView.as_view(), name='game'),
    path('games/<game_id>/board/', views.GameBoardView.as_view(), name='game_board'),

    path('games/<game_id>/ships/', views.ShipListView.as_view(), name='ships'),
    path('games/<game_id>/ships/<ship_id>/', views.ShipDetailView.as_view(), name='ship'),

    path('games/<game_id>/shots/', views.ShotListView.as_view(), name='shots'),
    path('games/<game_id>/shots/<shot_id>/', views.ShotDetailView.as_view(), name='shot'),

    path('admin/', admin.site.urls),
]
