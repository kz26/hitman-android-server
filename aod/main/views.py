from django.http import *
from django.views.decorators.http import *
from django.views.decorators.csrf import *
from django.shortcuts import *
from django.contrib.auth.decorators import *
from django.utils import timezone
from aod.main.models import *

@require_POST
@login_required
def update_location(request):
    if 'coords' in request.POST:
        x, y = request.POST['coords'].split(",")
        coords = "POINT(%s %s)" % (x,y)
        print coords

        timenow = timezone.now()
        user = request.user

        contract_target = Contract.objects.get(target=user)
        contract_target.target_location = coords
        contract_target.target_timestamp = timenow
        contract_target.save()
        contract_assassin = Contract.objects.get(assassin=user)
        contract_assassin.assassin_location = coords
        contract_assassin.assassin_timestamp = timenow
        contract_assassin.save()

        return HttpResponse()
    else:
        raise Http404
