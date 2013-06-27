import nltk
import lib.database as db
session = db.Session()
session.query(db.Document)
doc_q = session.query(db.Document)
word_count = nltk.FreqDist()
phrase_count = nltk.FreqDist()
title_word_length = nltk.FreqDist()
title_phrase_length = nltk.FreqDist()
for doc in db.sliced_query(doc_q):
    if not doc.title:
        continue
    words = nltk.tokenize.word_tokenize(doc.title.lower())
    phrases = doc.terms_list()
    for word in words:
        word_count.inc(word)
    for phrase in phrases:
        phrase_count.inc(phrase)
    title_word_length.inc(len(words))
    title_phrase_length.inc(len(phrases))
