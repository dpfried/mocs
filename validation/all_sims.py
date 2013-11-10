from lib.database import ManagedSession, sliced_query
from lib.mocs_database import Document, filter_query
import sys
import cPickle
from lib.similarity import jaccard

from validation.coverage import count_terms

def jaccard_query(documents, phrases_to_score, partial):
    def status_callback(s):
        sys.stdout.write('\r' + s)
        sys.stdout.flush()
    return jaccard((doc.terms_list() for doc in documents), phrases_to_score, partial=partial, status_callback=status_callback, status_increment=1000)

def jaccard_threshold(query, threshold=10, partial=False):
    documents = list(query)
    term_counts =  count_terms(documents)
    phrases_to_score = set(term for term, count in term_counts.iteritems()
                           if count >= threshold)
    return jaccard_query(documents, phrases_to_score, partial=partial)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dump_filename')
    parser.add_argument('--threshold', type=int, default=10)
    args = parser.parse_args()
    with ManagedSession() as session:
        query = sliced_query(filter_query(session.query(Document), dirty=False, sample_size=30000))
        jaccard_return = jaccard_threshold(query, partial=True, threshold=args.threshold)
        with open(args.dump_filename, 'wb') as f:
            cPickle.dump(jaccard_return, f)
