
from wwwcie.settings import AUTH_USER_MODEL
from django.db import models


class Game(models.Model):
	"""
		Represent a play session of Wakkerdam
	"""
	name = models.CharField(max_length = 32)
	state = models.CharField(max_length = 10, choices = (
		('join', 'Players are joining'),
		('start', 'The game is starting'),
		('day', 'Playing; it is day in the game'),
		('night', 'Playing; it is night in the game'),
		('over', 'The game has been completed!'),
	), default = 'join')
	started = models.DateTimeField(auto_now_add = True)
	initiator = models.ForeignKey(AUTH_USER_MODEL)
	def __unicode__(self):
		return self.name


class Player(models.Model):
	CIV = 'civilian'
	WOLF = 'werewolf'
	name = models.CharField(max_length=32)
	role = models.CharField(max_length = 10, choices = (
		(CIV, 'Ordinary citizen'),
		(WOLF, 'Hungry mothafucker'),
	), blank = True, null = True, default = CIV)
	game = models.ForeignKey(Game, related_name = 'players')
	alive = models.BooleanField(default = True)
	""" User is the actual person, it's a standard Django model """
	""" Player is the civilian within a game session (new player for each game) """
	""" These need to be linked, so that users can only make their own moves """
	user = models.ForeignKey(AUTH_USER_MODEL)

	class Meta:
		unique_together = ('game', 'user')

	def __unicode__(self):
		return self.name


