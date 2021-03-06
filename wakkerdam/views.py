from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from wakkerdam.forms import CreateGameForm, NumberOfWolvesForm
from wakkerdam.functions import distribute_roles, number_of_wolves
from wakkerdam.models import Game, Player
from wakkerdam.forms import JoinPlayerForm
from wwwcie.settings import MINIMUM_STARTING_PLAYERS
from random import sample


def all_games(request):
	"""
		Shows all available Wakkerdam games...
	"""
	open_games = Game.objects.filter(state = 'join')
	return render(request, 'all_games.html', {
		'games': open_games,
	})


@require_GET # only for showing empty forms
@login_required
def make_game(request):
	"""
		Show the empty form to the user who is starting a game.
	"""
	form = CreateGameForm(data = None)
	return render(request, 'make_game.html', {
		'form': form,
	})


@require_POST
@login_required
def join_game(request):
	"""
		Show the empty form to the user who is starting a game.
	"""
	try:
		id = int(request.GET['id'])
		game = Game.objects.get(id = id)
	except (KeyError, ValueError, Game.DoesNotExist), e: # if no id or not a valid id or no such game
		return redirect(to = '%s' % reverse('wakkerdam_game_not_found'))
	form = JoinPlayerForm(data = request.POST)
	if form.is_valid():
		player = form.instance
		""" Make sure a player can't join twice """
		for player_loop in game.players.all():
			if player_loop.user.pk == request.user.pk:
				return HttpResponse('You have already joined asshole')
			if player_loop.name == player.name:
				return HttpResponse('Sorry, too late, this name has already been taken! KUT')
		player.game = game
		player.user = request.user
		player.save()
	""" send the player back to the game overview: """
	return redirect(to = '%s?id=%d' % (reverse('wakkerdam_game'), game.id))


@require_POST # only send completed forms here
@login_required
def make_game_submit(request):
	"""
		Start a new game that people can join, using the provided form data.
	"""
	form = CreateGameForm(data = request.POST)
	if form.is_valid():
		""" save the new Game if it's valid """
		game = form.instance
		game.initiator = request.user
		game=form.save()
		player=Player(name='Master',game=game, user=request.user)
#		distribute_roles(game)
		player.save()
		game.players.add(player)
	return redirect(to = '%s?id=%d' % (reverse('wakkerdam_game'), game.id))


@require_POST
@login_required
def start_game(request):
	try:
		id = int(request.GET['id'])
		game = Game.objects.get(id = id)
	except (KeyError, ValueError, Game.DoesNotExist), e: # if no id or not a valid id or no such game
		return redirect(to = '%s' % reverse('wakkerdam_game_not_found'))
	if request.user==game.initiator:
		game.state='start'
		game.save()
		form = NumberOfWolvesForm(data = None, initial={'nr':number_of_wolves(game.players.all().count())})
		return render(request, 'start_game.html', {
		'form': form,
		'game': game,
		})

	else:
		return redirect(to = '%s?id=%d' % (reverse('wakkerdam_game'), game.id))


@require_POST
@login_required
def leave_game(request):
	try:
		id = int(request.GET['id'])
		game = Game.objects.get(id = id)
	except (KeyError, ValueError, Game.DoesNotExist), e: # if no id or not a valid id or no such game
		return redirect(to = '%s' % reverse('wakkerdam_game_not_found'))
	game.players.filter(game=game, user=request.user).delete()
	return redirect(to = '%s?id=%d' % (reverse('wakkerdam_game'), game.id))


def show_game(request):
	try:
		id = int(request.GET['id'])
		game = Game.objects.get(id = id)
	except (KeyError, ValueError, Game.DoesNotExist), e: # if no id or not a valid id or no such game
		return redirect(to = '%s' % reverse('wakkerdam_game_not_found'))
	form = JoinPlayerForm(data = None)
	currentplayer = None
	if request.user.is_authenticated():
		currentplayers = Player.objects.filter(game=game,user=request.user)
		if currentplayers:
			currentplayer = currentplayers[0]
	return render(request, 'show_game.html', {
		'game': game,
		'form': form,
		'currentplayer':currentplayer,
		'minimum_players':MINIMUM_STARTING_PLAYERS,
	})


def game_not_found(request):
	return render(request, 'game_not_found.html')

def start_phase_two(request):
	try:
		id = int(request.GET['id'])
		game = Game.objects.get(id = id)
	except (KeyError, ValueError, Game.DoesNotExist), e: # if no id or not a valid id or no such game
		return redirect(to = '%s' % reverse('wakkerdam_game_not_found'))
	form = NumberOfWolvesForm(data = request.POST)
	if form.is_valid():
		if 0 < form.cleaned_data['nr'] < game.players.all().count():
			wolves = sample(game.players.all(), form.cleaned_data['nr'])
			for wolf in wolves:
				wolf.state = Player.WOLF
				wolf.save()
			game.state = 'night'
			game.save()
			return redirect(to = '%s?id=%d' % (reverse('wakkerdam_night'), game.id))
	return HttpResponse('Je bent een sukkeltje, volgende keer beter. Peters moeder troost je wel!')


def info(request):
	return render(request, 'info.html')


