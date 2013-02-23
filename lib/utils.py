import random
import operator

def sample_iterable(iterable, sampling_rate, seed=None):
    if seed:
        random.seed(seed)
    for it in iterable:
        if random.random() < sampling_rate:
            yield it

def sub_lists(lst, min_length = 1, proper=True):
    l = len(lst)
    if not proper:
        yield tuple(lst)
    for i in range(l - 1, min_length - 1, -1):
        for j in range(0, l - i + 1):
            yield tuple(list(lst)[j:j+i])

def sort_dict(dictionary, reverse=False):
    return sorted(dictionary.iteritems(), key=lambda p: p[1], reverse=reverse)

def density(matrix):
    return float((matrix != 0).sum()) / operator.mul(*matrix.shape)

def avg_load(matrix):
    return (matrix != 0).sum(0).mean()

def hashable(x):
    if type(x) is list:
        return tuple(x)
    return x

def first(fn, seq):
    return (s for s in seq if fn(s)).next()

def flatten(lists):
    """flatten a list of lists by one level. [[1,2], [3,4], [[5],6]] -> [1,2,3,4,[5],6]"""
    return [x for lst in lists for x in lst]
