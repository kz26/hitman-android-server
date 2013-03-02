from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User)
    gcm_regid = models.CharField(max_length=255, blank=True)
    update_frequency = models.FloatField(default=3600)

    def __unicode__(self):
        return self.user.username
