from django.contrib.auth.models import User
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    gcm_regid = serializers.CharField()
