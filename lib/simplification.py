from itertools import combinations
"""module to take documents (a list of list of phrases) and a short list of
phrases, and replace the phrases in the document with a shorter phrase, if the
shorter phrase is contained in the longer phrase. Intention was to have more
phrase commonalities for similarity algorithms to use, haven't done enough
testing to see if this makes a large difference. Code is fast, though"""

'''
# was going to use this to check each phrase in short list against each phrase in doc,
# but figured checking subsequences of phrases in docs against short list would be quicker
def is_subsequence(needle, haystack):
    """ is needle a contiguous, non-empty subsequence of haystack? """
    if not needle or not haystack:
        return False
    for position in range(len(haystack) - len(needle) + 1):
        for offset in range(len(needle)):
            if needle[offset] != haystack[position + offset]:
                break
            elif offset == len(needle) - 1:
                return True
    return False
'''

def _subsequences(sequence):
    # calculate possible indices 
    split_points = ((a, b) for (a, b) in combinations(range(len(sequence) + 1), 2) if a < b)
    # return subseqs in order of size, increasing
    for a, b in sorted(split_points, key=lambda (a, b): b - a):
        yield sequence[a:b]

def _rewrite_phrase(phrase, short_phrases):
    # don't rewrite the phrase if it's in short_phrases
    if phrase in short_phrases:
        return phrase
    # check subsequences of phrase to see if any are in short_phrases
    for s in _subsequences(phrase):
        if s in short_phrases:
            return s
    # if none were, return the original phrase
    return phrase

def _rewrite_doc(doc, short_phrases):
    return [_rewrite_phrase(phrase, short_phrases) for phrase in doc]

def phrase_replacement(structured_phrases, short_phrases):
    """replaces phrases in structred_phrases with phrases from short_phrases if the short phrase is contained in the longer phrase"""
    short_set = set(short_phrases)
    return [_rewrite_doc(doc, short_set) for doc in structured_phrases]
