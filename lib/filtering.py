debug = False

def phrase_pairs(row_accessor, indices, top_limit, load_factor):
    phrase_pairs = {}
    for index in xrange(min(top_limit, len(indices))):
        phrase = indices[index]
        row = row_accessor(index)
        pairs = [(indices[i], s) for (i, s) in enumerate(row) if s > 0]
        top = sorted(pairs, key=lambda pair: pair[1], reverse=True)
        # just include edges
        # that we haven't processed yet
        # avoid double counts
        phrase_pairs[phrase] = [(p, score) for (p, score) in top[:load_factor]
                                if (p not in phrase_pairs)
                                or (phrase not in [q for (q, s) in phrase_pairs[p]])]
        # processed_phrases.add(phrase)
    return phrase_pairs

def top(similarity_matrix, indices, top_limit=500, load_factor=8):
    """ indices should contain phrases for every row and col in matrix,
    and they should be in order of decreasing ranking
    top_limit is the number that should be counted as top phrases"""
    return phrase_pairs(lambda index: similarity_matrix[index, :top_limit], indices, top_limit, load_factor)

def pull_lesser(similarity_matrix, indices, top_limit=90, load_factor=8):
    """ indices should contain phrases for every row and col in matrix,
    and they should be in order of decreasing ranking
    top_limit is the number that should be counted as top phrases"""
    return phrase_pairs(lambda index: similarity_matrix[index, :], indices, top_limit, load_factor)

def hybrid(similarity_matrix, indices, top_limit=100, load_factor=9):
    phrase_pairs = {}
    N = min(top_limit, len(indices))
    top_set = set([indices[i] for i in xrange(N)])
    for index in xrange(N):
        phrase = indices[index]
        row = similarity_matrix[index, :]
        nonzero_pairs = [(indices[i], s) for (i, s) in enumerate(row) if s > 0]
        nonzero_top_pairs = [(i, s) for (i, s) in nonzero_pairs if i in top_set]
        nonzero_bot_pairs = [(i, s) for (i, s) in nonzero_pairs if i not in top_set]
        top = sorted(nonzero_top_pairs, key=lambda pair: pair[1], reverse=True)[:load_factor/2] \
                + sorted(nonzero_bot_pairs, key=lambda pair:pair[1], reverse=True)[:load_factor/2]
        phrase_pairs[phrase] = top
    return phrase_pairs
