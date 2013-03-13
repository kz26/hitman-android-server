from django.conf import settings
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from rest_framework import views
from aod.game.models import *
from aod.game.serializers import *
from aod.users.gcm_auth import *
from aod.game import tasks
from aod.users import permissions as userPermissions
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
            return Response({'success': True, 'num_players': game.players.all().count()})

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

class CreateLocation(generics.CreateAPIView):
    model = LocationRecord
    serializer_class = LocationRecordSerializer
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated, userPermissions.IsInGame)

    def pre_save(self, obj):
        obj.user = self.request.user
        obj.game = self.request.user.games.all()[0]

class PhotoUpload(generics.CreateAPIView):
    model = Photo
    serializer_class = PhotoSerializer
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated, userPermissions.IsInGame)

    def pre_save(self, obj):
        obj.user = self.request.user
        obj.game = self.request.user.games.all()[0]

    def post_save(self, obj, created):
        if created:
            tasks.notify_photo.delay(obj.id)

class DoKill(views.APIView):
    authentication_classes = (GCMAuthentication,)
    permission_classes = (permissions.IsAuthenticated, userPermissions.IsInGame)

    def post(self, request):
        if 'kill_code' in request.DATA:
            result = Kill.objects.process_kill(request.user, request.DATA['kill_code'])
            if result:
                return Response({'success': True})
            else:
                return Response({'success': False, 'reason': 'Invalid kill code'}, status=403)
        else:
            return Response({'success': False, 'reason': 'kill_code not provided'}, status=400)

