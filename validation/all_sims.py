from lib.database import ManagedSession, sliced_query
from lib.mocs_database import Document, filter_query
import sys
import cPickle
from lib.similarity import jaccard
from lib.partial_match_dict import PartialMatchDict, PartialMatchDict2
from lib.ranking import cnc_unigrams

from validation.coverage import count_terms

def jaccard_query(documents, phrases_to_score, partial, **kwargs):
    def status_callback(s):
        sys.stdout.write('\r' + s)
        sys.stdout.flush()
    return jaccard((doc.terms_list() for doc in documents), phrases_to_score, partial=partial, status_callback=status_callback, status_increment=1000, **kwargs)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dump_filename')
    parser.add_argument('--threshold', type=int, default=10)
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--slice_size', type=int, default=100000)
    args = parser.parse_args()
    with ManagedSession() as session:
        def make_query():
            return sliced_query(filter_query(session.query(Document), dirty=False, sample_size=None), slice_size=args.slice_size)
        print 'counting terms'
        term_counts =  count_terms(make_query())
        print 'filtering terms'
        phrases_to_score = set(term for term, count in term_counts.iteritems()
                               if count >= args.threshold)
        print '%d phrases' % len(phrases_to_score)
        import time
        start = time.time()
        print 'ranking phrases'
        scored_phrases, _ = cnc_unigrams(phrase for doc in make_query()
                                         for phrase in doc.terms_list()
                                         if phrase in phrases_to_score)
        print 'ordering phrases'
        ordered_phrases = [phrase for phrase, score in sorted(scored_phrases.iteritems(),
                                                             key=lambda p: p[1], reverse=True)]
        print 'similarities'
        jaccard_return = jaccard_query(make_query(), ordered_phrases, partial=args.partial, pmd_class=PartialMatchDict2)
        print time.time() - start
        print 'dumping'
        with open(args.dump_filename, 'wb') as f:
            cPickle.dump(jaccard_return, f)
