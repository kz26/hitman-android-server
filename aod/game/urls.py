from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from aod.game.views import *

urlpatterns = patterns('',
    url(r'^$', GameList.as_view(), name='GameList'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
