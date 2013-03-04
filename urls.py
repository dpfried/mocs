from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mocs.views.home', name='home'),
    # url(r'^mocs/', include('mocs.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', 'views.home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^maps/', include('maps.urls')),
    url(r'^reload/$', 'views.reload_site'),
)
