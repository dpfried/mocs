import mocs_database as db
from chunking import noun_phrases
from dblp import ok_title

def preprocess(title):
    return title.lower()

if __name__ == "__main__":
    N = db.Document.query.count()
    count = 0
    for record in db.sliced_query(db.Document.query, session_to_write = db.session):
        count += 1
        if record.title:
            record.terms = ','.join([' '.join(phrase) for phrase in noun_phrases(preprocess(record.title))])
            record.clean = ok_title(record.title)
        else:
            record.clean = False
        if (count % 1000 == 0):
            print 'updated %s records (%.f%%)' % (count, float(count) * 100 / N)
    print 'finished, updated %s records' % count
