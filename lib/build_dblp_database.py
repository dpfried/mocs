import xml.etree.cElementTree as tree
from database import ManagedSession
import mocs_database as db
import sys
from chunking import noun_phrases
import langid
import sys

# http://codereview.stackexchange.com/questions/2449/parsing-huge-xml-file-with-lxml-etree-iterparse-in-python
# CATEGORIES = set(['article', 'inproceedings', 'proceedings', 'book', 'incollection', 'phdthesis', 'mastersthesis', 'www'])
CATEGORIES = set(['article', 'inproceedings', 'book', 'incollection',
                  'phdthesis', 'mastersthesis'])

# use global vars to only load on demand
langdetect = None

stop_words = ['book review', 'guest editor', 'special issue', 'conference', 'workshop', 'symposium', 'part ii']

def has_stop_words(title):
    if title == 'home page':
        return True
    for s in stop_words:
        if s in title:
            return True
    return False

def ok_title(title):
    """see if the title appears to be English and doesn't have stopwords"""
    global langdetect
    if not langdetect:
        langdetect = langid.LangDetect(['en', 'de', 'fr', 'es'])
    is_english = lambda(text): langdetect.detect(text) == 'en'
    return title and is_english(title) and not has_stop_words(title.lower())

def preprocess(title):
    return title.lower()

def memoized_row(Class, memo, name):
    # this is a hack and will only work if the class constructor takes a name
    # param (e.g. Author or Journal, currently)
    if name in memo:
        return memo[name]
    else:
        # shouldn't need to call session.add(row) if the referencing document
        # is added
        row = Class(name=name)
        memo[name] = row
        return row

def load_memo_from_database(Class):
    """Class must have a name attribute"""
    with ManagedSession() as session:
        memo = {}
        print 'for class', Class
        query = session.query(Class)
        print 'loading %d records already in database' % query.count()
        for row in query:
            if row.name in memo:
                print "warning: found duplicate %s" % row.name
            memo[row.name] = row
        return memo

if __name__ == '__main__':
    # mapping of author, journal, and conference names to existing rows in database
    author_memo = load_memo_from_database(db.Author)
    journal_memo = load_memo_from_database(db.Journal)
    conference_memo = load_memo_from_database(db.Conference)

    count = 0

    data = {}
    # state machine to read doc info. elem is only returned upon reading the end of a
    # tag, so if we've read one of the top level categories, we check to see
    # what info we've stored about title, year, author etc (since these tags
    # have ended inside the outer document tag). We store these inner tags in
    # the data dictionary, and be sure to clear this upon reaching the end of a
    # tag so that attributes don't carry over from one document to another.
    with ManagedSession() as session:
        for event, elem in tree.iterparse(sys.stdin):
            # check to see if we've reached the end of a document tag
            if elem.tag in CATEGORIES:
                # store attribute info, do preprocessing if necessary
                title = data.get('title')
                year = data.get('year')
                author_names = data.get('author_names', [])
                journal_name = data.get('journal_name')
                conference_name = data.get('conference_name')

                # clear out attribute info, and write
                data = {}
                doc = db.Document(title=title, year=year)
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

                session.add(doc)
                count += 1
                # commit changes periodically
                if (count % 1000 == 0):
                    session.commit()
                    sys.stdout.write('\rcreated %s records' % (count))
                    sys.stdout.flush()
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
        session.commit()
    print
    print 'finished, created %s records' % count
