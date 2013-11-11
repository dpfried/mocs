def make_header(**attrs):
    return """graph G {
    forcelabels=false;
    node [label="", shape=plaintext];
    """ + '\n'.join('%s="%s";' % (k, v) for (k, v) in attrs.items())

footer = "}"

def node_string(node, **kwargs):
    if 'fontsize' not in kwargs:
        kwargs = kwargs.copy()
        kwargs['fontsize'] = 14
    params = ", ".join("%s=%s" % (key, value) for key, value in kwargs.items())
    return '"%s" [%s]\n' % (node, params)

def pair_string(name1, name2, **kwargs):
    params = ", ".join("%s=%s" % (key, value) for key, value in kwargs.items())
    return '"%s" -- "%s"[%s]\n' % (name1, name2, params)

def safe_string(tpl):
    try:
        return ' '.join(tpl).replace('\\', '\\\\').replace('"', '\\"').encode('utf8', 'ignore')
    except UnicodeDecodeError:
        return 'UNICODE ERROR'

def output_pairs(labels, dist_matrix, dist_filter=lambda x: x != 1):
    """
    labels   - a hash of indices for array: integer -> string
    dist_matrix - a numpy array of distances
    dist_filter - a function that will be called on each distance. Distance is
                  only written if it returns true
    """
    graph_rep = make_header()
    N = len(labels)
    for i in range(N):
        for j in range(i+1, N):
            if dist_filter(dist_matrix[i][j]):
                graph_rep += pair_string(safe_string(labels[i]), safe_string(labels[j]), len=dist_matrix[i][j], weight=1)
    graph_rep += footer
    return graph_rep

def create_font_size_function(phrase_frequencies, min_size=12, max_size=30):
    min_freq = min(phrase_frequencies.values())
    max_freq = max(phrase_frequencies.values())
    def font_size_from_frequency(freq):
        return int((freq - min_freq) / float(max_freq - min_freq) * (max_size - min_size) + min_size)
    return font_size_from_frequency

def output_pairs_dict(pair_similarity, enlarge_primary=False, heatmap_vals=None, true_scaling=False, phrase_frequencies=None, similarities=None, phrase_scores=None, n_layers=0, graph_attrs=None):
    if not graph_attrs:
        graph_attrs = {}
    if n_layers:
        graph_attrs['layers'] = ':'.join(map(str, range(1, n_layers+1)))
    graph_rep = make_header(**graph_attrs)

    graph_terms = set()
    for term, lst in pair_similarity.items():
        graph_terms.add(term)
        graph_terms.update(term for term, val in lst)

    if true_scaling and phrase_frequencies is not None:
        font_size_from_frequency = create_font_size_function(phrase_frequencies)

    min_freq, max_freq = min(phrase_frequencies.values()), max(phrase_frequencies.values())
    def level_from_freq(freq):
        level = (freq - min_freq) * n_layers / (max_freq - min_freq)
        return max(min(level, n_layers - 1), 0) + 1

    for term in graph_terms:
        if true_scaling:
            fontsize = font_size_from_frequency(phrase_frequencies[term])
        elif enlarge_primary and term in pair_similarity:
            fontsize = 18
        else:
            fontsize = 14
        if heatmap_vals and term in heatmap_vals:
            level = heatmap_vals[term]
        else:
            level = 0
        kwargs = {'level': level, 'fontsize': fontsize}
        if phrase_frequencies:
            kwargs['freq'] = phrase_frequencies[term]
            if n_layers:
                kwargs['layer'] = level_from_freq(phrase_frequencies[term])
        if phrase_scores:
            kwargs['imp'] = phrase_scores[term]
        graph_rep += node_string(safe_string(term), **kwargs)

    for phrase1, pairs in pair_similarity.iteritems():
        if similarities:
            similarity_pairs = dict(similarities[phrase1])
        for phrase2, distance in pairs:
            kwargs = {'sim': similarity_pairs[phrase2]} if similarities else {}
            graph_rep += pair_string(safe_string(phrase1), safe_string(phrase2), len=distance, weight=1, **kwargs)
    graph_rep += footer
    return graph_rep
