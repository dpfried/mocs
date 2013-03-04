#!/usr/bin/python
from utils import sub_lists
import database as db
import filtering
# import pickle
import ranking
import similarity
import simplification
import write_dot
from mocs_config import GRAPHVIZ_PARAMS
from subprocess import Popen, PIPE
from re import sub
from utils import flatten
from collections import Counter
from sqlalchemy.sql.expression import func
from status import set_status
from celery.task import task
from maps.models import Task
import json

debug = False

USE_SFDP_FOR_LAYOUT = False

def filter_query(query, dirty=False, starting_year=None, ending_year=None,
                 sample_size=None, model=None):
    filtered = query
    if ending_year is not None:
        filtered = filtered.filter(db.Document.year <= ending_year)
    if starting_year is not None:
        filtered = filtered.filter(db.Document.year >= starting_year)
    if model is not None:
        set_status('%d documents met filtering criteria' % filtered.count())
    if sample_size is not None:
        filtered = filtered.order_by(func.rand()).limit(sample_size)
    if model is not None:
        set_status('%d documents were sampled' % filtered.count())

    return [doc.terms_list() for doc in filtered]


def calculate_heatmap_values(heatmap_terms, graph_terms, model=None):
    """returns a dictionary of term -> intensity values for the
    terms in documents in heatmap_terms (which should be an iterable
    of term tuples) that are also in the set
    graph_terms"""
    term_counts = Counter(term for term in heatmap_terms if term in graph_terms)
    return term_counts


def _handle_query(arg_dict, prefix):
    author = '%s_author' % prefix
    conference = '%s_conference' % prefix
    journal = '%s_journal' % prefix
    print prefix

    if arg_dict.get(author):
        name_like = arg_dict.get(author)
        print name_like
        query = db.Author.doc_query(name_like)
    elif arg_dict.get(conference):
        name_like = arg_dict.get(conference)
        print name_like
        query = db.Conference.doc_query(name_like)
    elif arg_dict.get(journal):
        name_like = arg_dict.get(journal)
        print name_like
        query = db.Journal.doc_query(name_like)
    else:
        print 'none'
        query = db.Document.query
    return query


@task()
def request_task(task_id, **kwargs):
    basemap_query = _handle_query(kwargs, 'basemap')
    heatmap_query = _handle_query(kwargs, 'heatmap')

    print 'requesting task', task_id
    task = Task.objects.get(id=task_id)
    print 'after getting task and basemap'
    map_dict, graph_terms = make_basemap(task.basemap, basemap_query, **filter_basemap_args(kwargs))
    print 'making heatmap'
    make_heatmap(task.heatmap, graph_terms, heatmap_query, **filter_heatmap_args(kwargs))
    print 'done'
    return task_id


def make_heatmap(heatmap, graph_terms, heatmap_query, heatmap_starting_year=None,
                 heatmap_ending_year=None, heatmap_sample_size=None):
    def _jsonready_heatmap_vals(heatmap_vals, term_to_str_fn=lambda tpl: ' '.join(tpl)):
        """Input: a dictionary of string tuples to values.

        Val: a dictionary of strings to values, where tuples have been separated by spaces"""
        return [{'term':' '.join(term), 'intensity':count} for (term, count) in heatmap_vals.items()]
    set_status('getting document list', model=heatmap)
    filtered_query = filter_query(heatmap_query, dirty=True,
                                  starting_year=heatmap_starting_year,
                                  ending_year=heatmap_ending_year,
                                  sample_size=heatmap_sample_size,
                                  model=heatmap)
    heatmap_terms = flatten(filtered_query)
    heatmap_vals = calculate_heatmap_values(heatmap_terms, graph_terms)
    heatmap.terms = json.dumps(_jsonready_heatmap_vals(heatmap_vals))
    set_status('heatmap complete', model=heatmap)
    heatmap.finished = True
    heatmap.save()
    return heatmap_vals

def make_basemap(basemap, basemap_query, basemap_starting_year=2000,
                 basemap_ending_year=2013, basemap_sample_size=None, **kwargs):
    print kwargs
    set_status('getting document list', model=basemap)
    terms_in_docs = filter_query(basemap_query, dirty=False,
                                 starting_year=basemap_starting_year,
                                 ending_year=basemap_ending_year,
                                 sample_size=basemap_sample_size,
                                 model=basemap)

    map_dict, graph_terms = map_representation(terms_in_docs, model=basemap, **kwargs)

        # map_string will be a graphviz-processable string
    map_string = write_dot.output_pairs_dict(map_dict, True)
    # save to database
    basemap.dot_rep = map_string
    basemap.save()
    svg_str = strip_dimensions(call_graphviz(map_string, file_format='svg', model=basemap))
    basemap.svg_rep = svg_str
    set_status('basemap complete', model=basemap)
    basemap.finished = True
    basemap.save()
    return map_dict, graph_terms


def query_for_author(name_like):
    return db.Document.query.join(db.Author, db.Document.authors).filter(db.Author.name.like(name_like))


def query_for_conference(name_like):
    return db.Document.query.join(db.Conference).filter(db.Conference.name.like(name_like))


def query_for_journal(name_like):
    return db.Document.query.join(db.Journal).filter(db.Journal.name.like(name_like))

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
    return "%s -c -f %s | %s -Goverlap=prism -Goutputorder=edgesfirst -Gsize=60,60! | %s -e  -s -4 | %s -Gforcelabels=false -Ecolor=grey  -Gsize=60,60! -n2 -T%s" % (gvpr, labels_path, sfdp if USE_SFDP_FOR_LAYOUT else neato, gvmap, neato, file_format)


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
    proc = Popen(graphviz_command(file_format=file_format, **GRAPHVIZ_PARAMS), stdout=PIPE, stdin=PIPE, shell=True)
    map_out, map_err = proc.communicate(input=map_string)
    return map_out


def function_help(calling_function):
    """can be called on the call_* functions to get a list of the different algorithms they can use"""
    return '\n'.join([str(index) + ':' + str(fn)
                      for index, fn in enumerate(calling_function.functions)])


def _make_arg_filter(passthrough_dict):
    """takes a dictionary of argname, type and returns a function that will
    take a dictionary and return the arguments in the dictionary also in
    passthrough_dict, cast to the type that arg is mapped to in passthrough_dict"""
    def filter_args(args):
        pass_args = {}
        for arg, type_ in passthrough_dict.items():
            if arg in args:
                pass_args[arg] = type_(args[arg])
        return pass_args
    return filter_args

"""used to filter arguments passed in through a request that should also
be passed as keyword args to basemake_map"""
filter_basemap_args = _make_arg_filter(
    {
        'basemap_ending_year': int,
        'basemap_sample_size': int,
        'basemap_starting_year': int,
        'number_of_terms': int,
        'ranking_algorithm': int,
        'similarity_algorithm': int,
        'filtering_algorithm': int
    }
)

"""used to filter arguments passed in through a request that should also
be passed as keyword args to heatmap_map"""
filter_heatmap_args = _make_arg_filter(
    {
        'heatmap_starting_year': int,
        'heatmap_ending_year': int,
        'heatmap_sample_size': int
    }
)
