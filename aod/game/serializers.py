from aod.game.models import *
from rest_framework import serializers

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'name', 'start_time', 'location', 'num_players') 

    num_players = serializers.SerializerMethodField('get_num_players')

    def get_num_players(self, obj):
        return obj.players.all().count()
