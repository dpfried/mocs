import sdb_database as sdb_db
from database import ManagedSession, sliced_query
from chunking import noun_phrases
from csv import DictReader
from utils import drop
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
        print 'loading %d records already in database' % session.query(Class).count()
        for row in sliced_query(session.query(Class)):
            hashed = row.uuid()
            if hashed in memo:
                print "warning: found duplicate %s" % hashed
            memo[hashed] = row
    return memo

def parse_date(string):
    return strptime(string.strip(), "%m/%d/%Y")

def sandwich(record, lookup):
    return dict((field_name, cast_fn(record[field_name]))
                for field_name, cast_fn in lookup.items()
                if record.get(field_name, '').strip())

def grant_from_csv(csv_fields):
    """populate the attributes of sdb_db.Grant from a csv record"""
    # every row should have something in the id column
    params = {'sdb_id': csv_fields['id'].strip()}

    params.update(sandwich(csv_fields, {
        'award_number': lambda x: x.strip(),
        'date_started': parse_date,
        'date_expires': parse_date,
        'published_year': int,
        'title': lambda s: s.strip().lower(),
        'abstract': lambda s: s.strip().lower()
    }))
    params['clean'] = bool(params.get('title') or params.get('abstract'))
    terms = []
    if params.get('title'):
        terms += noun_phrases(params.get('title'))
    if params.get('abstract'):
        terms += noun_phrases(params.get('abstract'))
    params['terms'] = sdb_db.stringify_terms(terms)
    return sdb_db.Grant(**params)

def authors_from_csv(csv_fields):
    first = lambda n: 'name_first_%d' % n
    middle = lambda n: 'name_middle_%d' % n
    last = lambda n: 'name_last_%d' % n
    authors = []
    for i in range(1, 8):
        names = [csv_fields[acc(i)].strip() for acc in [first, middle, last]]
        if not any(names):
            break
        else:
            names = dict(zip(['first_name', 'middle_name', 'last_name'], names))
            author = sdb_db.Author(**names)
            author.set_name(**names)
            authors.append(author)
    return authors

def institution_from_csv(csv_fields):
    params = {}
    sdb_id = csv_fields['inst_id'].strip()
    if sdb_id:
        params['sdb_id'] = sdb_id
    name = csv_fields['institution_name'].strip()
    if name and name != 'DATA NOT AVAILABLE':
        params['name'] = name
    if params:
        return sdb_db.Institution(**params)


def load_from_file(filename, offset=None):
    grants_memo = load_memo_from_database(sdb_db.Grant)
    author_memo = load_memo_from_database(sdb_db.Author)
    institution_memo = load_memo_from_database(sdb_db.Institution)
    count = 0
    if offset:
        print 'starting at row %d' % offset
    with open(filename) as f, ManagedSession() as session:
        reader = DictReader(f, delimiter=",")
        for csv_fields in (reader if offset is None else drop(offset, reader)):
            grant = grant_from_csv(csv_fields)
            if grant.uuid() in grants_memo:
                continue
            # print grant
            authors = authors_from_csv(csv_fields)
            if authors:
                mem_auths = [memoized_row(author_memo, author) for author in authors]
                # if len(mem_auths) != len(authors):
                #     print 'fewer memoized authors!'
                #     import pprint
                #     print pprint.pprint(csv_fields)
                # if len(set(mem_auths)) != len(mem_auths):
                #     print 'duplicate memoized authors!'
                #     import pprint
                #     print pprint.pprint(csv_fields)
                for author in set(mem_auths):
                    grant.authors.append(author)
            institution = institution_from_csv(csv_fields)
            if institution:
                grant.institution = memoized_row(institution_memo, institution)
            session.add(grant)
            count += 1
            grants_memo[grant.uuid()] = grant
            if (count % 1000 == 0):
                session.commit()
                print 'created %s records' % count
        session.commit()
        print 'created total of %s records' % count

if __name__ == '__main__':
    # mapping of author, journal, and conference names to existing rows in database
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--offset", type=int)
    parser.add_argument("filename")
    args = parser.parse_args()
    load_from_file(args.filename, offset=args.offset)
