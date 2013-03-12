from django.db import models
from django.contrib.auth.models import User
from aod.users.killcode import killcode

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User)
    gcm_regid = models.CharField(max_length=255, blank=True)
    update_frequency = models.FloatField(default=3600)
    kill_code = models.CharField(max_length=255)

    def __unicode__(self):
        return self.user.username

    def refresh_kill_code(self):
        self.kill_code = killcode.gen_kill_code()
        self.save()
