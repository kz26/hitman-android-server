from django.conf.urls import patterns, include, url
from aod.users.views import *

urlpatterns = patterns('',
    url(r'^login/$', DoLogin.as_view(), name='login'),
    url(r'^signup/$', DoSignup.as_view(), name='signup'),
)
