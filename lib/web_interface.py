from maps.models import Task, Basemap, Heatmap
from celery.task import task
from pipeline import create_query, filter_query, calculate_heatmap_values,\
    map_representation, strip_dimensions, call_graphviz, extract_terms
from status import set_status
from utils import flatten, jsonize_phrase_dict
import write_dot
import json

def create_task_and_maps(task_parameters, include_heatmap=True):
    # set up new objects
    basemap = Basemap(finished=False, **filter_basemap_args(task_parameters))
    basemap.save()
    if include_heatmap:
        heatmap = Heatmap(finished=False, **filter_heatmap_args(task_parameters))
        heatmap.save()
        task = Task(basemap=basemap, heatmap=heatmap)
    else:
        task = Task(basemap=basemap)
    task.save()
    return task

def create_task_with_existing_basemap(basemap_id, heatmap_task_parameters):
    basemap = Basemap.objects.get(id=basemap_id)
    heatmap = Heatmap(finished=False, **filter_heatmap_args(heatmap_task_parameters))
    heatmap.save()
    task = Task(basemap=basemap, heatmap=heatmap)
    task.save()
    return task


@task(ignore_result=True)
def request_task(task_id):
    task = Task.objects.get(id=task_id)
    map_dict, graph_terms = make_basemap(task.basemap)
    heatmap_vals = make_heatmap(task.heatmap, graph_terms)

def make_heatmap(heatmap, graph_terms):
    set_status('getting document list', model=heatmap)
    heatmap_query= create_query(author=heatmap.author, conference=heatmap.conference, journal=heatmap.journal)
    filtered_query = filter_query(heatmap_query, dirty=True,
                                  starting_year=heatmap.starting_year,
                                  ending_year=heatmap.ending_year,
                                  sample_size=heatmap.sample_size,
                                  model=heatmap)
    extracted_terms = extract_terms(filtered_query, heatmap.term_type)
    heatmap_terms = flatten(extracted_terms)
    heatmap_vals = calculate_heatmap_values(heatmap_terms, graph_terms)
    heatmap.terms = json.dumps(jsonize_phrase_dict(heatmap_vals, 'intensity'))
    set_status('heatmap complete', model=heatmap)
    heatmap.finished = True
    heatmap.save()
    return heatmap_vals

def make_basemap(basemap):
    set_status('getting document list', model=basemap)
    basemap_query = create_query(author=basemap.author, conference=basemap.conference, journal=basemap.journal)
    documents = filter_query(basemap_query, dirty=False,
                             starting_year=basemap.starting_year,
                             ending_year=basemap.ending_year,
                             sample_size=basemap.sample_size,
                             model=basemap)
    extracted_terms = extract_terms(documents, basemap.term_type)
    map_dict, graph_terms, phrase_frequencies = map_representation(extracted_terms,
                                                                   ranking_algorithm=basemap.ranking_algorithm,
                                                                   similarity_algorithm=basemap.similarity_algorithm,
                                                                   filtering_algorithm=basemap.filtering_algorithm,
                                                                   number_of_terms=basemap.number_of_terms,
                                                                   model=basemap)
    # map_string will be a graphviz-processable string
    map_string = write_dot.output_pairs_dict(map_dict, True).decode('ascii', 'ignore')
    # save to database
    basemap.dot_rep = map_string
    # basemap.phrase_frequencies = json.dumps(jsonize_phrase_dict(phrase_frequencies), indent=4).decode('ascii', 'ignore')
    basemap.save()
    svg_str, width, height = strip_dimensions(call_graphviz(map_string, file_format='svg', model=basemap))
    basemap.svg_rep = svg_str
    basemap.width = width
    basemap.height = height
    basemap.finished = True
    basemap.save()
    set_status('basemap complete', model=basemap)
    return map_dict, graph_terms

def _make_arg_filter(passthrough_dict):
    """takes a dictionary of argname, type and returns a function that will
    take a dictionary and return the arguments in the dictionary also in
    passthrough_dict, cast to the type that arg is mapped to in passthrough_dict"""
    def filter_args(args):
        pass_args = {}
        for arg_name, maps_to in passthrough_dict.items():
            if type(maps_to) is tuple:
                type_, new_arg_name = maps_to
            else:
                type_, new_arg_name = maps_to, arg_name
            if arg_name in args:
                pass_args[new_arg_name] = type_(args[arg_name])
        return pass_args
    return filter_args

"""used to filter arguments passed in through a request that should also
be passed as keyword args to basemake_map"""
filter_basemap_args = _make_arg_filter(
    {
        'basemap_ending_year': (int, "ending_year"),
        'basemap_sample_size': (int, "sample_size"),
        'basemap_starting_year': (int, "starting_year"),
        'number_of_terms': int,
        'ranking_algorithm': int,
        'similarity_algorithm': int,
        'filtering_algorithm': int,
        'basemap_author': (str, 'author'),
        'basemap_conference': (str, 'conference'),
        'basemap_journal': (str, 'journal'),
        'basemap_term_type': (int, 'term_type'),
    }
)

"""used to filter arguments passed in through a request that should also
be passed as keyword args to heatmap_map"""
filter_heatmap_args = _make_arg_filter(
    {
        'heatmap_starting_year': (int, "starting_year"),
        'heatmap_ending_year': (int, "ending_year"),
        'heatmap_sample_size': (int, "sample_size"),
        'heatmap_author': (str, 'author'),
        'heatmap_conference': (str, 'conference'),
        'heatmap_journal': (str, 'journal'),
        'heatmap_term_type': (int, 'term_type'),
    }
)
