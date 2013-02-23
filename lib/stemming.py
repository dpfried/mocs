from nltk.stem import PorterStemmer

stemmer = None

def stem_phrase(phrase):
    global stemmer
    if not stemmer:
        stemmer = PorterStemmer()
    return map(stemmer.stem, phrase)

def stem_document(document):
    return map(stem_phrase, document)
