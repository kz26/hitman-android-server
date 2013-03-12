from django.conf import settings
from celery import task
import random
from gcm import GCM
from django.utils import timezone

gcm = GCM(settings.GCM_API_KEY)

@task
def assign_targets(gameid):
    from aod.game.models import Game, Contract
    game = Game.objects.get(id=gameid)
    playerCount = game.players.all().count()
    if playerCount >= 2:
        print "Game %s: Assigning contracts for %s players" % (game.id, playerCount)
        players = list(game.players.all())
        random.shuffle(players)
        players.append(players[0])
        for index, player in enumerate(players[1:]):
            target = player
            assassin = players[index]
            Contract.objects.create(game=game, assassin=assassin, target=target)

        start_game.delay(gameid)

    else:
        print "Game %s: not enough players - deleting" % (game.id)
        if game.players.all().count():
            gcmid = game.players.all()[0].get_profile().gcm_regid
            gcm.json_request(registration_ids=[gcmid], data={'type': 'game_canceled'})
        game.delete()

@task
def start_game(gameid):
    from aod.game.models import Game, Contract
    #from aod.game.serializers import GameSerializer
    game = Game.objects.get(id=gameid)
    print "Game %s: starting" % (game.id)
    for player in game.players.all():
        player_profile = player.get_profile()
        contract = Contract.objects.get(game=game, assassin=player)
        target = contract.target.username
        data = {'type': 'game_start', 'target': target, 'kill_code': player_profile.kill_code}
        print "[%s] (%s) %s" % (timezone.now(), player.username, data) 
        gcm.json_request(registration_ids=[player_profile.gcm_regid], data=data)

@task
def notify_join(gameid, newPlayer): # newplayer is a username
    from aod.game.models import Game
    game = Game.objects.get(id=gameid)
    for player in game.players.all():
        if player.username != newPlayer:
            gcmid = player.get_profile().gcm_regid
            data = {'type': 'player_join', 'name': newPlayer}
            print "[%s] (%s) %s" % (timezone.now(), player.username, data)
            gcm.json_request(registration_ids=[gcmid], data=data)

@task
def notify_photo(photoid):
    from aod.game.models import Photo
    photo = Photo.objects.get(id=photoid)
    contract = photo.photoset.contract
    assassin_gcmid = contract.assassin.get_profile().gcm_regid
    data = {'type': 'photo_received', 'target': contract.target.username, 'url': photo.photo.url}
    print "[%s] (%s) %s" % (timezone.now(), contract.assassin.username, data)
    gcm.json_request(registration_ids=[assassin_gcmid], data=data)

@task
def notify_new_target(contractId):
    from aod.game.models import Contract
    contract = Contract.objects.get(id=contractId)
    assassin_gcmid = contract.assassin.get_profile().gcm_regid
    data = {'type': 'new_target', 'target': contract.target.username}
    print "[%s] (%s) %s" % (timezone.now(), contract.assassin.username, data)
    gcm.json_request(registration_ids=[assassin_gcmid], data=data)

@task
def notify_killed(game, user):
    profile = user.get_profile()
    data = {'type': 'killed', 'victim': user.username}
    for player in game.players.all():
        print "[%s] (%s) %s" % (timezone.now(), profile.gcm_regid, data)
        gcm.json_request(registration_ids=[player.get_profile().gcm_regid], data=data)

@task
def end_game(gameId):
    from aod.game.models import Game
    game = Game.objects.get(id=gameId)
    for player in game.players.all():
        gcm_ids.append(player.get_profile().gcm_regid)
    data = {'type': 'game_end', 'winner': game.contracts.all()[0].assassin.username}
    print "[%s] (%s) %s" % (timezone.now(), str(gcm_ids), data)
    gcm.json_request(registration_ids=gcm_ids, data=data)

