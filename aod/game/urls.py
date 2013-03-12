from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from aod.game.views import *

urlpatterns = patterns('',
    url(r'^$', GameList.as_view(), name='GameList'),
    url(r'^create/$', CreateGame.as_view(), name='CreateGame'),
    url(r'^(?P<pk>[0-9]+)/$', ShowGame.as_view(), name='ShowGame'),
    url(r'^(?P<pk>[0-9]+)/join/$', JoinGame.as_view(), name='JoinGame'),
    url(r'^sensors/location/create/$', CreateLocation.as_view(), name='CreateLocation'),
    url(r'^sensors/camera/upload/$', PhotoUpload.as_view(), name='PhotoUpload'),
    url(r'^kill/$', DoKill.as_view(), name='DoKill'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
