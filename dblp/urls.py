from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dblp.views',
    url(r'^top_authors$', 'top_authors', name='top_authors'),
    url(r'^top_journals$', 'top_journals', name='top_journals'),
    url(r'^top_conferences$', 'top_conferences', name='top_conferences'),
)
