from lib.mocs_database import create_query_for_model, filter_query, Document
import json
import sys

import lib.database as db
import nltk
from lib.utils import sub_lists

def count_terms(documents, print_freq = 1000):
    term_counts = nltk.FreqDist()
    for i, document in enumerate(documents):
        term_counts.update(document.terms_list())
        if print_freq and i % print_freq == 0:
            sys.stdout.write('\r%d counted' % i)
            sys.stdout.flush()
    return term_counts

def all_terms():
    with db.ManagedSession() as session:
        query = db.sliced_query(filter_query(session.query(Document)), slice_size=100000)
        return count_terms(query)

def check_coverage(document_query, term_list, print_every=1000, partial=False):
    docs_covered = 0
    term_set = set(tuple(term) for term in term_list)
    for doc_index, doc in enumerate(document_query):
        term_iterator = doc.terms_list()
        if partial:
            term_iterator = (subterm for term in term_iterator
                             for subterm in sub_lists(term, proper=False))
        if any(term in term_set for term in term_iterator):
            docs_covered += 1
        if doc_index % print_every == 0:
            sys.stdout.write("\r%d / %d (%0.2f) documents covered" % (docs_covered, doc_index + 1, float(docs_covered) / (doc_index + 1)))
            sys.stdout.flush()
    print "total of %d / %d (%0.2f) documents covered" % (docs_covered, doc_index + 1, float(docs_covered) / (doc_index + 1))
    return docs_covered, doc_index + 1

def validate_map(basemap, dirty=True, sample=False, partial=False):
    with db.ManagedSession() as session:
        query = db.sliced_query(create_query_for_model(session, basemap, dirty=dirty, sample=sample), slice_size=100000)
        return check_coverage(query, json.loads(basemap.phrases_in_map), partial=partial)
