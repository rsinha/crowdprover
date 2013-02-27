from django.conf.urls import patterns, include, url
from django.contrib import admin

from proveit import views
from proveit import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^polls/', include('proveit.polls.urls', namespace="polls")),
    url(r'^programs/', include('proveit.programs.urls', namespace="programs")),
    url(r'^admin/', include(admin.site.urls)),
)

if not settings.DEBUG:
   urlpatterns += staticfiles_urlpatterns()
