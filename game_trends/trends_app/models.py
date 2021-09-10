from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User, UserManager
from random import randrange, seed, uniform
from random import randint
import requests

class Game(models.Model):
	bgg_id = models.PositiveIntegerField(default=0)
	name = models.CharField(max_length=255, default='Game 0')
	year_published = models.PositiveSmallIntegerField(default=0)
	plays = models.PositiveIntegerField(default=0)
	play_rank = models.PositiveSmallIntegerField(default=0)
	growth_rank = models.PositiveSmallIntegerField(default=0)
	growth = models.FloatField(default=0)
	fav_users = models.ManyToManyField(User, related_name='fav_games')
	# objects = GameManager()
	
	# def getGameData(self, url):
	# 	self.bgg_id = randint(10000, 99999)
	# 	self.name = "Game "+ str(randint(10000, 99999))
	# 	self.year_published = randint(1900, 2000)
	# 	self.play_rank = randint(10, 99)
	# 	self.growth_rank = randint(10, 99)
	# 	self.growth = uniform(-0.5,0.5)

class MonthlyPlay(models.Model):
	game = models.ForeignKey(Game, related_name='monthly_play', on_delete=CASCADE)
	year = models.PositiveSmallIntegerField()
	month = models.PositiveSmallIntegerField()
	plays = models.PositiveSmallIntegerField()
	
	# def getPlayData(self, year, month):
	# 	self.year = year
	# 	self.month = month
	# 	self.plays = randint(10, 10000)
