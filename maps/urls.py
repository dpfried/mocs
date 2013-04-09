from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('maps.views',
    url(r'^basemap/(\d*)/$', 'basemap'),
    url(r'^basemap_metadata/(\d*)/$', 'basemap_metadata'),
    url(r'^heatmap_metadata/(\d*)/$', 'heatmap_metadata'),
    url(r'^heatmap/(\d*)/$', 'heatmap'),
    url(r'^task_status/(\d*)/$', 'task_status', name='task_status'),
    url(r'^map/(\d*)/$', 'display_map', name='display_map'),
    #url(r'^map/$', 'display_map', name='display_map'),
    url(r'^request_map/$', 'request_map', name='request_map'),
    url(r'^query/$', 'query'),
    url(r'^task/(\d*)/heatmap/$', 'heatmap_for_task_id', name='heatmap_for_task_id'),
    url(r'^task/(\d*)/basemap/$', 'basemap_for_task_id', name='basemap_for_task_id'),
)
