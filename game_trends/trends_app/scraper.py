import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath
from urllib.parse import urlparse
import os.path

def getIDfromURL(url):
	id = PurePosixPath(
		unquote(
			urlparse(url).path
		)
	).parts[2]
	return id

print(getIDfromURL('https://www.boardgamegeek.com/boardgame/267991/conspiracy-solomon-gambit'))
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
	data.append([cells[0].get_text(strip=True), cells[2].get_text(strip=True)])
	# print(rows[i])

print(data)

# tds = soup.find_all('td')[1:5]
# for i in enumerate(tds, 1):
# 	date = i.text

# print(tds)

# # print(list(soup.children))
# # body = list(html.children)[3]
# # p = list(body.children)[1]
# # p.get_text()

# # print(p)