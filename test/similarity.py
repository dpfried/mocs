import lib.similarity
import numpy as np

lookups_full = {
    'a': ('A',),
    'b': ('B',),
    'c': ('C',),
    'd': ('D',),
    'e': ('E',)
}

jaccard_full_input = [[lookups_full[term] for term in doc.split()]
                      for doc in ['a b e', 'b', 'b c e', 'a d', 'a b d']]

phrases_to_score = [lookups_full[phrase] for phrase in 'a b c d'.split()]

jaccard_full_output = np.array(
    [[0, 2./5, 0, 2./3],
     [2./5, 0, 1./4, 1./5],
     [0, 1./4, 0, 0],
     [2./3, 1./5, 0, 0]]
)

def test_jaccard_full():
    similarity, phrases = lib.similarity.jaccard_full(jaccard_full_input, phrases_to_score)
    # print similarity
    # print jaccard_full_output
    # print similarity.todense() == jaccard_full_output
    assert (similarity.todense() == jaccard_full_output).sum() == 16

if __name__ == "__main__":
    test_jaccard_full()
