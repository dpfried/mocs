from lib.database import ManagedSession, sliced_query
from lib.mocs_database import Document, filter_query
import sys
import cPickle
from lib.similarity import jaccard
from lib.partial_match_dict import PartialMatchDict, PartialMatchDict2
from lib.ranking import cnc_unigrams
import itertools as its

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
    parser.add_argument('--threshold', type=int, default=0)
    parser.add_argument('--partial', action='store_true')
    parser.add_argument('--slice_size', type=int, default=100000)
    parser.add_argument('--dirty', action='store_true')
    parser.add_argument('--n_terms', type=int, default=5000)
    args = parser.parse_args()
    with ManagedSession() as session:
        def make_query():
            return sliced_query(filter_query(session.query(Document), dirty=args.dirty, sample_size=None), slice_size=args.slice_size)
        term_iterator = (phrase for doc in make_query()
                         for phrase in doc.terms_list())
        if args.threshold > 0:
            print 'counting terms'
            term_counts =  count_terms(make_query())
            print 'thresholding terms'
            phrases_above_threshold = set(term for term, count in term_counts.iteritems()
                                          if count >= args.threshold)
            print '%d phrases above threshold' % len(phrases_above_threshold)
            term_iterator = its.ifilter(lambda p: p in phrases_above_threshold,
                                        term_iterator)
        import time
        start = time.time()
        print 'ranking phrases'
        scored_phrases, _ = cnc_unigrams(term_iterator)
        print 'ordering phrases'
        ordered_phrases = [phrase for phrase, score in its.islice(sorted(scored_phrases.iteritems(),
                                                                         key=lambda p: p[1], reverse=True),
                                                                  args.n_terms)]
        print 'similarities'
        jaccard_return = jaccard_query(make_query(), ordered_phrases, partial=args.partial, pmd_class=PartialMatchDict2)
        print time.time() - start
        print 'dumping'
        with open(args.dump_filename, 'wb') as f:
            cPickle.dump(jaccard_return, f)
