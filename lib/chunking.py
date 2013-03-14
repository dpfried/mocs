import nltk

# regular expression to pull noun phrases out of the parse trees
np_grammar = "NP: {(<JJR>|<JJS>|<JJ>|<NN>|<NNS>|<NNP>|<NNPS>)*}"
np_parser = nltk.RegexpParser(np_grammar)

# store stemmer in this global var so we don't have to reload each time
stemmer = None

# exclude phrases containing these words
STOP_WORDS = ['new', 'novel', 'study', 'isbn', '.', '(', ')', '[', ']']

debug = False

def ok_phrase(phrase):
    """check to see if a phrase contains stop words or is just a single character, like ( or )"""
    if len(phrase) == 1 and len(phrase[0]) == 1:
        return False
    for s in STOP_WORDS:
        if s in phrase:
            return False
    return True

def noun_phrases(document, stem=False):
    # document here is a string. Fix this!
    """given a text string, extract the noun phrases from it. Case sensitive,
    so may be best to lowercase Anything Capitalized Like This. If stem,
    will run Porter stemmer to prune words down to base roots"""
    global stemmer
    if not stemmer:
        stemmer = nltk.stem.PorterStemmer()
    flattened = []
    try:
        for sentence in nltk.tokenize.sent_tokenize(document):
            tree = np_parser.parse(nltk.tag.pos_tag(nltk.tokenize.word_tokenize(sentence)))
            nps = [np.leaves() for np in tree.subtrees(lambda tree: tree.node == 'NP')]
            for np in nps:
                if stem:
                    flattened.append([stemmer.stem(tpl[0]) for tpl in np])
                else:
                    flattened.append([tpl[0] for tpl in np])
        return [phrase for phrase in flattened if ok_phrase(phrase)]
    except TypeError:
        if debug:
            print document
