import sdb_database as sdb_db
from database import ManagedSession, sliced_query
from chunking import noun_phrases
from csv import DictReader
from itertools import islice
from utils import drop, compose
from time import strptime
import argparse

def preprocess(text):
    return text.lower()

def memoized_row(memo, row):
    hashed = row.uuid()
    if hashed in memo:
        return memo[hashed]
    else:
        # shouldn't need to call session.add(row) if the referencing document
        # is added
        memo[hashed] = row
        return row

def load_memo_from_database(Class):
    memo = {}
    with ManagedSession() as session:
        print 'for class', Class
        print 'loading %d records already in database' % Class.query.count()
        for row in sliced_query(session.query(Class)):
            hashed = row.uuid()
            if hashed in memo:
                print "warning: found duplicate %s" % hashed
            memo[hashed] = row
    return memo

def parse_date(string):
    return strptime(string, "%m/%d/%Y")

def sandwich(record, lookup):
    return dict((field_name, lambda s: cast_fn(record[field_name]))
                for field_name, cast_fn in lookup.items()
                if record.get(field_name, '').strip())

def grant_from_csv(csv_fields):
    """populate the attributes of sdb_db.Grant from a csv record"""
    # every row should have something in the id column
    params = {'sdb_id': int(csv_fields['id'])}

    params.update(sandwich(csv_fields, {
        'award_number': int,
        'date_started': parse_date,
        'date_expires': parse_date,
        'published_year': int,
        'title': lambda s: s.strip().lower(),
        'abstract': lambda s: s.strip().lower()
    }))
    params['clean'] = bool(params['title'] or params['abstract'])
    params['terms'] = noun_phrases(params['title']) + noun_phrases(['abstract'])
    return sdb_db.Grant(**params)

def authors_from_csv(csv_fields):
    first = lambda n: 'name_first_' + n
    middle = lambda n: 'name_middle_' + n
    last = lambda n: 'name_last_' + n
    authors = []
    for i in range(1, 8):
        names = [csv_fields[acc(i)].strip() for acc in [first, middle, last]]
        if not any(names):
            break
        else:
            authors.append(sdb_db.Author(**dict(zip(['first_name', 'middle_name', 'last_name'], names))))
    return authors

def load_from_file(filename, offset=None):
    grants_memo = load_memo_from_database(sdb_db.Grant)
    author_memo = load_memo_from_database(sdb_db.Author)
    institution_memo = load_memo_from_database(sdb_db.Institution)
    count = 0
    with open(filename) as f:
        reader = DictReader(f, delimiter=",")
        for record in (reader if offset is None else drop(offset, reader)):
            doc = db.Document(title=title, year=year)

    clean = Column(Boolean)
    terms = Column(UnicodeText)

if __name__ == '__main__':
    # mapping of author, journal, and conference names to existing rows in database

            # if this item has a title, memoize the terms and check if it's
            # clean (aka usable)
            if title != None:
                doc.terms = ','.join([' '.join(phrase) for phrase in noun_phrases(preprocess(title))])
                doc.clean = ok_title(title)
            else:
            # doc doesn't have a title, so mark it as unusable
                doc.clean = False
            # take care of authors and journal
            for author_name in author_names:
                doc.authors.append(memoized_row(db.Author, author_memo, author_name))
            if journal_name != None:
                doc.journal = memoized_row(db.Journal, journal_memo, journal_name)
            if conference_name != None:
                doc.conference = memoized_row(db.Conference, conference_memo, conference_name)

            db.session.add(doc)
            count += 1
            # commit changes periodically
            if (count % 1000 == 0):
                db.session.commit()
                print 'created %s records (about %.f%% done)' % (count, float(count) * 100 / 3228329)
        else:
            # if we're down here, we reached the end of some tag that wasn't a
            # doc tag, (for example title or year), so store the tag's text in
            # the data dictionary
            if elem.tag == 'author':
                if 'author_names' in data:
                    data['author_names'].append(elem.text)
                else:
                    data['author_names'] = [elem.text]
            elif elem.tag == 'journal':
                data['journal_name'] = elem.text
            elif elem.tag == 'booktitle':
                data['conference_name'] = elem.text
            else:
                data[elem.tag] = elem.text
        # save memory
        elem.clear()
    # commit lingering changes
    db.session.commit()
    print 'finished, created %s records' % count
