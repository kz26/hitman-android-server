from django.conf import settings
from django.contrib.gis.geos import *
from aod.game.models import *
from rest_framework import serializers

class LatLongField(serializers.WritableField):
    def to_native(self, value):
        return "%s,%s" % (value.y, value.x)

    def from_native(self, value):
        return "POINT(%s %s)" % tuple(reversed(value.split(",")))

class PlayersField(serializers.Field):
    read_only = True
    def to_native(self, obj):
        plist = []
        for p in obj.players.all():
            plist.append({'id': p.id, 'username': p.username})
        return plist

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game

    players = PlayersField(source="*")
    location = LatLongField()

    def get_players(self, obj):
        plist = []
        for p in obj.players.all():
            plist.append({'id': p.id, 'username': p.username})
        return plist

class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'name', 'start_time', 'location', 'players')

    location = LatLongField()
    players = PlayersField(source="*")

class LocationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationRecord
        fields = ('location',)
    location = LatLongField()

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('photoset', 'photo')

