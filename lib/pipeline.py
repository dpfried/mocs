#!/usr/bin/python
from utils import sub_lists
import database as db
import filtering
# import pickle
import ranking
import similarity
import simplification
import write_dot
import config
from subprocess import Popen, PIPE
from re import sub
from utils import flatten
from collections import Counter
from math import log
from sqlalchemy.sql.expression import func
from status import set_status
from celery import task
from maps.models import Task

debug = False


def filter_query(query, dirty=False, starting_year=None, ending_year=None,
                 sample_size=None, model=None):
    if debug:
        print 'before filtering %d' % query.count()
    if not dirty:
        filtered = query.filter(db.Document.clean == True)
    else:
        filtered = query
    if debug:
        print 'after cleaning %d' % filtered.count()
    if ending_year is not None:
        filtered = filtered.filter(db.Document.year <= ending_year)
    if starting_year is not None:
        filtered = filtered.filter(db.Document.year >= starting_year)
    if debug:
        print 'before sampling %d' % filtered.count()
    if sample_size is not None:
        filtered = filtered.order_by(func.rand()).limit(sample_size)

    return [doc.terms_list() for doc in filtered]

'''
def plot_heatmap_values(heatmap_query, graph_terms, title):
    term_counts = Counter(flatten(doc.terms_list() for doc in heatmap_query))
    if debug:
        print 'number of terms in heatmap = %d' % len(term_counts)
        print 'len graph_terms = %d' % len(graph_terms)

    heatmap_counts = [(term, log(count)) for term, count in term_counts.items() if term in graph_terms]
    plt.bar(range(len(heatmap_counts)), map(lambda pair: pair[1], heatmap_counts), width=1.0)
    plt.title(title)
    plt.show()
    '''

def calculate_heatmap_values(heatmap_terms, graph_terms, model=None):
    """returns a dictionary of term -> intensity values for the
    terms in documents in heatmap_terms (which should be an iterable
    of term tuples) that are also in the set
    graph_terms"""
    term_counts = Counter(heatmap_terms)
    # term_counts = Counter(flatten(doc.terms_list() for doc in heatmap_query))
    if debug:
        print 'number of terms in heatmap = %d' % len(term_counts)
        print 'len graph_terms = %d' % len(graph_terms)

    #heatmap_counts = [(term, log(count)) for term, count in term_counts.items() if term in graph_terms]
    heatmap_counts = [(term, log(count)) for term, count in term_counts.items() if term in graph_terms]
    if debug:
        print 'len intersection = %d' % len(heatmap_counts)
    # make the largest count 1, and reduce other counts proportionately
    # alternatively, could divide by the sum, but then might be harder to see colors
    norm = max([count for term, count in heatmap_counts])
    return dict([(term, float(count)/norm)
                 for term, count in heatmap_counts])

@task()
def request_task(task_id, **kw_args):
    print 'requesting task', task_id
    task = Task.objects.get(id=task_id)
    basemap = task.basemap
    print 'after getting task and basemap'
    return make_map(basemap, **kw_args)

def make_map(basemap, query=db.Document.query, heatmap_query=None, only_terms=False, file_format='svg',
             starting_year=2000, ending_year=2013, sample_size=None,
             should_filter_query=True, **params):

    set_status('querying docs', model=basemap)
    set_status('%d documents found' % query.count(), model=basemap)
    if should_filter_query:
        terms_in_docs = filter_query(query, starting_year=starting_year,
                                     ending_year=ending_year,
                                     sample_size=sample_size)
    else:
        terms_in_docs = [doc.terms_list() for doc in query]
    set_status('%d documents sampled' % (len(terms_in_docs),), model=basemap)

    map_dict, graph_terms = map_representation(terms_in_docs, model=basemap, **params)

    if heatmap_query is not None:
        heatmap_terms = flatten(doc.terms_list() for doc in heatmap_query)
        heatmap_vals = calculate_heatmap_values(heatmap_terms, graph_terms)
        # plot_heatmap_values(heatmap_query, graph_terms, 'plot of term freq')
        map_string = write_dot.output_pairs_dict(map_dict,
                                                 enlarge_primary=True,
                                                 heatmap_vals=heatmap_vals)
    else:
        # map_string will be a graphviz-processable string
        map_string = write_dot.output_pairs_dict(map_dict, True)
    # save to database
    basemap.dot_rep = map_string
    basemap.save()
    svg_str = strip_dimensions(call_graphviz(map_string, file_format='svg', model=basemap))
    basemap.svg_rep = svg_str
    set_status('complete', model=basemap)
    basemap.finished = True
    basemap.save()
    return True

def query_for_author(name_like):
    return db.Document.query.join(db.Author, db.Document.authors)\
            .filter(db.Author.name.like(name_like))

def query_for_conference(name_like):
    return db.Document.query.join(db.Conference)\
            .filter(db.Conference.name.like(name_like))

def query_for_journal(name_like):
    return db.Document.query.join(db.Journal)\
            .filter(db.Journal.name.like(name_like))

ranking_fns = [ranking.tfidf, ranking.cnc_bigrams, ranking.cnc_unigrams, ranking.tf]
def call_rank(ranking_index, flattened, n_large, start_words=[], model=None):
    """ranking_index: 0 = TFIDF; 1 = C-value; 2 = C-value + Unigrams; 3 = TF"""
    ranking_fn = ranking_fns[ranking_index]
    set_status('ranking with %s' % ranking_fn, model=model)
    if debug:
        print 'ranking with %s' % ranking_fn
    scored_phrases = ranking_fn(flattened)
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

        return found_start_words + large_phrases
    else:
        return large_phrases
call_rank.functions = ranking_fns
call_rank.default = ranking_fns.index(ranking.cnc_bigrams)

similarity_fns = [similarity.lsa, similarity.jaccard_full, similarity.jaccard_partial, similarity.distributional_js]
def call_similarity(similarity_index, structured_nps, phrases, model=None, status_callback=None):
    """
    similarity_index: 0 = LSA (w/ Cosine similarity); 1 = Jaccard; 2 = Jaccard (partial match); 3 = Distributional similarity (w/ Jensen-Shannon divergence)
    """
    # similarity_fns = [similarity.lsa, similarity.jaccard_full, similarity.jaccard_partial]
    similarity_fn = similarity_fns[similarity_index]
    set_status('calculating similarity with %s' % similarity_fn, model=model)
    sim_matrix, phrases = similarity_fn(structured_nps, phrases, status_callback=status_callback)
    return sim_matrix, phrases
call_similarity.functions = similarity_fns
call_similarity.default = similarity_fns.index(similarity.jaccard_partial)

filtering_fns = [filtering.top, filtering.pull_lesser, filtering.hybrid]
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

def graphviz_command(sfdp='sfdp', gvmap='gvmap', gvpr='gvpr', labels_path='map/viz/labels.gvpr', neato='neato', file_format='svg'):
    # return "%s -Goverlap=prism -Goutputorder=edgesfirst -Gsize=60,60! | %s -e  -s -4 | %s -c -f %s | %s -Gforcelabels=false -Ecolor=grey  -Gsize=60,60! -n2 -T%s" % (sfdp, gvmap, gvpr, labels_path, neato, file_format)
    return "%s -c -f %s | %s -Goverlap=prism -Goutputorder=edgesfirst -Gsize=60,60! | %s -e  -s -4 | %s -Gforcelabels=false -Ecolor=grey  -Gsize=60,60! -n2 -T%s" % (gvpr, labels_path, sfdp, gvmap, neato, file_format)

def strip_dimensions(svg):
    """having width and height attributes as well as a viewbox will cause openlayers to not display the svg propery, so we strip those attributes out"""
    return sub('<svg width=".*" height=".*"', '<svg', svg, count=1)

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
        ranked_phrases = call_rank(ranking_algorithm, flattened, number_of_terms, start_words=start_words, model=model)
    else:
        ranked_phrases = call_rank(ranking_algorithm, flattened, number_of_terms, model=model)
    if simplify_terms:
        structured_nps = simplification.term_replacement(structured_nps, ranked_phrases)
    set_status('calculating similarity', model=model)
    sim_matrix, phrase_lookups = call_similarity(similarity_algorithm, structured_nps, ranked_phrases, model=model, status_callback=lambda s: set_status(s, model=model))
    phrase_pairs = call_filter(filtering_algorithm,  sim_matrix, phrase_lookups, model=model)
    normed = similarity.process_dict(phrase_pairs)
    # build set of terms in graph
    graph_terms = set()
    for term, lst in normed.items():
        graph_terms.add(term)
        graph_terms.update(term for term, val in lst)
    return normed, graph_terms

def call_graphviz(map_string, file_format='svg', model=None):
    """map_string should be a string in the dot file format, which the pipeline will be called on. Output in format file_format"""
    set_status('drawing graph', model=model)
    proc = Popen(graphviz_command(file_format=file_format, **config.GRAPHVIZ_PARAMS), stdout=PIPE, stdin=PIPE, shell=True)
    map_out, map_err = proc.communicate(input=map_string)
    return map_out

def function_help(calling_function):
    """can be called on the call_* functions to get a list of the different algorithms they can use"""
    return '\n'.join([str(index) + ':' + str(fn)
                      for index, fn in enumerate(calling_function.functions)])

def map_args(args):
    """used to filter arguments passed in through a request that should also
    be passed as keyword args to make_map"""
    arg_set = {
        'starting_year':int,
        'ending_year':int,
        'ranking_algorithm':int,
        'similarity_algorithm':int,
        'filtering_algorithm':int,
        'number_of_terms':int,
        'sample_size':int
    }
    pass_args = {}
    for arg, type_ in arg_set.items():
        if arg in args:
            pass_args[arg] = type_(args[arg])
    return pass_args
