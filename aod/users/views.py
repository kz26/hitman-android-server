from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from aod.users.models import *
from aod.users.serializers import *

class DoLogin(APIView):
    def post(self, request, *args, **kwargs):
        credentials = LoginSerializer(data=request.DATA)
        if credentials.is_valid():
            user = authenticate(username=credentials.object['username'], password=credentials.object['password'])
            if not user:
                return Response({'success': False, 'reason': 'bad credentials'}, status=403)
            profile = user.get_profile()
            profile.gcm_regid = credentials.object['gcm_regid']
            profile.save()
            return Response({'success': True})
        else:
            return Response({'success': False, 'reason': 'incorrect parameters'}, status=400)

class DoSignup(APIView):
    def post(self, request, *args, **kwargs):
        credentials = LoginSerializer(data=request.DATA)
        if credentials.is_valid():
            if not User.objects.filter(username=credentials.object['username']).exists():
                user = User.objects.create(credentials.object['username'], password=credentials.object['password'])
                return Response({'success': True})
            else:
                return Response({'success': False, 'reason': 'Username already exists'})
        else:
            return Response({'success': False, 'reason': 'incorrect parameters'}, status=400)
