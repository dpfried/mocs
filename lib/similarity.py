import numpy as np
from utils import hashable
from partial_match_dict import PartialMatchDict
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
from scipy.sparse import lil_matrix, csc_matrix
from numpy import log
# from sparsesvd import sparsesvd

debug = False

def similarity_to_distance(sim_matrix, base=1):
    """ convert a similarity matrix, with values ranging from 0 (not similar)
    to 1 (completely similar) to a distance matrix, using Sankar's formula """
    return 10 * (base / (base + sim_matrix))

def normalize(matrix):
    """ ensure the max entry in the matrix is 1 """
    return matrix / matrix.max()

def process_dict(pairs_by_phrase):
    max_similarity = 0
    for phrase, pairs in pairs_by_phrase.iteritems():
        if pairs == []:
            max_in_lst = 0
        else:
            max_in_lst = max([pair[1] for pair in pairs])
        max_similarity = max(max_similarity, max_in_lst)
    if debug:
        print max_similarity

    mapped = {}
    for phrase, pairs in pairs_by_phrase.iteritems():
        mapped[phrase] = [(p, similarity_to_distance(s / max_similarity)) \
                          for p, s in pairs]
    return mapped


def kl_div(A,B):
    """ Kullback-Leibler divergence between two discrete probability
    distributions, represented as numpy vectors """
    if debug:
        print np.divide(A, B)
    divided = np.divide(A, B).todense()
    Adense = A.todense()
    mask = Adense != 0
    return np.sum(np.multiply(Adense[mask], np.log(divided[mask])))

def js_div(A, B):
    """ Jensen-Shannon divergence between two discrete probability
    distributions, represented as numpy vectors """
    norm_A = A / A.sum()
    norm_B = B / B.sum()
    M = (norm_A+norm_B)/2
    return 0.5 * (kl_div(norm_A,M)+kl_div(norm_B,M))

def _pmi_on_row(A, B):
    N = A.shape[0]
    p_a = float((A != 0).sum()) / N
    p_b = float((B != 0).sum()) / N

    p_ab = float(((A != 0) & (B != 0)).sum()) / N

    return log(p_ab) - log(p_a) - log(p_b)

def pointwise_mutual_information(structured_phrases, phrases_to_score):
    M, indices, phrases = _document_matrix(structured_phrases, phrases_to_score)

    if debug:
        print 'pairwise distance'
    pairwise_distance = pdist(M, metric=_pmi_on_row)
    if debug:
        print 'pairwise similarity'
    pairwise_similarity = squareform(1 - pairwise_distance)
    return pairwise_similarity, phrases

def distributional_js(structured_phrases, phrases_to_score):
    """ Calculate distributional similarity between phrases_to_score using the
    contexts in structured_phrases and Jensen-Shannon divergence as the distance
    metric between contexts """
    flattened = [phrase for doc in structured_phrases for phrase in doc]

    full_phrases = {}
    full_indices = {}

    N = 0
    for phrase in flattened + phrases_to_score:
        if phrase not in full_indices:
            full_indices[phrase] = N
            full_phrases[N] = phrase
            N += 1

    co_occurrences = lil_matrix((N, N))

    if debug:
        print 'counting cooccurrences'
    # take each document
    for doc_phrases in structured_phrases:
        # take all phrases within this document
        for i in range(len(doc_phrases)):
            index1 = full_indices[doc_phrases[i]]
            for j in range(i, len(doc_phrases)):
                index2 = full_indices[doc_phrases[j]]
                if debug:
                    if index1 >= N:
                        print index1
                    if index2 >= N:
                        print index2
                co_occurrences[index1,index2] += 1
                co_occurrences[index2,index1] += 1
    if debug:
        print 'done'
        print 'calc squareform'

    score_phrases = {}
    score_indices = {}

    score_set = set(score_phrases.values())
    full_set = set(full_phrases.values())

    if debug:
        if full_set.intersection(score_set) != score_set:
            print score_set.difference(full_set.intersection(score_set))
            print full_set.intersection(score_set).difference(score_set)
        else:
            print 'sets ok'

    M = len(phrases_to_score)
    for i, phrase in enumerate(phrases_to_score):
        score_indices[phrase] = i
        score_phrases[i] = phrase

    pairwise_distances = lil_matrix((M, M))
    if debug:
        print 'building rows'
    rows = [co_occurrences.getrow(full_indices[score_phrases[n]]) for n in range(M)]
    if debug:
        print 'done'
    for i in range(M):
        if debug:
            print i
        most_similar = None
        most_similar_val = 10
        for j in range(i+1, M):
            val = js_div(rows[i], rows[j])
            if val < most_similar_val:
                most_similar = j
                most_similar_val = val
            pairwise_distances[i,j] = val
            pairwise_distances[j,i] = val
        if debug:
            if most_similar:
                print i, most_similar
                print most_similar_val, score_phrases[i], score_phrases[most_similar]
    return np.asarray(pairwise_distances.todense()), score_phrases

def _document_matrix(structured_phrases, phrases_to_score):
    indices = {}
    phrases = {}

    for i, phrase in enumerate(phrases_to_score):
        indices[phrase] = i
        phrases[i] = phrase

    # M = np.zeros((len(phrases_to_score), len(structured_phrases)))
    # sparsesvd requires csc format of sparse matrix
    M = lil_matrix((len(phrases_to_score), len(structured_phrases)))

    if debug:
        print 'document matrix'
    for doc_index, doc in enumerate(structured_phrases):
        for phrase in doc:
            h = hashable(phrase)
            if h in indices:
                M[indices[hashable(phrase)], doc_index] += 1
    return M.todense(), indices, phrases


def lsa(structured_phrases, phrases_to_score):
    """ Calculate similarity between phrases_to_score using structured_phrases to
    build term-document matrix and latent semantic analysis for similarity """
    M, indices, phrases = _document_matrix(structured_phrases, phrases_to_score)
    # would performing TFIDF here improve performance?

    if debug:
        print 'svd'
    U, S, V = np.linalg.svd(M,full_matrices=False)
    # sparsesvd is slow as hell
    # U, S, V = sparsesvd(M, len(phrases_to_score))

    if debug:
        print 'pairwise distance'
    pairwise_distance = pdist(np.dot(U, np.diag(S)), metric='cosine')
    if debug:
        print 'pairwise similarity'
    pairwise_similarity = squareform(1 - pairwise_distance)
    return pairwise_similarity, phrases

def jaccard_partial(structured_phrases, phrases_to_score):
    return jaccard(structured_phrases, phrases_to_score, partial=True)

def jaccard_full(structured_phrases, phrases_to_score):
    return jaccard(structured_phrases, phrases_to_score, partial=False)

def jaccard(structured_phrases, phrases_to_score, partial=False):
    """ calculate jaccard similarity between phrases_to_score, using
    structured_phrases to determine cooccurrences. For phrases `a' and `b', let
    A be the set of documents `a' appeared in, and B be the set of documents
    `b' appeared in.  Then the Jaccard similarity of `a' and `b' is Similarity
    value of two phrases is |A intersect B| / |A union B|.
    Setting partial to true allows partial phrase matching: two phrases are the
    same if they have any common subsequence of words. Very slow.
    """

    # indicies will index into our union and intersection arrays
    phrases = {}
    if partial:
        indices = PartialMatchDict()
    else:
        indices = {}

    for i, phrase in enumerate(phrases_to_score):
        indices[phrase] = i
        phrases[i] = phrase

    N = len(phrases_to_score)

    phrase_count = np.zeros(N)
    intersection = np.zeros(shape=(N, N))

    if debug:
        print 'counting collocations'
    # take each document
    for doc_phrases in structured_phrases:
        if debug:
            print 'processing document %s' % doc_phrases
        # take all phrases within this document
        for i in range(len(doc_phrases)):
            np1 = tuple(doc_phrases[i])
            if debug:
                print 'processing tuple' , np1
            if np1 in indices:
                if debug:
                    print 'found' , np1
                # this phrase is important enough to count
                if partial:
                    matches1 = indices[np1]
                else:
                    matches1 = set()
                    matches1.add(indices[np1])
                if debug:
                    print 'matches:' , matches1

                for index1 in matches1:
                    phrase_count[index1] += 1

                for k in range(i + 1, len(doc_phrases)):
                    np2 = tuple(doc_phrases[k])
                    if debug:
                        print '\tprocessing sub-tuple' , np2
                    if np2 in indices:
                        if debug:
                            print '\tfound' , np2
                        # this np is important enough to count
                        if partial:
                            matches2 = indices[np2]
                        else:
                            matches2 = set()
                            matches2.add(indices[np2])
                        for index1 in matches1:
                            for index2 in matches2:
                                if index2 != index1:
                                    intersection[index1][index2] += 1
                                    intersection[index2][index1] += 1
    # use inclusion exclusion
    if debug:
        print 'jaccard matrix'
    union = np.array([phrase_count,]*N) + np.array([phrase_count,]*N).transpose() - intersection
    jaccard = intersection / union
    return jaccard, phrases

# Calculate based on term similarity. conditional probability of one phrase given another or mutual info
