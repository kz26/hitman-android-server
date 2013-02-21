from django.http import *
from django.views.decorators.http import *
from django.views.decorators.csrf import *
from django.shortcuts import *
from django.contrib.auth.decorators import *
from django.utils import timezone
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from rest_framework import generics
from rest_framework import permissions
from aod.game.models import *
from aod.game.serializers import *

class GameList(generics.ListCreateAPIView):
    model = Game
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = GameSerializer

    def get(self, request, *args, **kwargs):
        if all([x in request.QUERY_PARAMS for x in ('lat', 'long')]):
            pnt = GEOSGeometry("POINT(%s %s)" % (float(request.QUERY_PARAMS['lat']), float(request.QUERY_PARAMS['long'])), srid=4326)
            qs = self.model.objects.distance(pnt).order_by('distance')
        else:
            qs = self.model.objects.all()
        self.queryset = qs
        return super(GameList, self).get(request, *args, **kwargs)

