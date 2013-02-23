from django.conf.urls import patterns, url

urlpatterns = patterns('maps.views',
    url(r'^map/$', 'map'),
    url(r'^task_status/$', 'task_status'),
    url(r'^request/$', 'start_request'),
)
