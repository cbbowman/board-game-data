from django.urls import path
from . import views

urlpatterns = [
    path('', views.index), # main page showing growth and plays tables
    path('update', views.update),
    path('delete_all', views.delete_all),
    path('auth', views.auth), # page showing login and registration forms
    path('login', views.login_user), # route that logs the user in
    path('register', views.register), # route that creates a new user and logs them in
    path('user/<int:user_id>', views.user), # page showing user's favorite games with stats
    path('game/<int:game_id>', views.game), # page showing stats for a game
    path('overall', views.overall), # page showing table of best overall games
    path('players', views.players), # page showing table of games with most plays
    path('growth', views.player_growth), # page showing table of games with most play growth
    path('h', views.h), # page showing table of games with high h-index
    path('h_growth', views.h_growth), # page showing table of games with high h-index
    path('add', views.add), # page that allows the user to add a new game to be tracked
    path('top', views.top), #check the BGG top games list for new games
    path('fav/<int:game_id>', views.fav), # route that adds a game to the users favorites
    path('unfav/<int:game_id>', views.unfav), # route that removes a game from the users favorites
    path('logout', views.logout_user), # route that logs the user out
	]