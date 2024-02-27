from django.db import models
from django.utils.crypto import get_random_string

# pylint: disable=no-member


class Game(models.Model):
    game_id = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        while not self.game_id:
            generated_name = get_random_string(
                10, 'abcdefghijklmnoprstuwxyz0123456789')
            if not Game.objects.filter(game_id=generated_name).exists():
                self.game_id = generated_name
        super(Game, self).save(*args, **kwargs)
