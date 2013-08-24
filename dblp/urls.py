from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dblp.views',
    url(r'^top_authors$', 'top_authors_json', name='top_authors'),
    url(r'^top_journals$', 'top_journals_json', name='top_journals'),
    url(r'^top_conferences$', 'top_conferences_json', name='top_conferences'),
    url(r'^top_everything$', 'top_everything_json', name='top_everything'),
)
