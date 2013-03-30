header = """graph G {
node [shape=plaintext];
"""

footer = "}"

def node_string(node, level=None, fontsize=14):
    if level is not None:
        return '"%s" [level=%f, fontsize=%s]\n' % (node, level, fontsize)
    else:
        return '"%s" [fontsize=%s]\n' % (node, fontsize)

def pair_string(name1, name2, length, weight):
    return '"%s" -- "%s"[len=%.5f, weight=%d]\n' % (name1, name2, length, weight)

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
    graph_rep = header
    N = len(labels)
    for i in range(N):
        for j in range(i+1, N):
            if dist_filter(dist_matrix[i][j]):
                graph_rep += pair_string(safe_string(labels[i]), safe_string(labels[j]), dist_matrix[i][j], 1)
    graph_rep += footer
    return graph_rep

def create_font_size_function(phrase_frequencies, min_size=12, max_size=30):
    min_freq = min(phrase_frequencies.values())
    max_freq = max(phrase_frequencies.values())
    def font_size_from_frequency(freq):
        return int((freq - min_freq) / float(max_freq - min_freq) * (max_size - min_size) + min_size)
    return font_size_from_frequency

def output_pairs_dict(pair_similarity, enlarge_primary=False, heatmap_vals=None, true_scaling=False, phrase_frequencies=None):
    graph_rep = header

    graph_terms = set()
    for term, lst in pair_similarity.items():
        graph_terms.add(term)
        graph_terms.update(term for term, val in lst)

    if true_scaling and phrase_frequencies is not None:
        font_size_from_frequency = create_font_size_function(phrase_frequencies)

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
        graph_rep += node_string(safe_string(term), level=level, fontsize=fontsize)

    for phrase1, pairs in pair_similarity.iteritems():
        for phrase2, similarity in pairs:
            graph_rep += pair_string(safe_string(phrase1), safe_string(phrase2), similarity, 1)
    graph_rep += footer
    return graph_rep
