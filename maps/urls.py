from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('maps.views',
    url(r'^basemap/$', 'basemap'),
    url(r'^heatmap/$', 'heatmap'),
    url(r'^task_status/$', 'task_status', name='task_status'),
    url(r'^task/$', 'get_task'),
)
