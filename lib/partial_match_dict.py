from collections import defaultdict

class PartialMatchDict():
    def __init__(self):
        self.atoms_to_values = defaultdict(set)

    def __setitem__(self, key, item):
        for atom in key:
            self.atoms_to_values[atom].add(item)

    def __contains__(self, key):
        return any(atom in self.atoms_to_values
                   for atom in key)

    def __getitem__(self, key):
        return reduce(lambda s, t: s.union(t),
                      (self.atoms_to_values[atom] for atom in key))
