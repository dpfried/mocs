from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('maps.views',
    url(r'^map/$', 'map'),
    url(r'^task_status/$', 'task_status'),
    url(r'^task/$', 'get_task'),
)
