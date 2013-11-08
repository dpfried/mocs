from database import ManagedSession, sliced_query
from mocs_database import create_query_for_model
import json
import sys
def check_coverage(document_query, term_list, print_every=1000):
    docs_covered = 0
    term_set = set(tuple(term) for term in term_list)
    for doc_index, doc in enumerate(document_query):
        if any(term in term_set for term in doc.terms_list()):
            docs_covered += 1
        if doc_index % print_every == 0:
            sys.stdout.write("\r%d / %d (%0.2f) documents covered" % (docs_covered, doc_index + 1, float(docs_covered) / (doc_index + 1)))
            sys.stdout.flush()
    print "total of %d / %d (%0.2f) documents covered" % (docs_covered, doc_index + 1, float(docs_covered) / (doc_index + 1))
    return docs_covered, doc_index + 1

def validate_map(basemap, dirty=True, sample=False):
    with ManagedSession() as session:
        query = sliced_query(create_query_for_model(session, basemap, dirty=dirty, sample=sample))
        return check_coverage(query, json.loads(basemap.phrases_in_map))
