from rest_framework import authentication
from aod.users.models import *

class GCMAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        gcmid = request.META.get('HTTP_X_GCMID')
        if not gcmid:
            return None

        try:
            user = Profile.objects.get(gcm_regid=gcmid).user
        except Profile.DoesNotExist:
            raise authenticate.AuthenticationFailed("Invalid API key")
        return (user, None)
