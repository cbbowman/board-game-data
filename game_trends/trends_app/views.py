from os import stat
from django.shortcuts import redirect, render
from .models import Game, addNewGame, checkTopGames, deleteErrorGames, getIDfromURL
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db.models import F, Func
# from .tasks import scrape_games
# from background_task import background
# from background_task.models import Task
from .models import addNewGame, checkTopGames, updateMonthlyPlays, FloatField
import statistics
from datetime import date
import math

# @background(schedule=5)
# def scrape_games():
#     tasks = Task.objects.filter(verbose_name="scraper")
#     if len(tasks) == 0:
#         checkTopGames()
#         pass
#     else:
#         pass

def delete_all(request):
	Game.objects.all().delete()
	return redirect('/')

def update(request):
	all_games = Game.objects.all()

	for game in all_games:
		game.monthly_play.all().delete()
		updateMonthlyPlays(game.bgg_id)
	return redirect('/')

def index(request):
	# scrape_games(repeat = 300, repeat_until = None, verbose_name="scraper")

	sorted_by_plays = Game.objects.order_by('-plays')
	sorted_by_h = Game.objects.order_by('-h')
	
	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'play_list': sorted_by_plays[:10],
		'h_list': sorted_by_h[:10],
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

	context = {
		'fav_games': fav_games
	}
	return render(request, 'profile.html', context)
	
def game(request, game_id):
	this_game = Game.objects.filter(id = game_id)[0]

	context = {
		'game': this_game
	}
	return render(request, 'game.html', context)
	
def overall(request):

	all_games = Game.objects.all().exclude(plays = 0)

	overall_games = all_games.order_by('rank')

	user_favs = {}
	
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'overall_list': overall_games,
		'user_favs': user_favs
	}
	return render(request, 'overall.html', context)
	
def players(request):
	all_games = Game.objects.all().exclude(plays = 0)
	sorted_by_plays = all_games.order_by('-plays')

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'play_list': sorted_by_plays,
		'user_favs': user_favs
	}
	return render(request, 'plays.html', context)
	
def player_growth(request):
	all_games = Game.objects.all().exclude(plays = 0)
	sorted_by_growth = all_games.order_by('-growth')

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'growth_list': sorted_by_growth,
		'user_favs': user_favs
	}
	return render(request, 'growth.html', context)
	
def h(request):
	all_games = Game.objects.all().exclude(plays = 0)
	sorted_by_h = all_games.order_by('-h')

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'h_list': sorted_by_h,
		'user_favs': user_favs
	}
	return render(request, 'h_index.html', context)
	
def h_growth(request):
	all_games = Game.objects.all().exclude(plays = 0)
	sorted_by_h_growth = all_games.order_by('-h_growth')

	user_favs = {}
	if request.user.is_authenticated:
		this_user = User.objects.filter(id = request.session['user_id'])[0]
		user_favs = this_user.fav_games.all()

	context = {
		'h_growth_list': sorted_by_h_growth,
		'user_favs': user_favs
	}
	return render(request, 'h_growth.html', context)
	
def add(request):
	url = request.POST['url']
	addNewGame(url)
	if not len(Game.objects.filter(bgg_id=getIDfromURL(url))):
		return redirect('/')
	new_game = Game.objects.filter(bgg_id=getIDfromURL(url))[0]
	return redirect('/fav/'+f'{new_game.id}')

def top(request):
	checkTopGames()
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
