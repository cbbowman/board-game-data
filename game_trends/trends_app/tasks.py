from background_task import background
from background_task.models import Task
from .models import checkTopGames

@background(schedule=5)
def scrape_games():
    tasks = Task.objects.filter(verbose_name="scraper")
    if len(tasks) == 0:
        checkTopGames()
    else:
        pass



