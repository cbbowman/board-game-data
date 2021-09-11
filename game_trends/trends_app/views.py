from hashlib import new
from typing import ContextManager
from django.shortcuts import redirect, render, HttpResponse
from .models import Game, MonthlyPlay, getXMLURLfromGameID, getDataFromXML
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from random import randrange, seed, uniform
from random import randint
from django.contrib.sessions.models import Session
from .models import getIDfromURL

def index(request):
	all_games = Game.objects.all()
	# sorted_by_plays = sorted(all_games, key='play_rank')
	# sorted_by_growth = sorted(all_games, key='growth_rank')
	sorted_by_plays = Game.objects.order_by('-plays')
	sorted_by_growth = Game.objects.order_by('-growth')

	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1

	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank + 1

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()
		

	context = {
		'play_list': sorted_by_plays[:10],
		'growth_list': sorted_by_growth[:10],
		'user_favs': user_favs
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
		request.session['user_id'] = user.id
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
		request.session['user_id'] = new_user.id
		return redirect('/')
	
def user(request, user_id):
	this_user = User.objects.filter(id = request.session['user_id'])[0]
	fav_games = this_user.fav_games.order_by('name')
	sorted_by_plays = fav_games.order_by('plays')
	sorted_by_growth = fav_games.order_by('growth')

	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1

	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank + 1

	context = {
		'fav_games': fav_games
	}
	return render(request, 'profile.html', context)
	
def plays(request):
	sorted_by_plays = Game.objects.order_by('-plays')

	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'play_list': sorted_by_plays[:20],
		'user_favs': user_favs
	}
	return render(request, 'plays.html', context)
	
def growth(request):
	sorted_by_growth = Game.objects.order_by('-growth')

	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank + 1

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'growth_list': sorted_by_growth[:20],
		'user_favs': user_favs
	}
	return render(request, 'growth.html', context)
	
def add(request):
	url = request.POST['url']
	game_id = int(getIDfromURL(url))
	xml_link = getXMLURLfromGameID(game_id)
	game_name, year = getDataFromXML(xml_link)
	new_game = Game.objects.create(bgg_id = game_id, name = game_name, year_published = year, plays = randrange(1, 5000), play_rank = randint(10, 99), growth_rank = randint(10, 99), growth = round(uniform(-0.5,0.5),2))

	# new_game = Game.objects.create(bgg_id = randint(10000, 99999), name = "Game "+ str(randint(10000, 99999)), year_published = randint(1900, 2000), plays = randrange(1, 5000), play_rank = randint(10, 99), growth_rank = randint(10, 99), growth = round(uniform(-0.5,0.5),2))
	
	years = 5
	for this_year in range(2020-years, 2020):
		for this_month in range(1,12):
			new_play = MonthlyPlay.objects.create(game = new_game, month = this_month, year = this_year, plays = randrange(1, 5000))

	return redirect('/')
	
def fav(request, game_id):
	user_id = request.session['user_id']
	this_user = User.objects.filter(id = request.session['user_id'])[0]
	this_game = Game.objects.filter(id = game_id)[0]
	this_user.fav_games.add(this_game)
	url = '/user/' + str(user_id)
	return redirect(url)
	
def unfav(request, game_id):
	user_id = request.session['user_id']
	this_user = User.objects.filter(id = user_id)[0]
	this_game = Game.objects.filter(id = game_id)[0]
	this_user.fav_games.remove(this_game)
	url = '/user/' + str(user_id)
	return redirect(url)
	
def logout_user(request):
	logout(request)
	return redirect('/')