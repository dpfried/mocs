# Create your views here.
from lib.database import generalize
from lib.mocs_database import Author, Conference, Journal
from utils import json_response
from itertools import chain

def to_val_list(named_tpls, name_lookup_fn, doc_lookup_fn = lambda t: t.doc_count):
    return [{'label': '%s : %d papers' % (name_lookup_fn(named_tpl), doc_lookup_fn(named_tpl)),
             'value': name_lookup_fn(named_tpl)}
            for named_tpl in named_tpls]

def top_entities(class_, name_lookup_fn, term, n=10):
    entities_and_counts = class_.name_like_top(generalize(term), n=n)
    val_list = to_val_list(entities_and_counts, name_lookup_fn)
    return val_list

def top_authors(term, n):
    return top_entities(Author, lambda t:t.Author.name, term, n)

def top_journals(term, n):
    return top_entities(Journal, lambda t:t.Journal.name, term, n)

def top_conferences(term, n):
    return top_entities(Conference, lambda t:t.Conference.name, term, n)

def request_wrapper(fn):
    def foo(request):
        if request.method == 'GET':
            return fn(request.GET.get('term'), request.GET.get('n', 10))
    return json_response(foo)

def top_everything(term, n):
    def update_each_dict(list_of_dicts, key, val):
        return [dict(d.items() + [(key, val)])
                for d in list_of_dicts]
    entity_lists = [update_each_dict(fn(term, n), 'type', name)
                    for (fn, name) in [(top_authors, 'author'),
                                        (top_journals, 'journal'),
                                        (top_conferences, 'conference')]]
    entities = sorted(chain(*entity_lists), reverse=True, key=lambda s: s['value'])
    return entities[:n]

top_conferences_json = request_wrapper(top_conferences)
top_authors_json = request_wrapper(top_authors)
top_journals_json = request_wrapper(top_journals)
top_everything_json = request_wrapper(top_everything)
