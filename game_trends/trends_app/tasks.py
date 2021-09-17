from background_task import background
from background_task.models import Task
from .models import addNewGame, checkTopGames

# @background(schedule=5)
# def scrape_games():
#     tasks = Task.objects.filter(verbose_name="scraper")
#     if len(tasks) == 0:
#         checkTopGames()
#         pass
#     else:
#         pass

# @background(schedule=5)
# def add_this_game():
#     addNewGame('https://boardgamegeek.com/boardgame/228504/cat-lady')
#     pass



