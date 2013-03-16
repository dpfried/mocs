# Create your views here.
from lib.database import Author, Conference, Journal
from utils import json_response, generalize

def to_val_list(named_tpls, name_lookup_fn, doc_lookup_fn = lambda t: t.doc_count):
    return [{'label': '%s : %d' % (name_lookup_fn(named_tpl), doc_lookup_fn(named_tpl)),
             'value': name_lookup_fn(named_tpl)}
            for named_tpl in named_tpls]

@json_response
def top_authors(request):
    if request.method == 'GET':
        authors_and_counts = Author.name_like_top(generalize(request.GET.get('term')),
                                                  n=request.GET.get('n', 10))
        return to_val_list(authors_and_counts, name_lookup_fn=lambda t: t.Author.name)

@json_response
def top_journals(request):
    if request.method == 'GET':
        authors_and_counts = Journal.name_like_top(generalize(request.GET.get('term')),
                                                   n=request.GET.get('n', 10))
        return to_val_list(authors_and_counts, name_lookup_fn=lambda t: t.Journal.name)

@json_response
def top_conferences(request):
    if request.method == 'GET':
        authors_and_counts = Conference.name_like_top(generalize(request.GET.get('term')),
                                                      n=request.GET.get('n', 10))
        return to_val_list(authors_and_counts, name_lookup_fn=lambda t: t.Conference.name)
