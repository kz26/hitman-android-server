from django.http import *
from django.views.decorators.http import *
from django.views.decorators.csrf import *
from django.shortcuts import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import *
from aod.users.models import *

@require_POST
@csrf_exempt
def do_login(request):
   #if all([x in request.POST for x in ('user', 'password')]):
    if 'user' in request.POST:
        user = authenticate(username=request.POST['user'], password=request.POST['user'])
        if user:
            login(request, user)
        else:
            raise Http404
        if 'regid' in request.POST:
            profile = user.get_profile()
            profile.gcm_regid = request.POST['regid']
            profile.save()
        return HttpResponse()
    else:
        raise Http404
