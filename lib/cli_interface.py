#!/usr/bin/python
from pipeline import map_representation, strip_dimensions, call_graphviz, call_rank,\
    call_similarity, call_filter, function_help, TermExtraction, extract_terms
from database import ManagedSession
from mocs_database import create_query, filter_query
import write_dot

debug = False
def make_map(query, only_terms=False, file_format='svg',
             include_svg_dimensions=False, starting_year=None,
             ending_year=None, sample_size=None, evaluation_output_path=None,
             term_type=TermExtraction.Phrases, data_dump_path=None, n_layers=0, graph_attrs=None, **kwargs):
    documents = filter_query(query,
                             starting_year=starting_year,
                             ending_year=ending_year,
                             sample_size=sample_size)
    extracted_terms = extract_terms(documents, term_type)
    map_dict, graph_terms, phrase_frequencies, similarities, scored_phrases = map_representation(extracted_terms, data_dump_path=data_dump_path, **kwargs)
    print type(similarities)
    # map_string will be a graphviz-processable string
    print 'here'
    map_string = write_dot.output_pairs_dict(map_dict, False, true_scaling=True, phrase_frequencies=phrase_frequencies, similarities=similarities, phrase_scores=scored_phrases, n_layers=n_layers, graph_attrs=graph_attrs)
    print map_string

    if evaluation_output_path:
        import evaluation
        evaluation.plot_phrase_frequencies(phrase_frequencies, evaluation_output_path)
        evaluation.plot_edge_weight_distribution(map_dict, evaluation_output_path)

    if only_terms:
        return '\n'.join(sorted([' '.join(tpl) for tpl in graph_terms]))
    if file_format == 'raw':
        return map_string
    else:
        map_ = call_graphviz(map_string, file_format)
        if file_format == 'svg' and not include_svg_dimensions:
            return strip_dimensions(map_)
        else:
            return map_

def map_args(args):
    """used to filter arguments passed in on the command line that should also
    be passed as keyword args to make_map"""
    arg_set = set(['starting_year', 'ending_year', 'ranking_algorithm',
                   'similarity_algorithm', 'filtering_algorithm',
                   'number_of_terms', 'include_svg_dimensions', 'file_format',
                   'only_terms', 'sample_size', 'evaluation_output_path', 'n_layers'])
    graphattr_set = set(['layerselect'])
    pass_args = {}
    for arg in arg_set:
        if arg in args:
            pass_args[arg] = args[arg]
    graph_attrs = { key: args[key] for key in graphattr_set if key in args and args[key]}
    pass_args['graph_attrs'] = graph_attrs

    return pass_args

if __name__ == "__main__":
    """takes a map using the given parameters, and prints to standard out"""
    import argparse
    parser = argparse.ArgumentParser(description="make map and save to file")
    parser.add_argument('output_file')
    parser.add_argument('--starting_year', type=int, help='starting year for query (inclusive)')
    parser.add_argument('--ending_year', type=int, help='ending year for query (inclusive)')
    parser.add_argument('--sample_size', default=30000, type=int, help='number of rows to sample')
    parser.add_argument('-r', '--ranking_algorithm', default=call_rank.default, type=int, help=function_help(call_rank))
    parser.add_argument('-s', '--similarity_algorithm', default=call_similarity.default, type=int, help=function_help(call_similarity))
    parser.add_argument('-f', '--filtering_algorithm', default=call_filter.default, type=int, help=function_help(call_filter))
    parser.add_argument('-n', '--number_of_terms', default=1000, type=int, help='number of terms to rank')
    parser.add_argument('--include_svg_dimensions', default=False, action="store_true", help='include width and height attributes in svg file')
    parser.add_argument('--dirty', default=False, action="store_true", help='include documents not marked as clean (no title or not in English)')
    parser.add_argument('--file_format', default='pdf', type=str, help='file format of map. "raw" for graphviz schematic')
    parser.add_argument('--author', default=None, help="string to match author using SQL's like (can use %%)")
    parser.add_argument('--conference', default=None, help="string to match author using SQL's like (can use %%)")
    parser.add_argument('--journal', default=None, help="string to match author using SQL's like (can use %%)")
    parser.add_argument('--only_terms', default=False, action="store_true", help="return a list of terms in the map")
    parser.add_argument('--term_type_name', type=str, default=TermExtraction.names[TermExtraction.Phrases], help="type of term to extract. Options: %s" % (TermExtraction.names))
    parser.add_argument('--debug', default=False, action="store_true", help="print status to stdout")
    parser.add_argument('--evaluation_output_path', help="run evaluation metrics, and dump files to this directory")
    parser.add_argument('--data_dump_path', type=str, help="dump some pickle files to this path")
    parser.add_argument('--n_layers', type=int, default=0)
    parser.add_argument('--layerselect')
    args = vars(parser.parse_args())

    global debug
    debug = args['debug']
    with ManagedSession() as session:
        query = create_query(session, author=args['author'], journal=args['journal'], conference=args['conference'])
        map_output = make_map(query,
                              term_type=TermExtraction.names.index(args['term_type_name']),
                              data_dump_path=args['data_dump_path'],
                              **map_args(args))
    print args['output_file']
    print map_output[:10]
    with open(args['output_file'], 'w') as f:
        f.write(map_output)
