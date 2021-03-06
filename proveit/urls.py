from django.conf.urls import patterns, include, url
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from proveit import views
from proveit import settings

dajaxice_autodiscover()
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.loginpage, name='login'),
    url(r'^logout/', views.logoutuser, name='logout'),
    url(r'^submit/', views.logging, name='logging'), # knew no better way to define the namespace 'logging' without assigning a new url to id
    url(r'^register/', views.registerpage, name='register'),
    url(r'^regsubmit/', views.registering, name='registering'), # knew no better way to define the namespace 'registering' without assigning a new url to id
    url(r'^programs/', include('proveit.programs.urls', namespace="programs")),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)

urlpatterns += staticfiles_urlpatterns()
