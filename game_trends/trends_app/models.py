from django.db import models
from django.db.models import Avg, FloatField, F
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import time
from datetime import date
import statistics, math

max_size = 500

def deleteErrorGames():
	zeros = Game.objects.filter(plays = 0)
	zeros.delete()
	return

def request(msg, slp=1):
    '''A wrapper to make robust https requests.'''
    status_code = 500  # Want to get a status-code of 200
    while status_code != 200:
        time.sleep(slp)  # Don't ping the server too often
        try:
            r = requests.get(msg)
            status_code = r.status_code
            if status_code != 200:
                print("Server Error! Response Code %i. Retrying..." % (r.status_code))
        except:
            print("An exception has occurred, probably a momentory loss of connection. Waiting one seconds...")
            time.sleep(1)
    return r

def checkTopGames():
	deleteErrorGames()

	for i in range(10):
		checkTopGamesByPage(i)
	return

def checkTopGamesByPage(page):
	url1 = "https://www.boardgamegeek.com/browse/boardgame/page/"+str(page)+"?sort=numvoters&sortdir=desc"
	page = request(url1)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	links1 = table.find_all('a', {'class': 'primary'})
	
	url2 = "https://www.boardgamegeek.com/browse/boardgame/page/"+str(page)
	page = request(url2)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	links2 = table.find_all('a', {'class': 'primary'})

	url_list = []

	for a in range(100):
		url_list.append(links1[a]['href'])
		url_list.append(links2[a]['href'])

	for url in url_list:
		addNewGame(url)
		
	low_ranked_games = Game.objects.all().order_by('-score')
	if len(low_ranked_games)>max_size:
		for i in range(len(low_ranked_games)-max_size):
			if len(low_ranked_games[i].fav_users.all())>0:
				continue
			else:
				low_ranked_games[i].delete()

	return

def addNewGame(url):
	game_id = int(getIDfromURL(url))

	if(len(Game.objects.filter(bgg_id = game_id))):
		return

	if(not checkForPlays(game_id)):
		return

	xml_link = getXMLURLfromGameID(game_id)
	game_name, year, pic, collectible = getDataFromXML(xml_link)

	if(year > 2019):
		return

	if collectible:
		return

	Game.objects.create(bgg_id = game_id, name = game_name, game_pic = pic, year_published = year)
	updateMonthlyPlays(game_id)

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

	todays_date = date.today()
	for game in all_games:
		age = todays_date.year - game.year_published
		game.score = statistics.harmonic_mean([game.play_rank, game.growth_rank, game.h_rank, game.h_growth_rank])/math.log(age,10)
		game.save()
	
	sorted_by_score = all_games.order_by('score')
	for rank in range(len(sorted_by_score)):
		game =  sorted_by_score[rank]
		game.rank = rank + 1
		game.save()

	return

def getIDfromURL(url):
	id = PurePosixPath(
		unquote(
			urlparse(url).path
		)
	).parts[2]
	return id

def checkForPlays(bgg_id):
	url = "https://boardgamegeek.com///xmlapi2/plays?id="+str(bgg_id)
	page = request(url)
	soup = BeautifulSoup(page.content, 'lxml')
	plays = int(soup.find('plays')['total'])
	if plays>0:
		return True
	return False

def getXMLURLfromGameID(gameid):
	url = "https://boardgamegeek.com//xmlapi2/thing?id="+str(gameid)
	return url

def getDataFromXML(url):
	page = request(url)
	soup = BeautifulSoup(page.content, 'lxml')
	name = soup.find('name')
	title = name['value']
	year = int(soup.find('yearpublished')['value'])
	img = str(soup.find('thumbnail').text)
	if soup.find(id='1044', type="boardgamecategory")==None:
		collectible = False
	else:
		collectible = True
	return title, year, img, collectible

def updateMonthlyPlays(game_id):
	if not len(Game.objects.filter(bgg_id=game_id)):
		return
	this_game = Game.objects.filter(bgg_id=game_id)[0]
	
	play_data = getPlayData(game_id)
	for monthly_play in play_data:
		if len(MonthlyPlay.objects.filter(game = this_game, year = monthly_play[0], month = monthly_play[1], plays = monthly_play[2])):
			continue
		if len(this_game.monthly_play.all())>25:
			break
		h_index = getGameHiByMonth(game_id, monthly_play[1], monthly_play[0])
		MonthlyPlay.objects.create(game = this_game, month = monthly_play[1], year = monthly_play[0], plays = monthly_play[2], h=h_index)

	this_game.plays = round(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[:12].aggregate((Avg('plays')))['plays__avg'],1)
	this_game.growth = round(((this_game.plays/(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[13:24].aggregate((Avg('plays')))['plays__avg']))-1),3)*100
	this_game.h = round(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[:12].aggregate((Avg('h')))['h__avg'],1)
	this_game.h_growth = round(((this_game.h/(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[13:24].aggregate((Avg('h')))['h__avg']))-1),3)*100
	this_game.save()

def getPlayData(game_id):
	url =  "https://www.boardgamegeek.com/playsummary/thing/"+str(game_id)
	page = request(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find_all('table')[1]
	rows = table.find_all('tr')

	data = []
	todays_date = date.today()
	for i in range(2,len(rows)-1):
		cells = rows[i].find_all('td')
		year = int(cells[0].get_text(strip=True)[:4])
		minYear=max(Game.objects.filter(bgg_id=game_id)[0].year_published,todays_date.year-3)
		if year<minYear:
			break
		data.append([year, int(cells[0].get_text(strip=True)[-2:]), int(cells[2].get_text(strip=True))])
	return data

def getGameHiByMonth(game_id, month, year):
	url = "https://boardgamegeek.com/playstats/thing/"+str(game_id)+"/"+str(year)+"-"+f"{month:02d}"
	time.sleep(1)
	page = request(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	tds = table.find_all('td', {'class': 'lf'})
	data = []
	for i in range(min([len(tds),25])):
		a = tds[i].find('a')
		data.append(int(a.get_text()))
	return hIndex(data)

def hIndex(list):
	if list == []:
		return 0
	if len(list)==1:
		return 1
	list.sort(reverse=True)
	h_index = 0
	for i in range(len(list)):
		if list[i]>=(i+1):
			h_index=(i+1)
		else:
			return h_index
	return h_index

class Game(models.Model):
	bgg_id = models.PositiveIntegerField(default=0)
	name = models.CharField(max_length=255, default='Game 0')
	game_pic = models.CharField(max_length=255, default='')
	year_published = models.SmallIntegerField(default=0)
	score = models.FloatField(default=0)
	rank = models.PositiveSmallIntegerField(default=0)
	plays = models.FloatField(default=0)
	growth = models.FloatField(default=0)
	h = models.FloatField(default=0)
	h_growth = models.FloatField(default=0)
	play_rank = models.PositiveSmallIntegerField(default=0)
	growth_rank = models.PositiveSmallIntegerField(default=0)
	h_rank = models.PositiveSmallIntegerField(default=0)
	h_growth_rank = models.PositiveSmallIntegerField(default=0)
	fav_users = models.ManyToManyField(User, related_name='fav_games')
	
class MonthlyPlay(models.Model):
	game = models.ForeignKey(Game, related_name='monthly_play', on_delete=CASCADE)
	year = models.PositiveSmallIntegerField()
	month = models.PositiveSmallIntegerField()
	plays = models.PositiveSmallIntegerField()
	h = models.PositiveSmallIntegerField()
