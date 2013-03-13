from nltk.probability import FreqDist
from nltk.util import ngrams
import utils
from math import log
import nltk
from mocs_config import NLTK_DATA_PATH

if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_PATH)
zuni_path = '/var/www/zuni/html/mocs/nltk_data'
if zuni_path not in nltk.data.path:
    nltk.data.path.append(zuni_path)

class CorpusRanker:
    def __init__(self, corpus=nltk.corpus.brown.words(), ngram_range=(1,6)):
        corpus_ngrams = {}
        for n in range(*ngram_range):
            corpus_ngrams[n] = FreqDist(ngrams(corpus, n))
        self.corpus_ngrams = corpus_ngrams

    def score(self, phrase_tuple, tf):
        return float(tf) / (1 + self.frequency(phrase_tuple))

    def frequency(self, phrase_tuple):
        length = len(phrase_tuple)
        if length in self.corpus_ngrams:
            return self.corpus_ngrams[length][phrase_tuple]
        else:
            return 0

def tf(phrase_lists):
    phrase_frequencies = FreqDist(tuple(p) for p in phrase_lists)
    scored = {}
    for phrase, freq in phrase_frequencies.iteritems():
        scored[phrase] = freq
    return scored, phrase_frequencies

def tfidf(phrase_lists, corpus=nltk.corpus.brown.words(), ngram_range=(1, 6)):
    ranker = CorpusRanker(corpus, ngram_range)
    phrase_frequencies = FreqDist(tuple(p) for p in phrase_lists)
    phrase_scores = {}
    for phrase, freq in phrase_frequencies.iteritems():
        phrase_scores[phrase] = ranker.score(phrase, freq)
    return phrase_scores, phrase_frequencies

def cnc_unigrams(phrase_lists):
    return cnc(phrase_lists, include_unigrams=True)

def cnc_bigrams(phrase_lists):
    return cnc(phrase_lists, include_unigrams=False)

def cnc_unweighted(phrase_lists):
    return cnc(phrase_lists, weight_by_length=False)

def cnc(phrase_lists, c_value_threshold = 0, include_unigrams = False, weight_by_length=True):
    """given a list of phrases, run the cnc algorithm and return a dictionary of word, c-value (ranking) pairs"""
    frequency_dists_by_length = {}
    for phrase in phrase_lists:
        l = len(phrase)
        if l not in frequency_dists_by_length:
            frequency_dists_by_length[l] = FreqDist()
        frequency_dists_by_length[l].inc(tuple(phrase))

    # word -> C-value(word)
    phrase_scores = {}

    # word -> num occurrences(word)
    phrase_frequencies = FreqDist()

    # word -> (t(word), c(word))
    sub_phrase_scores = {}

    # traverse from longest phrases to shortest
    for length, frequency_dist in sorted(frequency_dists_by_length.items(), \
                                         key=lambda pair: pair[0], reverse=True):
        # update global frequency counts with all counts of this length
        phrase_frequencies.update(frequency_dist)
        # within each phrase length, traverse from most common phrases to least
        for phrase, frequency in frequency_dist.iteritems():
            if phrase in sub_phrase_scores:
                t, c = sub_phrase_scores[phrase]
                subtractive = 1.0 / c * t
            else:
                subtractive = 0
            if weight_by_length:
                if include_unigrams:
                    weight = log(length + 1, 2)
                else:
                    weight = log(length, 2)
            else:
                weight = 1
            c_value = weight * (frequency - subtractive)
            if c_value >= c_value_threshold:
                phrase_scores[phrase] = c_value
                for sub_phrase in utils.sub_lists(phrase):
                    if sub_phrase in sub_phrase_scores:
                        t, c = sub_phrase_scores[sub_phrase]
                    else:
                        t, c = 0, 0
                    sub_phrase_scores[sub_phrase] = t + frequency, c + 1
    return phrase_scores, phrase_frequencies
