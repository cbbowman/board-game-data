from django.db import models
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User

# Create your models here.
class Game(models.Model):
	bgg_id = models.PositiveIntegerField
	name = models.CharField(max_length=255)
	year_published = models.PositiveSmallIntegerField
	play_rank = models.PositiveSmallIntegerField
	growth_rank = models.PositiveSmallIntegerField

class MonthlyPlay(models.Model):
	game = models.ManyToManyField(Game, on_delete=models.CASCADE, related_name='monthly_play')
	year = models.PositiveSmallIntegerField
	month = models.PositiveSmallIntegerField
	plays = models.PositiveSmallIntegerField

class FavoriteGame():
	game = models.ManyToManyField(User, on_delete=models.CASCADE, related_name='favorites')