from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('nsf.views',
    url(r'^top_authors$', 'top_authors', name='nsf_top_authors'),
    url(r'^top_institutions$', 'top_institutions', name='nsf_top_institutions'),
)
