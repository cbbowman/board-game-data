import requests
from bs4 import BeautifulSoup

page = requests.get("https://www.boardgamegeek.com/playsummary/thing/432")

soup = BeautifulSoup(page.content, 'html.parser')

html = list(soup.children)[2]