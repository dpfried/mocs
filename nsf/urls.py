from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('nsf.views',
    url(r'^top_authors$', 'top_authors', name='top_authors'),
    url(r'^top_institutions$', 'top_institutions', name='top_institutions'),
)
