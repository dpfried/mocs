from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('nsf_maps.views',
    url(r'^basemap/(\d*)/$', 'basemap', name='nsf_basemap'),
    url(r'^basemap_metadata/(\d*)/$', 'basemap_metadata', name='nsf_basemap_metadata'),
    url(r'^heatmap_metadata/(\d*)/$', 'heatmap_metadata', name='nsf_heatmap_metadata'),
    url(r'^heatmap/(\d*)/$', 'heatmap', name='nsf_heatmap'),
    url(r'^task_status/(\d*)/$', 'task_status', name='nsf_task_status'),
    url(r'^map/(\d*)/$', 'display_map', name='nsf_display_map'),
    #url(r'^map/$', 'display_map', name='display_map'),
    url(r'^request_map/$', 'request_map', name='nsf_request_map'),
    url(r'^query/$', 'query', name='nsf_query'),
    url(r'^task/(\d*)/heatmap/$', 'heatmap_for_task_id', name='nsf_heatmap_for_task_id'),
    url(r'^task/(\d*)/basemap/$', 'basemap_for_task_id', name='nsf_basemap_for_task_id'),
)
