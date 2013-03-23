from web_interface import *
from maps.models import Task, Basemap, Heatmap

author = 'Kwan-Liu Ma'
journal = None
conference = None
basemap_query = create_query(author=author,
                             journal=journal,
                             conference=conference)
basemap_starting_year = 1950
basemap_ending_year = 2013
basemap_sample_size = 30000
number_of_terms = 1500
basemap_term_type = TermExtraction.Phrases

basemap_ids = {}

for ranking_algorithm in ranking_fns:
    for similarity_algorithm in similarity_fns:
        for filtering_algorithm in filtering_fns:
            task_parameters = {
                'basemap_ending_year': basemap_starting_year,
                'basemap_sample_size': basemap_sample_size,
                'basemap_starting_year': basemap_starting_year,
                'number_of_terms': number_of_terms,
                'ranking_algorithm': ranking_algorithm,
                'similarity_algorithm': similarity_algorithm,
                'filtering_algorithm': filtering_algorithm,
                'basemap_author': ('%s' % author),
                'basemap_conference': ('%s' % conference),
                'basemap_journal': ('%s' % journal),
                'basemap_term_type': basemap_term_type,
            }
            basemap_task = create_task_and_maps(task_parameters, include_heatmap=False)
