from pandas.core.indexing import is_nested_tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
from urllib.parse import urlparse
import os.path
# from statsmodels.tsa.api import ExponentialSmoothing as HWES
import pandas as pd
from random import randint
from matplotlib import pyplot as plt
# from pandas import datetools
# import statsmodels.tsa.api as tsa
# from statsmodels.tsa.holtwinters import ExponentialSmoothing as HWES



def getIDfromURL(url):
	id = PurePosixPath(
		unquote(
			urlparse(url).path
		)
	).parts[2]
	return id

# print(getIDfromURL('https://www.boardgamegeek.com/boardgame/267991/conspiracy-solomon-gambit'))
# url = 'https://www.boardgamegeek.com/boardgame/267991/conspiracy-solomon-gambit'

# id = PurePosixPath(
# 	unquote(
# 		urlparse(url).path
# 	)
# ).parts[2]

# print(id)

page = requests.get("https://boardgamegeek.com//xmlapi2/thing?id=267991")
soup = BeautifulSoup(page.content, 'lxml')
name = soup.find('name')
title = name['value']
year = soup.find('yearpublished')['value']

page = requests.get("https://www.boardgamegeek.com/playsummary/thing/267991")
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find_all('table')[1]
rows = table.find_all('tr')

data = []
for i in range(1,len(rows)-1):
	cells = rows[i].find_all('td')
	data.append([cells[0].get_text(strip=True)[:4], cells[0].get_text(strip=True)[-2:], cells[2].get_text(strip=True)])
	# data.append([cells[0].get_text(strip=True), cells[2].get_text(strip=True)])


url = "https://www.boardgamegeek.com/browse/boardgame"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('table')
# rows = table.find_all('tr')
links = table.find_all('a', {'class': 'primary'})
url_list = []
for a in range(len(links)):
	url_list.append(links[a]['href'])

play_counts = []

for i in range(100):
	play_counts.insert(0,[str(2020 - (i // 12))+"-"+f'{((i % 12) + 1):02d}', randint(1,1000)])
# print(play_counts)
df = pd.DataFrame(play_counts)

# print(df.head())
df.index.freq = 'MS'
# model = HWES(df, seasonal_periods=12, trend='mul', seasonal='mul')
# level = model.level()
# print(level)

# print(url_list)


# tds = soup.find_all('td')[1:5]
# for i in enumerate(tds, 1):
# 	date = i.text

# print(tds)

# # print(list(soup.children))
# # body = list(html.children)[3]
# # p = list(body.children)[1]
# # p.get_text()

# # print(p)