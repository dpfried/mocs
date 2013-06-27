with open('/home/dfried/Dropbox/MoCS/abstracts/purchase_1997.txt') as f:
    a1 = f.read().strip()
with open('/home/dfried/Dropbox/MoCS/abstracts/eppstein_1999.txt') as f:
    a2 = f.read().strip()
with open('/home/dfried/Dropbox/MoCS/abstracts/wills_1997.txt') as f:
    a3 = f.read().strip()
import lib.chunking
lib.chunking.noun_phrases(a1)
with open('/home/dfried/Dropbox/MoCS/abstracts/purchase_1997.txt') as f:
    a1 = f.read().strip()
with open('/home/dfried/Dropbox/MoCS/abstracts/eppstein_1999.txt') as f:
    a2 = f.read().strip()
with open('/home/dfried/Dropbox/MoCS/abstracts/wills_1997.txt') as f:
    a3 = f.read().strip()
p1 = lib.chunking.noun_phrases(a1)
p2 = lib.chunking.noun_phrases(a2)
p3 = lib.chunking.noun_phrases(a3)
p1
p2
p3
from lib.pipeline import calculate_heatmap_values
calculate_heatmap_values(p1)
calculate_heatmap_values(p1, None)
import lib.pipeline
reload(lib.pipeline)
from lib.pipeline import calculate_heatmap_values
calculate_heatmap_values(p1, None)
from lib.utils import jsonize_phrase_dict
import json
json.dumps(jsonize_phrase_dict(calculate_heatmap_values(p1, None)))
p1 = set(lib.chunking.noun_phrases(a1))
p1
calculate_heatmap_values(p1, None)
dict((term, val) for (term, val) in calculate_heatmap_values(p1, None).items() if term in basemap_terms)
import Basemap
from maps.models import Basemap
b = Basemap.get(id=425)
b = Basemap.objects.get(id=425)
b.phrases_in_map
json.loads(b.phrases_in_map)
set(map(tuple,json.loads(b.phrases_in_map))
)
set(map(tuple,json.loads(b.phrases_in_map)))
basemap_terms = set(map(tuple,json.loads(b.phrases_in_map)))
dict((term, val) for (term, val) in calculate_heatmap_values(p1, None).items() if term in basemap_terms)
json.dumps(jsonize_phrase_dict(dict((term, val) for (term, val) in calculate_heatmap_values(p1, None).items() if term in basemap_terms)))
json.dumps(jsonize_phrase_dict(dict((term, val) for (term, val) in calculate_heatmap_values(p1, None).items() if term in basemap_terms), 'intensity'))
a1
json.dumps(jsonize_phrase_dict(dict((term, val) for (term, val) in calculate_heatmap_values(a1, None).items() if term in basemap_terms), 'intensity'))
json.dumps(jsonize_phrase_dict(dict((term, val) for (term, val) in calculate_heatmap_values(p2, None).items() if term in basemap_terms), 'intensity'))
a2
json.dumps(jsonize_phrase_dict(dict((term, val) for (term, val) in calculate_heatmap_values(p3, None).items() if term in basemap_terms), 'intensity'))
