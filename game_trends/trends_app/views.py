from hashlib import new
from random import randint, randrange
from typing import ContextManager
from django.shortcuts import redirect, render, HttpResponse
from .models import Game, MonthlyPlay, FavoriteGame
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from random import randrange, seed, uniform
from random import randint

def index(request):
	context = {
		'all_games': Game.objects.all()
	}

	return render(request, 'index.html', context)
	
def auth(request):
	if request.user.is_authenticated:
		return redirect('/')
	return render(request, 'auth.html')
	
def login_user(request):
	this_username = request.POST['username']
	this_password = request.POST['password']
	user = authenticate(request, username=this_username, password=this_password)
	if user is not None:
		login(request, user)
		return redirect('/')
	else:
		messages.error(request, "Incorrect username or password.")
		return redirect('/auth')
	
def register(request):
	this_username = request.POST['username']
	this_password = str(request.POST['password'])

	find_user = User.objects.filter(username=this_username)
	if len(find_user)>0:
		messages.error(request, "Username already in use.")
		return redirect("/auth")
	else:
		new_user = User.objects.create(username = this_username)
		new_user.set_password(this_password)
		new_user.save()
		login(request, new_user)
		return redirect('/')
	
def user(request, user_id):
	return render(request, 'profile.html')
	
def plays(request):
	all_games = Game.objects.all()
	context = {
		'all_games': all_games
	}
	return render(request, 'plays.html', context)
	
def growth(request):
	all_games = Game.objects.all()
	context = {
		'all_games': all_games
	}	
	return render(request, 'growth.html', context)
	
def add(request):
	new_game = Game.objects.create(bgg_id = randint(10000, 99999), name = "Game "+ str(randint(10000, 99999)), year_published = randint(1900, 2000), plays = randrange(1, 5000), play_rank = randint(10, 99), growth_rank = randint(10, 99), growth = round(uniform(-0.5,0.5),2))
	# new_game.getGame(request.POST['url'])
	
	years = 5
	for this_year in range(2020-years, 2020):
		for this_month in range(1,12):
			new_play = MonthlyPlay.objects.create(game = new_game, month = this_month, year = this_year, plays = randrange(1, 5000))

	return redirect('/')
	
def fav(request):
	return redirect('/')
	
def unfav(request):
	return redirect('/')
	
def logout_user(request):
	logout(request)
	return redirect('/')