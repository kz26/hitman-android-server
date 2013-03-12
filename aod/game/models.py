from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import *
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.gis.measure import D
import uuid
import os
from datetime import date
from aod.game import fsqfuncs
from aod.game import gisfuncs
from aod.game import tasks
from aod.game import validators
from aod.game.imageResize import enlarge 

# Create your models here.

class Game(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField(validators=[validators.FutureDateValidator])
    location = models.PointField()
    players = models.ManyToManyField(User, related_name="games", null=True, blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.id, self.name)

    def has_ended(self):
        return self.contracts.all().count() <= 1

    def save(self, *args, **kwargs):
        firstSave = False
        if not self.id:
            firstSave = True
        super(Game, self).save(*args, **kwargs)
        if firstSave:
            tasks.assign_targets.apply_async([self.id], eta=self.start_time)

@receiver(m2m_changed, sender=Game.players.through, dispatch_uid="game join notification")
def game_join_notify(sender, **kwargs):
    if kwargs['action'] == "pre_add" and kwargs['reverse'] == False:
        game = kwargs['instance']
        new_players = [User.objects.get(pk=x) for x in kwargs['pk_set']]
        for player in new_players:
            player.get_profile().refresh_kill_code()
            tasks.notify_join.delay(game.id, player.username)

class Contract(models.Model):
    game = models.ForeignKey(Game, related_name="contracts")
    assassin = models.ForeignKey(User, related_name="+")
    target = models.ForeignKey(User, related_name="+")

    def __unicode__(self):
        return "Assassin: %s, Target: %s" % (self.assassin.username, self.target.username)

    def assassin_win(self): # call when assassin kills target
        target_contract = Contract.objects.get(assassin=self.target) # retrieve victim's contract
        self.target = target_contract.target # and update with new target
        self.save()
        target_contract.delete() # delete the deceased's contract
        return self

    def target_win(self): # call when target kills assassin
        assassin_contract = Contract.objects.get(target=self.assassin) # retrieve contract of person assigned to kill assassin
        assassin_contract.target = self.target # update target to the person who killed the assassin
        assassin_contract.save()
        self.delete()
        return assassin_contract 

class KillManager(models.Manager):
    def process_kill(self, user, kill_code):
        contracts = Contract.objects.filter(assassin=user, target__profile__kill_code=kill_code)
        if contracts.exists() and user != contracts[0].target:
            killer = contracts[0].assassin
            victim = contracts[0].target
            toRun = contracts[0].assassin_win
        else:
            contracts = Contract.objects.filter(target=user, assassin__profile__kill_code=kill_code)
            if contracts.exists() and user != contracts[0].assassin:
                killer = contracts[0].target
                victim = contracts[0].assassin
                toRun = contracts[0].target_win
            else:
                return False
        killRecord = self.create(game=contracts[0].game, killer=killer, victim=victim)
        new_contract = toRun()
        tasks.notify_killed.delay(killRecord.victim)
        if killRecord.game.has_ended():
            tasks.end_game.delay(killRecord.game.id) 
        else:
            tasks.notify_new_target.delay(new_contract.id)
        return True


class Kill(models.Model):
    game = models.ForeignKey(Game)
    killer = models.ForeignKey(User, related_name="+")
    victim = models.ForeignKey(User, related_name="+")
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = KillManager()

    def __unicode__(self):
        return "%s killed %s" % (self.killer, self.victim)

class SensorRecord(models.Model):
    class Meta:
        ordering = ['-timestamp']
    timestamp = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey(Game, related_name="+")
    user = models.ForeignKey(User, related_name="+")

    class Meta:
        abstract = True

class LocationManager(models.Manager):
    def gen_user_location(self, contract):
        userLocs = list(self.filter(user=contract.target).order_by("-timestamp")[:5])
        if not userLocs:
            return None
        mostRecentLoc = userLocs[0]
        isMoving = False
        gcmid = contract.assassin.get_profile().gcm_regid
        if gisfuncs.multi_distance(userLocs) >= 250:
            isMoving = True
            oldestLoc = userLocs[-1]
            nameFrom = fsqfuncs.get_nearest_location(oldestLoc.location)
            nameTo = fsqfuncs.get_nearest_location(mostRecentLoc.location)
            if nameFrom and nameTo:
                return [(gcmid, {'type': 'location_moving', 'target': contract.target.username, 'locationFrom': nameFrom, 'locationTo': nameTo})]
            return None
        else:
            name = fsqfuncs.get_nearest_location(mostRecentLoc.location)
            if name:
                return [(gcmid, {'type': 'location_stationary', 'target': contract.target.username, 'location': name})]
            return None

class LocationRecord(SensorRecord):
    location = models.PointField()

    objects = LocationManager()

    def __unicode__(self):
        return "%s, %s, %s,%s" % (self.user, self.timestamp, self.location.x, self.location.y)

class PhotoSetManager(models.Manager):
    def gen_photosets(self, contract):
        targetLocs = LocationRecord.objects.filter(game=contract.game, user=contract.target).order_by("-timestamp") 
        if not targetLocs.exists():
            return None
        for player in contract.game.players.all().order_by("?"):
            if player == contract.assassin or player == contract.target:
                continue
            takerLocs = LocationRecord.objects.filter(game=contract.game, user=player).order_by("-timestamp")
            if not takerLocs.exists():
                continue
            if gisfuncs.multi_distance([takerLocs[0], targetLocs[0]]) > 50:
                continue
            ps = self.filter(contract=contract, user=player)
            if ps.exists():
                return [(player.get_profile().gcm_regid, {'type': 'take_photo', 'photoset': ps[0].id})]
            else:
                ps = self.create(game=contract.game, contract=contract, user=player)
                return [(player.get_profile().gcm_regid, {'type': 'take_photo', 'photoset': ps.id})]

class PhotoSetRecord(SensorRecord):
    contract = models.ForeignKey(Contract)

    objects = PhotoSetManager()

def gen_filename(instance, filename):
    fn = date.today().strftime("%Y/%m/%d/")
    fn += str(uuid.uuid1()) + os.path.splitext(filename)[1].lower()
    return fn

class Photo(models.Model):
    photoset = models.ForeignKey(PhotoSetRecord)
    photo = models.FileField(upload_to=gen_filename)

@receiver(post_save, sender=Photo, dispatch_uid="enlarge photo")
def enlarge_photo(sender, **kwargs):
    enlarge(kwargs['instance'].photo.path) 

NOTIFICATION_PROVIDERS = [LocationRecord.objects.gen_user_location, PhotoSetRecord.objects.gen_photosets]

