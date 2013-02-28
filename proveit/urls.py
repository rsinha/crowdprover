from django.conf.urls import patterns, include, url
from django.contrib import admin

from proveit import views
from proveit import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^programs/', include('proveit.programs.urls', namespace="programs")),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
