from django.urls import re_path
from channels.routing import URLRouter
from . import consumers

urlpatterns = [
    re_path(r"ws/game/(?P<game_id>\w+)/$", consumers.GameConsumer.as_asgi(), name = "ws_game"),
]

websockets = URLRouter(urlpatterns)