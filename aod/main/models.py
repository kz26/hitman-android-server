from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import *
from django.dispatch import receiver
from django.contrib.auth.models import User
from geopy.distance import distance
from geopy.point import Point
from gcm import GCM

# Create your models here.

class Contract(models.Model):
    assassin = models.ForeignKey(User, related_name="+")
    assassin_location = models.PointField()
    assassin_timestamp = models.DateTimeField()
    target = models.ForeignKey(User, related_name="+")
    target_location = models.PointField() 
    target_timestamp = models.DateTimeField()

    def __unicode__(self):
        return "Assassin: %s, Target: %s" % (self.assassin.username, self.target.username)

    def get_proximity(self):
        return distance(
            Point(*self.assassin_location.coords),
            Point(*self.target_location.coords)
        ).meters

# Signal handling

gcm = GCM(settings.GCM_SENDER_ID)


#@receiver(post_save, sender=Contract, dispatch_uid="contract_post_save_gcm")
def gcm_update(sender, **kwargs):
    contract = kwargs['instance']
    assassin_gcmid = contract.assassin.get_profile().gcm_regid
    target_gcmid = contract.target.get_profile().gcm_regid
    data = {
        'assassin': {
            'x': contract.assassin_location.x,
            'y': contract.assassin_location.y
        },
        'target': {
            'x': contract.target_location.x,
            'y': contract.target_location.y
        }
    }
    gcm.json_request(registration_ids=[assassin_gcmid, target_gcmid], data=data)
