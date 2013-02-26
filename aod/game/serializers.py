from django.conf import settings
from aod.game.models import *
from rest_framework import serializers

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'name', 'start_time', 'location_lat', 'location_long', 'players') 

    players = serializers.SerializerMethodField('get_players')
    location_lat = serializers.SerializerMethodField('get_lat')
    location_long = serializers.SerializerMethodField('get_long')

    def get_lat(self, obj):
        return obj.location.x

    def get_long(self, obj):
        return obj.location.y

    def get_players(self, obj):
        plist = []
        for p in obj.players.all():
            plist.append({'id': p.id, 'username': p.username})
        return plist

class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'name', 'start_time', 'location_lat', 'location_long')

    location_lat = serializers.FloatField()
    location_long = serializers.FloatField()

    def restore_object(self, attrs, instance=None):
        if instance:
            game = instance
        else:
            game = super(CreateGameSerializer, self).restore_object(attrs, instance)
        game.location = "POINT(%s %s)" % (attrs['location_lat'], attrs['location_long'])
        return game

class LocationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationRecord
        fields = ('location_lat', 'location_long')

    location_lat = serializers.FloatField()
    location_long = serializers.FloatField()

    def restore_object(self, attrs, instance=None):
        if instance:
            record = instance
        else:
            record = super(UpdateLocationSerializer, self).restore_object(attrs, instance)
        record.location = "POINT(%s %s)" % (attrs['location_lat'], attrs['location_long'])
        return record
