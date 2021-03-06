from django.conf.urls import patterns, url

from proveit.programs import views

urlpatterns = patterns('',
    # ex: /programs/
    url(r'^$', views.index, name='index'),
    # ex: /programs/5/
    url(r'^(?P<program_id>\d+)/$', views.detail, name='detail'),
    # ex: /programs/5/submit/
    #url(r'^(?P<program_id>\d+)/submit/$', views.submit, name='submit'),
    # ex: /programs/5/results/
    url(r'^(?P<program_id>\d+)/results/$', views.results, name='results'),
)
