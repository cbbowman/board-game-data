# from .models import Game, MonthlyPlay
import requests
from bs4 import BeautifulSoup

def hIndex(list):
	if list == []:
		return 0
	list.sort(reverse=True)
	# print(list)
	h_index = 0
	for i in range(len(list)):
		# print([list[i],i])
		if list[i] >= i+1:
			h_index=i+1
			# print(h_index)
		else:
			return h_index
	return h_index

def getGameHiByMonth(game_id, month, year):
	# if not len(Game.objects.filter(bgg_id=game_id)):
	# 	return
	# this_game = Game.objects.filter(bgg_id=game_id)[0]
	# plays = MonthlyPlay.objects.filter(game = this_game)

	url = "https://boardgamegeek.com/playstats/thing/"+str(game_id)+"/"+str(year)+"-"+f"{month:02d}"

	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	table = soup.find('table')
	# rows = table.find_all('tr')
	tds = table.find_all('td', {'class': 'lf'})
	# values = tds.find_all('a')

	data = []
	for i in range(len(tds)):
		a = tds[i].find('a')
		data.append(int(a.get_text()))
	
	# print(url)
	return hIndex(data)

print(getGameHiByMonth(174430,9,2021))