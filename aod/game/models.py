from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import *
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.gis.measure import D
import uuid
from aod.game import fsqfuncs
from aod.game import gisfuncs
from aod.game import tasks

# Create your models here.

class Game(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    location = models.PointField()
    players = models.ManyToManyField(User, related_name="players", null=True, blank=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return "%s: %s" % (self.id, self.name)

@receiver(post_save, sender=Game, dispatch_uid="game start signal")
def game_start_handler(sender, **kwargs):
    game = kwargs['instance']
    tasks.assign_targets.apply_async([game.id], eta=game.start_time)

class Contract(models.Model):
    game = models.ForeignKey(Game, related_name="contracts")
    assassin = models.ForeignKey(User, related_name="+")
    target = models.ForeignKey(User, related_name="+")

    def __unicode__(self):
        return "Assassin: %s, Target: %s" % (self.assassin.username, self.target.username)

    def assassin_win(self): # call when assassin kills target
        Kill.objects.create(game=self, killer=self.assassin, victim=self.target) # create kill record
        target_contract = Contract.objects.get(assassin=self.target) # retrieve victim's contract
        self.target = target_contract.target # and update with new target
        self.save()
        target_contract.delete() # delete the deceased's contract

    def target_win(self): # call when target kills assassin
        Kill.objects.create(game=self, killer=self.target, victim=self.assassin) # create kill record
        assassin_contract = Contract.objects.get(target=self.assassin)
        self.assassin = assassin_contract.assassin
        self.save()
        assassin_contract.delete()

class Kill(models.Model):
    game = models.ForeignKey(Game)
    killer = models.ForeignKey(User, related_name="+")
    victim = models.ForeignKey(User, related_name="+")
    timestamp = models.DateTimeField(auto_now_add=True)

class SensorRecord(models.Model):
    class Meta:
        ordering = ['-timestamp']
    timestamp = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey(Game, related_name="+")
    user = models.ForeignKey(User, related_name="+")

    class Meta:
        abstract = True

class LocationManager(models.Manager):
    def gen_user_location(self, user):
        userLocs = list(self.filter(user=user).order_by("-timestamp")[:5])
        if not userLocs:
            return None
        mostRecentLoc = userLocs[0]
        isMoving = False
        if gisfuncs.multi_distance(userLocs) >= 250:
            isMoving = True
            oldestLoc = userLocs[-1]
            nameFrom = fsqfuncs.get_nearest_location(oldestLoc.location)
            nameTo = fsqfuncs.get_nearest_location(mostRecentLoc.location)
            if nameFrom and nameTo:
                return {'type': 'location_moving', 'target': user.username, 'locationFrom': nameFrom, 'locationTo': nameTo}
            return None
        else:
            name = fsqfuncs.get_nearest_location(mostRecentLoc.location)
            if name:
                return {'type': 'location_stationary', 'target': user.username, 'location': name}
            return None

class LocationRecord(SensorRecord):
    location = models.PointField()

    objects = LocationManager()

    def __unicode__(self):
        return "%s, %s, %s,%s" % (self.user, self.timestamp, self.location.x, self.location.y)

class PhotoSetRecord(SensorRecord):
    contract = models.ForeignKey(Contract)

def gen_filename(instance, filename):
    fn = "%s.%s/" % (instance.content_type.app_label, instance.content_type.model)
    fn += date.today().strftime("%Y/%m/%d/")
    fn += str(uuid1()) + splitext(filename)[1].lower()
    return fn

class Photo(models.Model):
    photoset = models.ForeignKey(PhotoSetRecord)
    photo = models.FileField(upload_to=gen_filename)

NOTIFICATION_PROVIDERS = [LocationRecord.objects.gen_user_location]

#@receiver(post_save, sender=Contract, dispatch_uid="contract_post_save_gcm")
#def gcm_update(sender, **kwargs):
#    contract = kwargs['instance']
#    assassin_gcmid = contract.assassin.get_profile().gcm_regid
#    target_gcmid = contract.target.get_profile().gcm_regid
#    data = {
#        'assassin': {
#            'x': contract.assassin_location.x,
#            'y': contract.assassin_location.y
#        },
#        'target': {
#            'x': contract.target_location.x,
#            'y': contract.target_location.y
#        }
#    }
#    gcm.json_request(registration_ids=[assassin_gcmid, target_gcmid], data=data)
