from django.db import models
from django.db.models import Avg, FloatField
from django.db.models.deletion import CASCADE
from django.db.models.functions import Cast
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
import os.path, time

def checkTopGames():
	for i in range(1,10):
		checkTopGamesByPage(i)
	return

def checkTopGamesByPage(page):
	url1 = "https://www.boardgamegeek.com/browse/boardgame/page/"+str(page)+"?sort=numvoters&sortdir=desc"
	time.sleep(1)
	page = requests.get(url1)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	links1 = table.find_all('a', {'class': 'primary'})
	
	url2 = "https://www.boardgamegeek.com/browse/boardgame/page/"+str(page)
	time.sleep(1)
	page = requests.get(url2)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	links2 = table.find_all('a', {'class': 'primary'})

	url_list = []
	for a in range(len(links1)):
		url_list.append(links1[a]['href'])
		url_list.append(links2[a]['href'])
	for url in url_list:
		addNewGame(url)

def addNewGame(url):
	game_id = int(getIDfromURL(url))

	if(len(Game.objects.filter(bgg_id = game_id))):
		return
	if(not checkForPlays(game_id)):
		return
	xml_link = getXMLURLfromGameID(game_id)
	game_name, year, pic = getDataFromXML(xml_link)

	if(year > 2019):
		return

	new_game = Game.objects.create(bgg_id = game_id, name = game_name, game_pic = pic, year_published = year, plays = 0, play_rank = 0, growth_rank = 0, growth = 0)
	
	updateMonthlyPlays(game_id)
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
	time.sleep(1)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'lxml')
	plays = int(soup.find('plays')['total'])
	if plays>0:
		return True
	return False

def getXMLURLfromGameID(gameid):
	url = "https://boardgamegeek.com//xmlapi2/thing?id="+str(gameid)
	return url

def getDataFromXML(url):
	time.sleep(1)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'lxml')
	name = soup.find('name')
	title = name['value']
	year = int(soup.find('yearpublished')['value'])
	img = str(soup.find('thumbnail').text)
	return title, year, img

def updateMonthlyPlays(game_id):
	if not len(Game.objects.filter(bgg_id=game_id)):
		return
	
	this_game = Game.objects.filter(bgg_id=game_id)[0]
	
	play_data = getPlayData(game_id)
	for monthly_play in play_data:
		if len(MonthlyPlay.objects.filter(game = this_game, year = monthly_play[0], month = monthly_play[1], plays = monthly_play[2])):
			continue
		h_index = getGameHiByMonth(game_id, monthly_play[1], monthly_play[0])
		new_play = MonthlyPlay.objects.create(game = this_game, month = monthly_play[1], year = monthly_play[0], plays = monthly_play[2], h=h_index)

	this_game.plays = round(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[:12].aggregate((Avg('plays')))['plays__avg'],1)

	this_game.growth = round(((this_game.plays/(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[13:24].aggregate((Avg('plays')))['plays__avg']))-1),2)*100

	this_game.h = round(MonthlyPlay.objects.filter(game=this_game).order_by('-year','-month')[:12].aggregate((Avg('h')))['h__avg'],1)

	this_game.save()

def getPlayData(game_id):
	url =  "https://www.boardgamegeek.com/playsummary/thing/"+str(game_id)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find_all('table')[1]
	rows = table.find_all('tr')

	data = []
	for i in range(2,len(rows)-1):
		cells = rows[i].find_all('td')
		year = int(cells[0].get_text(strip=True)[:4])
		minYear=max(Game.objects.filter(bgg_id=game_id)[0].year_published,2003)
		if year<minYear:
			break
		data.append([year, int(cells[0].get_text(strip=True)[-2:]), int(cells[2].get_text(strip=True))])
	return data

def getGameHiByMonth(game_id, month, year):
	url = "https://boardgamegeek.com/playstats/thing/"+str(game_id)+"/"+str(year)+"-"+f"{month:02d}"
	time.sleep(1)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	tds = table.find_all('td', {'class': 'lf'})
	data = []
	for i in range(len(tds)):
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
	plays = models.PositiveIntegerField(default=0)
	play_rank = models.PositiveSmallIntegerField(default=0)
	growth_rank = models.PositiveSmallIntegerField(default=0)
	growth = models.SmallIntegerField(default=0)
	h = models.FloatField(default=0)
	h_rank = models.PositiveSmallIntegerField(default=0)
	fav_users = models.ManyToManyField(User, related_name='fav_games')
	
	# def getGameData(self, url):
	# 	self.bgg_id = randint(10000, 99999)
	# 	# self.name = "Game "+ str(randint(10000, 99999))
	# 	self.name = "Tony Game "+ str(randint(10000, 99999))
	# 	self.year_published = randint(1900, 2000)
	# 	# self.play_rank = randint(10, 99)
	# 	self.play_rank = 1
	# 	self.growth_rank = randint(10, 99)
	# 	self.growth = uniform(-0.5,0.5)

class MonthlyPlay(models.Model):
	game = models.ForeignKey(Game, related_name='monthly_play', on_delete=CASCADE)
	year = models.PositiveSmallIntegerField()
	month = models.PositiveSmallIntegerField()
	plays = models.PositiveSmallIntegerField()
	h = models.PositiveSmallIntegerField()
	
	# def getPlayData(self, year, month):
	# 	self.year = year
	# 	self.month = month
	# 	self.plays = randint(10, 10000)
