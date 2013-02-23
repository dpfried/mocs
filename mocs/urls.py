from django.conf.urls import patterns, include, url
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mocs.views.home', name='home'),
    # url(r'^mocs/', include('mocs.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^maps/', include('maps.urls')),
)
