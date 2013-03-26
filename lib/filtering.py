debug = False
def top(similarity_matrix, indices, top_limit=500, load_factor=8):
    """ indices should contain phrases for every row and col in matrix,
    and they should be in order of decreasing ranking
    top_limit is the number that should be counted as top phrases"""
    phrase_pairs = {}
    found = set()
    for index in xrange(min(top_limit, len(indices))):
        phrase = indices[index]
        row = similarity_matrix[index, :top_limit]
        pairs = [(indices[i], s) for (i, s) in enumerate(row) if s > 0]
        top = sorted(pairs, key=lambda pair: pair[1], reverse=True)
        phrase_pairs[phrase] = top[:load_factor]
        for p, s in phrase_pairs[phrase]:
            found.add(p)

    if debug:
        print "filtered %d phrases" % len(found)
    return phrase_pairs

def pull_lesser(similarity_matrix, indices, top_limit=90, load_factor=10):
    """ indices should contain phrases for every row and col in matrix,
    and they should be in order of decreasing ranking
    top_limit is the number that should be counted as top phrases"""
    phrase_pairs = {}
    found = set()
    total_len = 0
    for index in xrange(min(top_limit, len(indices))):
        phrase = indices[index]
        row = similarity_matrix[index, :]
        pairs = [(indices[i], s) for (i, s) in enumerate(row) if s > 0]
        top = sorted(pairs, key=lambda pair: pair[1], reverse=True)
        phrase_pairs[phrase] = top[:load_factor]
        total_len += len(phrase_pairs[phrase])
        found.add(phrase)
        for p, s in phrase_pairs[phrase]:
            found.add(p)
    if debug:
        print "filtered %d phrases" % len(found)
        print "average phrases / top phrase %f" % (float(total_len) / top_limit)
    return phrase_pairs

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
