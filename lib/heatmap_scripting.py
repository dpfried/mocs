from web_interface import *
from maps.models import Task, Basemap, Heatmap

basemap_query = create_query(author='Kwan-Liu Ma',
                             journal=None,
                             conference=None)
basemap_starting_year = 1950
basemap_ending_year = 2013
basemap_sample_size = 30000
basemap_term_type = TermExtraction.Phrases
documents = filter_query(basemap_query, dirty=False,
                            starting_year=basemap_starting_year,
                            ending_year=basemap_ending_year,
                            sample_size=basemap_sample_size,
                            model=basemap)
extracted_terms = extract_terms(documents, basemap_term_type)

for ranking_algorithm in ranking_fns:
    for similarity_algorithm in similarity_fns:
        for filtering_algorithm in filtering_fns:
    flattened = flatten(extracted_terms)
    # TODO HERE
    set_status('ranking terms', model=model)
    if start_words is not None:
        # start words should be a list like ["machine learning", "artificial intelligence"]
        start_words = [tuple(s.split()) for s in start_words]
        ranked_phrases, phrase_frequencies = call_rank(ranking_algorithm, flattened, number_of_terms, start_words=start_words, model=model)
    else:
        ranked_phrases, phrase_frequencies = call_rank(ranking_algorithm, flattened, number_of_terms, model=model)
    if simplify_terms:
        structured_nps = simplification.term_replacement(structured_nps, ranked_phrases)
    set_status('calculating similarity', model=model)
    sim_matrix, phrase_lookups = call_similarity(similarity_algorithm, structured_nps, ranked_phrases, model=model, status_callback=lambda s: set_status(s, model=model))
    phrase_pairs = call_filter(filtering_algorithm,  sim_matrix, phrase_lookups, model=model)
    normed = similarity.similarity_dict_to_distance(phrase_pairs)
    # build set of terms in graph
    graph_terms = set()
    for term, lst in normed.items():
        graph_terms.add(term)
        graph_terms.update(term for term, val in lst)
    return normed, graph_terms, phrase_frequencies
