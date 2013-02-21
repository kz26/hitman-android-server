from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/$', 'aod.users.views.do_login', name='login'),
)
