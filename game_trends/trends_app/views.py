from typing import ContextManager
from django.shortcuts import redirect, render, HttpResponse
from .models import User, Game, MonthlyPlay, FavoriteGame

def index(request):
	return render(request, 'index.html')
	
def auth(request):
	return render(request, 'auth.html')
	
def login(request):
	return redirect('/')
	
def register(request):
	return redirect('/')
	
def user(request, user_id):
	return render(request, 'profile.html')
	
def plays(request):
	return render(request, 'plays.html')
	
def growth(request):
	return render(request, 'growth.html')
	
def add(request):
	return redirect('/')
	
def fav(request):
	return redirect('/')
	
def unfav(request):
	return redirect('/')
	
def logout(request):
	return redirect('/')