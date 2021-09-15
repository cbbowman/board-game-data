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
import random

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
	checkTopGamesByPage(10)
	# numGames = Game.objects.all().count()
	# while Game.objects.all().count()<(2*numGames):
	# 	pages=range(1,100)
	# 	pageWeights=[]
	# 	for i in range(0,99):
	# 		pageWeights.append(100-i)
	# 	# checkTopGamesByPage(random.choices(pages,weights=pageWeights, k=1)[0])
	# 	checkTopGamesByPage(2)
	# 	#checkTopGamesByPage(1)
	# 	#checkTopGamesByPage(random.randint(2,100))

	# 	sorted_by_plays = Game.objects.order_by('-plays')
	# 	sorted_by_growth = Game.objects.order_by('-growth')
	# 	sorted_by_h = Game.objects.order_by('-h')

	# 	for rank in range(len(sorted_by_plays)):
	# 		game =  sorted_by_plays[rank]
	# 		if game.plays == 0:
	# 			game.play_rank = rank +1
	# 			#game.play_rank = 0
	# 		else:
	# 			game.play_rank = rank + 1
	# 		game.save()

	# 	for rank in range(len(sorted_by_growth)):
	# 		game =  sorted_by_growth[rank]
	# 		if game.growth == 0:
	# 			#game.growth_rank = 0
	# 			game.growth_rank = rank +1
	# 		else:
	# 			game.growth_rank = rank + 1
	# 		game.save()

	# 	for rank in range(len(sorted_by_h)):
	# 		game =  sorted_by_h[rank]
	# 		if game.h == 0:
	# 			game.h_rank = rank +1
	# 			#game.h_rank = 0
	# 		else:
	# 			game.h_rank = rank + 1
	# 		game.save()
		
	# 	low_ranked_games = Game.objects.all().annotate(total_rank=F('play_rank')+F('growth_rank')+F('h_rank')).order_by('-total_rank')

	# 	for i in range(len(low_ranked_games)/2):
	# 		if low_ranked_games[i].fav_users.all().count()>0:
	# 			continue
	# 		else:
	# 			low_ranked_games[i].delete()
	#return checkTopGames()
	return

def checkTopGamesByPage(page):
	url1 = "https://www.boardgamegeek.com/browse/boardgame/page/"+str(page)+"?sort=numvoters&sortdir=desc"
	#time.sleep(1)
	page = request(url1)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	links1 = table.find_all('a', {'class': 'primary'})
	
	url2 = "https://www.boardgamegeek.com/browse/boardgame/page/"+str(page)
	#time.sleep(1)
	page = request(url2)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	links2 = table.find_all('a', {'class': 'primary'})

	url_list = []
	#for a in range(12):
	for a in range(100):
		url_list.append(links1[a]['href'])
		url_list.append(links2[a]['href'])
	# addNewGame[url_list[random.randint(1,100)]]
	addNewGame['https://boardgamegeek.com/boardgame/205322/oregon-trail-card-game']
	# addNewGame[url_list[10]]
	# for url in url_list:
		#addNewGame(url)
	#addNewGame(url_list[random.randint(1,len(url_list))])
	return

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
	#time.sleep(1)
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
	#time.sleep(1)
	page = request(url)
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
	page = request(url)
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
	plays = models.PositiveIntegerField(default=0)
	play_rank = models.PositiveSmallIntegerField(default=0)
	growth_rank = models.PositiveSmallIntegerField(default=0)
	growth = models.SmallIntegerField(default=0)
	h = models.FloatField(default=0)
	h_rank = models.PositiveSmallIntegerField(default=0)
	fav_users = models.ManyToManyField(User, related_name='fav_games')
	
class MonthlyPlay(models.Model):
	game = models.ForeignKey(Game, related_name='monthly_play', on_delete=CASCADE)
	year = models.PositiveSmallIntegerField()
	month = models.PositiveSmallIntegerField()
	plays = models.PositiveSmallIntegerField()
	h = models.PositiveSmallIntegerField()
