#!/usr/bin/python
import pickle
from utils import sub_lists
import database as db
import filtering
# import pickle
import ranking
import similarity
import simplification
from mocs_config import GRAPHVIZ_PARAMS
from subprocess import Popen, PIPE
from re import sub, search
from collections import Counter
from sqlalchemy.sql.expression import func
from status import set_status
from utils import flatten, hashable
from chunking import STOP_WORDS
from nltk.tokenize import word_tokenize

debug = False

USE_SFDP_FOR_LAYOUT = False

# a regular expression to extract width and height from the svg, and then
# eliminate these attributes
SVG_DIMENSION_REPLACEMENT = ('<svg width="(.*)pt" height="(.*)pt"', '<svg')

def filter_query(query, dirty=False, starting_year=None, ending_year=None,
                 sample_size=None, model=None):
    filtered = query
    if not dirty:
        filtered = query.filter(db.Document.clean == True)
    if ending_year is not None:
        filtered = filtered.filter(db.Document.year <= ending_year)
    if starting_year is not None:
        filtered = filtered.filter(db.Document.year >= starting_year)
    if model is not None:
        documents_in_set = filtered.count()
        model.documents_in_set = documents_in_set
        set_status('%d documents met filtering criteria' % documents_in_set)
    if sample_size is not None:
        filtered = filtered.order_by(func.rand()).limit(sample_size)
    if model is not None:
        documents_sampled = filtered.count()
        model.documents_sampled = documents_sampled
        set_status('%d documents were sampled' % documents_sampled)
    return filtered

class TermExtraction:
    '''hacky enum for use by extract_terms'''

    def phrases(document):
        return document.terms_list()

    def all_words(document):
        return [[word] for word in word_tokenize(document.title.lower())
                if word not in STOP_WORDS]

    def words_from_phrases(document):
        return [[word] for word in flatten(document.terms_list())
                if word not in STOP_WORDS]

    Phrases, AllWords, WordsFromPhrases = range(3)
    names = ['phrases', 'all_words', 'words_from_phrases']
    functions = [phrases, all_words, words_from_phrases]

def extract_terms(documents, term_type):
    return map(TermExtraction.functions[term_type], documents)

def calculate_heatmap_values(heatmap_terms, graph_terms, model=None):
    """returns a dictionary of term -> intensity values for the
    terms in documents in heatmap_terms (which should be an iterable
    of term tuples) that are also in the set
    graph_terms"""
    term_counts = Counter()
    for term in heatmap_terms:
        if hashable(term) in graph_terms:
            term_counts[hashable(term)] += 1
    # term_counts = Counter(term for term in heatmap_terms if hashable(term) in graph_terms)
    return term_counts

def create_query(author=None, conference=None, journal=None):
    query = db.Document.query
    if author:
        query = db.Author.filter_document_query(query, author)
    if journal:
        query = db.Journal.filter_document_query(query, journal)
    if conference:
        query = db.Conference.filter_document_query(query, conference)
    return query

ranking_fns = [ranking.tfidf, ranking.cnc_bigrams, ranking.cnc_unigrams, ranking.tf]
ranking_fn_names = ['TF/ICF', 'C-Value', 'C-Value with Unigrams', 'Term Frequency']
def call_rank(ranking_index, flattened, n_large, start_words=[], model=None):
    """ranking_index: 0 = TFIDF; 1 = C-value; 2 = C-value + Unigrams; 3 = TF"""
    ranking_fn = ranking_fns[ranking_index]
    ranking_fn_name = ranking_fn_names[ranking_index]
    set_status('ranking with %s' % ranking_fn_name, model=model)
    if debug:
        print 'ranking with %s' % ranking_fn_name
    scored_phrases, phrase_frequencies = ranking_fn(flattened)
    set_status('ordering', model=model)
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

        top_phrases = found_start_words + large_phrases
    else:
        top_phrases = large_phrases

    filtered_frequencies = dict((phrase, freq) for (phrase, freq) in phrase_frequencies.items() if phrase in top_phrases)
    return top_phrases, filtered_frequencies
call_rank.functions = ranking_fns
call_rank.default = ranking_fns.index(ranking.cnc_bigrams)

similarity_fns = [similarity.lsa, similarity.jaccard_full, similarity.jaccard_partial, similarity.distributional_js]
similarity_fn_names = ['LSA', 'Jaccard Coefficient', 'Partial Match Jaccard Coefficient', 'Distributional JS']
def call_similarity(similarity_index, structured_nps, phrases, model=None, status_callback=None):
    """
    similarity_index: 0 = LSA (w/ Cosine similarity); 1 = Jaccard; 2 = Jaccard (partial match); 3 = Distributional similarity (w/ Jensen-Shannon divergence)
    """
    # similarity_fns = [similarity.lsa, similarity.jaccard_full, similarity.jaccard_partial]
    similarity_fn = similarity_fns[similarity_index]
    set_status('calculating similarity with %s' % similarity_fn, model=model)
    sim_matrix, phrases = similarity_fn(structured_nps, phrases, status_callback=status_callback)
    # with open('/tmp/sim.pickle', 'w') as f:
    #     pickle.dump(sim_matrix, f)
    return sim_matrix, phrases
call_similarity.functions = similarity_fns
call_similarity.default = similarity_fns.index(similarity.jaccard_partial)

filtering_fns = [filtering.top, filtering.pull_lesser, filtering.hybrid]
filtering_fn_names = ['Top Terms Only', 'Pull Lesser Terms', 'Hybrid']
def call_filter(filter_index, sim_matrix, phrases, top_limit_override=None, model=None):
    """
    filter_index: 0 = Top; 1 = Pull in Lesser Terms; 2 = Take Top and Fill w/ Lesser
    """
    filtering_fn = filtering_fns[filter_index]
    set_status('filtering and getting pairwise with %s' % filtering_fn, model=model)
    if top_limit_override:
        phrase_pairs = filtering_fn(sim_matrix, phrases, top_limit=top_limit_override)
    else:
        phrase_pairs = filtering_fn(sim_matrix, phrases)
    return phrase_pairs
call_filter.functions = filtering_fns
call_filter.default = filtering_fns.index(filtering.pull_lesser)

def function_help(calling_function):
    """can be called on the call_* functions to get a list of the different algorithms they can use"""
    return '\n'.join([str(index) + ':' + str(fn)
                      for index, fn in enumerate(calling_function.functions)])

def graphviz_command(sfdp='sfdp', gvmap='gvmap', gvpr='gvpr', labels_path='map/viz/labels.gvpr', neato='neato', file_format='svg'):
    return "%s -c -f %s | %s -Goverlap=prism -Goutputorder=edgesfirst -Gsize=60,60! | %s -e  -s -4 | %s -Gforcelabels=false -Ecolor=grey  -Gsize=60,60! -n2 -T%s" % (gvpr, labels_path, sfdp if USE_SFDP_FOR_LAYOUT else neato, gvmap, neato, file_format)

def strip_dimensions(svg):
    """having width and height attributes as well as a viewbox will cause openlayers to not display the svg propery, so we strip those attributes out"""
    match_re, replacement = SVG_DIMENSION_REPLACEMENT
    try:
        width, height = map(float, search(match_re, svg).groups())
    except Exception:
        width, height = 0.0, 0.0
    return sub(match_re, replacement, svg, count=1), width, height


def map_representation(structured_nps, start_words=None, ranking_algorithm=1,
                       similarity_algorithm=2, filtering_algorithm=1,
                       number_of_terms=1000, simplify_terms=False, model=None):
    """returns a pair similarity dictionary for the map and set of terms in the map. Heatmap can
    be calculated seperately and then overlaid. Will need to convert dictionary representation
    to dot file format"""
    flattened = flatten(structured_nps)
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
    # with open('/tmp/sim_matrix.pickle', 'w') as f:
    #     pickle.dump(sim_matrix, f)
    # with open('/tmp/phrase_lookups.pickle', 'w') as f:
    #     pickle.dump(phrase_lookups, f)
    phrase_pairs = call_filter(filtering_algorithm,  sim_matrix, phrase_lookups, model=model)
    normed = similarity.similarity_dict_to_distance(phrase_pairs)
    # build set of terms in graph
    graph_terms = set()
    for term, lst in normed.items():
        graph_terms.add(term)
        graph_terms.update(term for term, val in lst)
    return normed, graph_terms, phrase_frequencies


def call_graphviz(map_string, file_format='svg', model=None):
    """map_string should be a string in the dot file format, which the pipeline will be called on. Output in format file_format"""
    set_status('drawing graph', model=model)
    proc = Popen(graphviz_command(file_format=file_format, **GRAPHVIZ_PARAMS), stdout=PIPE, stdin=PIPE, shell=True)
    map_out, map_err = proc.communicate(input=map_string)
    return map_out
