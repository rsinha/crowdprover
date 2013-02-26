from django.conf.urls import patterns, include, url
from django.contrib import admin

from proveit import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^polls/', include('proveit.polls.urls', namespace="polls")),
    url(r'^admin/', include(admin.site.urls)),
)
