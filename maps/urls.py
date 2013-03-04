from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('maps.views',
    url(r'^basemap/(\d*)/$', 'basemap'),
    url(r'^heatmap/(\d*)/$', 'heatmap'),
    url(r'^task_status/(\d*)/$', 'task_status', name='task_status'),
    url(r'^map/(\d*)/$', 'display_map', name='display_map'),
    #url(r'^map/$', 'display_map', name='display_map'),
    url(r'^request_map/$', 'request_map', name='request_map'),
    url(r'^query/$', 'query'),
)
