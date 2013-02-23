def load_nps(starting_year, ending_year, row_offset, row_limit, sampling_rate):
    query =  db.Document.query.filter(db.Document.clean == True)\
                              .filter(db.Document.year <= ending_year)\
                              .filter(db.Document.year >= starting_year)\
                              .slice(row_offset, row_offset + row_limit)
    sampled = sample_iterable(query, sampling_rate)
    return [doc.terms_list() for doc in sampled]

ranking_fns = [ranking.tfidf, ranking.cnc_bigrams, ranking.cnc_unigrams, ranking.tf]
def call_rank(ranking_index, flattened, n_large, start_words=[]):
    """ranking_index: 0 = TFIDF; 1 = C-value; 2 = C-value + Unigrams; 3 = TF"""
    ranking_fn = ranking_fns[ranking_index]
    if debug:
        print 'ranking with %s' % ranking_fn
    scored_phrases = ranking_fn(flattened)
    if debug:
        print 'ordering'
    ordered_phrases = sorted(scored_phrases.iteritems(),
                             key=lambda p: p[1], reverse=True)

#    ordered_fname ='../phrase_lists/%s.phrases' % ranking_index
#    print 'writing ordered phrases to file %s' % ordered_fname
#    with open(ordered_fname, 'w') as f:
#        for o in ordered_phrases[:n_large]:
#            f.write('%s\n' % str(o))
    if debug:
        print 'mapping'
    ranked_phrases = [p[0] for p in ordered_phrases]

    if debug:
        print 'trimming large'
    large_phrases = ranked_phrases[:n_large]

    if start_words:
        if debug:
            print 'looking for start words', start_words
        found_start_words = []
        for start_word in start_words:
            matches = (ranked_phrase for ranked_phrase in ranked_phrases if start_word in sub_lists(ranked_phrase, proper=False))
            try:
                word = matches.next()
                if word not in large_phrases:
                    found_start_words.append(word)
            except StopIteration:
                if debug:
                    print 'start word %s not found' % start_word
            if debug:
                print 'found start words', found_start_words

        return found_start_words + large_phrases
    else:
        return large_phrases
call_rank.functions = ranking_fns
call_rank.default = ranking_fns.index(ranking.cnc_bigrams)

similarity_fns = [similarity.lsa, similarity.jaccard_full, similarity.jaccard_partial, similarity.distributional_js]
def call_similarity(similarity_index, structured_nps, phrases):
    """
    similarity_index: 0 = LSA (w/ Cosine similarity); 1 = Jaccard; 2 = Jaccard (partial match); 3 = Distributional similarity (w/ Jensen-Shannon divergence)
    """
    # similarity_fns = [similarity.lsa, similarity.jaccard_full, similarity.jaccard_partial]
    similarity_fn = similarity_fns[similarity_index]
    if debug:
        print 'calculating similarity with %s' % similarity_fn
    sim_matrix, phrases = similarity_fn(structured_nps, phrases)
    return sim_matrix, phrases
call_similarity.functions = similarity_fns
call_similarity.default = similarity_fns.index(similarity.jaccard_partial)

filtering_fns = [filtering.top, filtering.pull_lesser, filtering.hybrid]
def call_filter(filter_index, sim_matrix, phrases, top_limit_override=None):
    """
    filter_index: 0 = Top; 1 = Pull in Lesser Terms; 2 = Take Top and Fill w/ Lesser
    """
    filtering_fn = filtering_fns[filter_index]
    if debug:
        print 'filtering and getting pairwise with %s' % filtering_fn
    if top_limit_override:
        phrase_pairs = filtering_fn(sim_matrix, phrases, top_limit=top_limit_override)
    else:
        phrase_pairs = filtering_fn(sim_matrix, phrases)
    return phrase_pairs
call_filter.functions = filtering_fns
call_filter.default = filtering_fns.index(filtering.pull_lesser)
