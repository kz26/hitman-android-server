from django.conf import settings
from django.contrib.gis.geos import *
from aod.game.models import *
from rest_framework import serializers

class LatLongField(serializers.WritableField):
    def to_native(self, value):
        return "%s,%s" % (value.x, value.y)

    def from_native(self, value):
        return "POINT(%s %s)" % tuple(value.split(","))

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game

    players = serializers.SerializerMethodField('get_players')
    location = LatLongField()

    def get_players(self, obj):
        plist = []
        for p in obj.players.all():
            plist.append({'id': p.id, 'username': p.username})
        return plist

class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'name', 'start_time', 'location')

    location = LatLongField()

class LocationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationRecord
        fields = ('location',)

