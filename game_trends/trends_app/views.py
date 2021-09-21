from os import stat
from django.shortcuts import redirect, render
from .models import Game, addNewGame, checkTopGames, deleteErrorGames, getIDfromURL
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db.models import F, Func
# from .tasks import scrape_games
from background_task import background
# from background_task.models import Task
from .models import addNewGame, checkTopGames, updateMonthlyPlays, FloatField
import statistics

@background(schedule=5)
def scrape_games():
    tasks = Task.objects.filter(verbose_name="scraper")
    if len(tasks) == 0:
        checkTopGames()
        pass
    else:
        pass

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
	scrape_games(repeat = 300, repeat_until = None, verbose_name="scraper")

	sorted_by_plays = Game.objects.order_by('-plays')
	sorted_by_growth = Game.objects.order_by('-growth')
	sorted_by_h = Game.objects.order_by('-h')
	sorted_by_h_growth = Game.objects.order_by('-h_growth')

	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1
		game.save()

	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank +1
		game.save()

	for rank in range(len(sorted_by_h)):
		game =  sorted_by_h[rank]
		game.h_rank = rank +1
		game.save()

	for rank in range(len(sorted_by_h_growth)):
		game =  sorted_by_h_growth[rank]
		game.h_growth_rank = rank +1
		game.save()
	
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
	sorted_by_plays = fav_games.order_by('plays')
	sorted_by_growth = fav_games.order_by('growth')

	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1
		game.save()

	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank + 1
		game.save()

	context = {
		'fav_games': fav_games
	}
	return render(request, 'profile.html', context)
	
def overall(request):

	all_games = Game.objects.all().exclude(plays = 0)

	sorted_by_plays = all_games.order_by('-plays')
	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1
		game.save()

	sorted_by_growth = all_games.order_by('-growth')
	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank + 1
		game.save()
		
	sorted_by_h = all_games.order_by('-h')
	for rank in range(len(sorted_by_h)):
		game =  sorted_by_h[rank]
		game.h_rank = rank + 1
		game.save()

	sorted_by_h_growth = all_games.order_by('-h_growth')
	for rank in range(len(sorted_by_h_growth)):
		game =  sorted_by_h_growth[rank]
		game.h_growth_rank = rank + 1
		game.save()

	for game in all_games:
		game.score = statistics.harmonic_mean([game.play_rank, game.growth_rank, game.h_rank, game.h_growth_rank])
		game.save()
	
	sorted_by_score = all_games.order_by('score')
	for rank in range(len(sorted_by_score)):
		game =  sorted_by_score[rank]
		game.rank = rank + 1
		game.save()

	overall_games = sorted_by_score

	# overall_games = all_games.annotate(total_rank=F('play_rank')+F('growth_rank')+F('h_rank')+F('h_growth_rank')).order_by('total_rank')

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

	for rank in range(len(sorted_by_plays)):
		game =  sorted_by_plays[rank]
		game.play_rank = rank + 1
		game.save()

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

	for rank in range(len(sorted_by_growth)):
		game =  sorted_by_growth[rank]
		game.growth_rank = rank + 1
		game.save()

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

	for rank in range(len(sorted_by_h)):
		game =  sorted_by_h[rank]
		game.h_rank = rank + 1
		game.save()

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

	for rank in range(len(sorted_by_h_growth)):
		game =  sorted_by_h_growth[rank]
		game.h_growth_rank = rank + 1
		game.save()

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
