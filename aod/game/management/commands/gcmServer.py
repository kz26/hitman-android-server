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
        gcm = GCM(settings.GCM_SENDER_ID)
        last_update = {}
        while True:
            for game in Game.objects.all():
                for contract in game.contracts.all():
                    target_profile = contract.target.get_profile()
                    for provider in NOTIFICATION_PROVIDERS:
                        result = provider(contract.target)
                        if contract.target.username not in last_update:
                            last_update[contract.target.username] = None 
                        if not last_update[contract.target.username] or timezone.now() >= last_update[contract.target.username] + timedelta(seconds=target_profile.update_frequency):
                            reg_ids = [target_profile.gcm_regid]
                            gcm.json_request(registration_ids=reg_ids, data=result)
                            last_update[contract.target.username] = timezone.now()
            sleep(60)
