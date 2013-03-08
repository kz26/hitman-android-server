from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from aod.game.views import *

urlpatterns = patterns('',
    url(r'^$', GameList.as_view(), name='GameList'),
    url(r'^create/$', CreateGame.as_view(), name='CreateGame'),
    url(r'^(?P<pk>[0-9]+)/$', ShowGame.as_view(), name='ShowGame'),
    url(r'^(?P<pk>[0-9]+)/join/$', JoinGame.as_view(), name='JoinGame'),
    url(r'^(?P<pk>[0-9]+)/sensors/location/update/$', UpdateLocation.as_view(), name='UpdateLocation'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
