from django.shortcuts import render
from django.utils.crypto import get_random_string
from .models import Game
from .utils import channels_reverse

card_values = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, "?", "☕"]


def index(request):
    context = {}
    return render(request, 'index.html', context)


def create(request):
    password = request.GET.get('password', '')
    
    game = Game(password=password)
    game.save()

    url = channels_reverse('ws_game', kwargs={'game_id': game.game_id})

    context = {
        "game_id": game.game_id,
        "is_owner": True,
        "values": card_values,
        "url": url,
    }

    return render(request, "game.html", context)


def game_join(request):
    game_id = request.GET.get('game_id', '')
    password = request.GET.get('password', '')
    url = channels_reverse('ws_game', kwargs={'game_id': game_id})

    try:
        room = Game.objects.get(game_id=game_id)
        if room.password and len(room.password) > 0 and room.password != password:
            return render(request, "index.html", {})
    except Game.DoesNotExist:
        return render(request, "index.html", {})

    context = {
        "game_id": game_id,
        "is_owner": False,
        "values": card_values,
        "url": url,
    }

    return render(request, "game.html", context)


def game_invite(request, game_id):
    context = {
        "game_id": game_id,
    }
    return render(request, 'index.html', context)
