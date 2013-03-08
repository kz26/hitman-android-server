from django.conf import settings
from celery import task
import random
from gcm import GCM

@task
def assign_targets(gameid):
    from aod.game.models import Game
    game = Game.objects.get(id=gameid)
    playerCount = game.players.all().count()
    if playerCount >= 2:
        print "Game %s: Assigning contracts for %s players" % (game.id, playerCount)
        players = random.shuffle(list(game.players.all()))
        for index, player in enumerate(players[1:]):
            target = player
            assassin = players[index]
            Contract.objects.create(game=game, assassin=assassin, target=target)
        # add last-to-first contract
            Contract.objects.create(game=game, assassin=players[-1], target=players[0])

        start_game.apply([gameid])

    else:
        print "Game %s: not enough players - deleting" % (game.id)
        if game.players.all().count():
            gcmid = game.players.all()[0].get_profile().gcm_regid
            gcm.json_request(registration_ids=[gcmid], data={'type': 'game_canceled'})
        game.delete()

@task
def start_game(gameid):
    from aod.game.models import Game
    game = Game.objects.get(id=gameid)
    print "Game %s: starting" % (game.id)
    gcm = GCM(settings.GCM_API_KEY)
    for player in game.players.all():
        gcmid = player.get_profile().gcm_regid
        contract = Contract.objects.get(assassin=player)
        target = contract.target.username
    gcm.json_request(registration_ids=[reg_id], data={'type': 'game_start', 'target': target})
