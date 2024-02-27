from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("create/", views.create, name="create"),
    path("invite/<str:game_id>/", views.game_invite, name="game"),
    path('game/', views.game_join, name='game_url'),
]
