from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import *
from django.dispatch import receiver
from django.contrib.auth.models import User
from geopy.distance import distance
from geopy.point import Point
import uuid
from gcm import GCM

# Create your models here.

class Game(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    location = models.PointField()
    players = models.ManyToManyField(User, related_name="+")

    objects = models.GeoManager()

class Contract(models.Model):
    game = models.ForeignKey(Game)
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
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, related_name="+")

    class Meta:
        abstract = True

class LocationRecord(SensorRecord):
    location = models.PointField()

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

    #def get_proximity(self):
    #    return distance(
    #        Point(*self.assassin_location.coords),
    #        Point(*self.target_location.coords)
    #    ).meters

# Signal handling

gcm = GCM(settings.GCM_SENDER_ID)


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
