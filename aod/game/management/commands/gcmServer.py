from aod.game.models import *
from aod.users.models import *
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from time import sleep
from datetime import timedelta
from gcm import GCM

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        gcm = GCM(settings.GCM_API_KEY)
        last_update = {} # key = GCMID, value = datetime
        while True:
            for game in Game.objects.all():
                for contract in game.contracts.all():
                    for provider in NOTIFICATION_PROVIDERS:
                        result = provider(contract)
                        if result is None:
                            continue
                        for gcmid, msg in result:
                            if gcmid not in last_update:
                                last_update[gcmid] = None 
                            profile = Profile.objects.get(gcm_regid=gcmid)
                            if not last_update[gcmid] or timezone.now() >= last_update[gcmid] + timedelta(seconds=profile.update_frequency):
                                self.stderr.write("[%s] Sent GCM message %s\n" % (timezone.now(), str(result)))
                                gcm.json_request(registration_ids=[gcmid], data=msg)
                                last_update[gcmid] = timezone.now()
            sleep(60)
