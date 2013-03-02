from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from aod.game.models import *
from aod.game.serializers import *
from aod.users.gcm_auth import *

class GameList(generics.ListAPIView):
    model = Game
    serializer_class = GameSerializer

    def get_queryset(self):
        """
        If lat, long are provided, sort by distance
        """
        request = self.request
        if all([x in request.QUERY_PARAMS for x in ('lat', 'long')]):
            pnt = GEOSGeometry("POINT(%s %s)" % (float(request.QUERY_PARAMS['lat']), float(request.QUERY_PARAMS['long'])), srid=4326)
            qs = Game.objects.distance(pnt).order_by('distance')
        else:
            qs = Game.objects.all()
        return qs

class CreateGame(generics.CreateAPIView):
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    model = Game
    serializer_class = CreateGameSerializer

class ShowGame(generics.RetrieveAPIView):
    model = Game
    serializer_class = GameSerializer

class JoinGame(generics.UpdateAPIView):
    model = Game
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        if request.user.games.exists():
            return Response({'success': False, 'reason': 'User is already part of a game'}, status=403)
        else:
            game = self.get_object()
            game.players.add(request.user)             
            return Response({'success': True})

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

class UpdateLocation(generics.CreateAPIView):
    model = LocationRecord
    serializer_class = LocationRecordSerializer
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def pre_save(self, obj):
        obj.user = self.request.user
