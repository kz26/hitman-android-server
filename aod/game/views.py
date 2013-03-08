from django.conf import settings
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from aod.game.models import *
from aod.game.serializers import *
from aod.users.gcm_auth import *
from aod.game import tasks
from gcm import GCM

gcm = GCM(settings.GCM_API_KEY) 

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

    def post_save(self, game, created):
        if created:
            tasks.assign_targets.apply_async([game.id], eta=game.start_time)

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

    def post_save(self, game, created):
        tasks.notify_join.delay(game.id, self.request.user.username)

class UpdateLocation(generics.CreateAPIView):
    model = LocationRecord
    serializer_class = LocationRecordSerializer
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_games = request.user.games.all()
        if not user_games.count():
            return Response({'success': False, 'reason': 'User is not joined to a game'}, status=403)
        else:
            self.user_game = user_games[0]
        return super(UpdateLocation, self).post(request, *args, **kwargs)

    def pre_save(self, obj):
        obj.user = self.request.user
        obj.game = self.user_game
