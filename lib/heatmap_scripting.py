from web_interface import *
from maps.models import Task, Basemap, Heatmap
from pipeline import TermExtraction
from pprint import pprint
import pickle

def make_basemaps(author = None, conference = None, journal = None,
                  basemap_starting_year = 1950, basemap_ending_year = 2013,
                  basemap_sample_size = 30000, number_of_terms = 1500,
                  pickle_filename = '/home/dfried/full_basemap_ids.pickle'):
    basemap_ids = {}

    for basemap_term_type in range(3):
        if basemap_term_type == 1:
            continue
        for ranking_algorithm in range(4):
            for similarity_algorithm in range(3):
                if similarity_algorithm == 0:
                    continue
                for filtering_algorithm in range(2):
                    if filtering_algorithm == 0:
                        continue
                    task_parameters = {
                        'basemap_starting_year': basemap_starting_year,
                        'basemap_ending_year': basemap_ending_year,
                        'basemap_sample_size': basemap_sample_size,
                        'number_of_terms': number_of_terms,
                        'ranking_algorithm': ranking_algorithm,
                        'similarity_algorithm': similarity_algorithm,
                        'filtering_algorithm': filtering_algorithm,
                        'basemap_author': author if author is not None else '',
                        'basemap_conference': conference if conference is not None else '',
                        'basemap_journal': journal if journal is not None else '',
                        'basemap_term_type': basemap_term_type,
                    }
                    basemap_task = create_task_and_maps(task_parameters, include_heatmap=False)
                    basemap_ids[(basemap_term_type, ranking_algorithm, similarity_algorithm, filtering_algorithm)] = basemap_task.basemap.id
                    print 'requesting map for %d:' % basemap_task.id
                    pprint(task_parameters)
                    request_task(basemap_task.id)
                    print 'task finished'

    pprint(basemap_ids)
    with open(pickle_filename, 'w') as f:
        pickle.dump(basemap_ids, f)
    return basemap_ids

def make_single_heatmap(basemap_id, author=None, conference=None, journal=None,
                        heatmap_starting_year=1950, heatmap_ending_year=2013,
                        heatmap_sample_size=4000):
    basemap = Basemap.objects.get(id=basemap_id)
    task_parameters = {
        'heatmap_starting_year': heatmap_starting_year,
        'heatmap_ending_year': heatmap_ending_year,
        'heatmap_sample_size': heatmap_sample_size,
        'heatmap_author': author if author is not None else '',
        'heatmap_conference': conference if conference is not None else '',
        'heatmap_journal': journal if journal is not None else '',
        'heatmap_term_type': basemap.term_type,
    }
    task = create_task_with_existing_basemap(basemap_id, task_parameters)
    request_heatmap(task.id)
    return task.id

def make_heatmaps_date_range(basemap_ids,start,end,increment=5, author=None,
                            conference=None, journal=None, heatmap_sample_size=4000,
                             cumulative=False,
                            pickle_filename='/home/dfried/date_range.pickle'):
    basemap_to_tasks = {}
    year_range = range(start, end, increment)
    for basemap_id in basemap_ids:
        print 'processing basemap %d' % basemap_id
        basemap_to_tasks[basemap_id] = []
        for start_year, end_year in zip(year_range, year_range[1:]+[end]):
            if cumulative:
                start_year = start
            if end_year != end:
                end_year -= 1
            print 'making heatmap for %d - %d' % (start_year, end_year)
            task_id = make_single_heatmap(basemap_id, author=author, conference=conference,
                                          journal=journal, heatmap_starting_year=start_year,
                                          heatmap_ending_year=end_year,
                                          heatmap_sample_size=heatmap_sample_size)
            basemap_to_tasks[basemap_id].append(task_id)
    with open(pickle_filename, 'w') as f:
        pickle.dump(basemap_to_tasks, f)
    return basemap_to_tasks
