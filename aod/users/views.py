from django.http import *
from django.views.decorators.http import *
from django.shortcuts import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import *
from aod.users.models import *

@require_POST
def do_login(request):
    if all([x in request.POST for x in ('user', 'password', 'gcm_regid')]):
        user = authenticate(username=request.POST['user'], password=request.POST['password'])
        if not user:
            raise HttpResponse(status=403)
        profile = user.get_profile()
        profile.gcm_regid = request.POST['regid']
        profile.save()
        return HttpResponse()
    else:
        raise Http404
