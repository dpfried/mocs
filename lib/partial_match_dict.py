import utils

class PartialMatchDict():
    def __init__(self):
        self.partial_keys_to_values = {}
        self.full_keys_to_values = {}

    def __setitem__(self, key, item):
        self.full_keys_to_values[key] = item
        for partial in utils.sub_lists(key, proper=False):
            if partial in self.partial_keys_to_values:
                self.partial_keys_to_values[partial].add(item)
            else:
                s = set()
                s.add(item)
                self.partial_keys_to_values[partial] = s

    def __contains__(self, key):
        for partial in utils.sub_lists(key, proper=False):
            if partial in self.partial_keys_to_values:
                return True
        return False

    def __getitem__(self, key):
        matches = set()
        for partial in utils.sub_lists(key, proper=False):
            if partial in self.partial_keys_to_values:
                for match in self.partial_keys_to_values[partial]:
                    matches.add(match)
        return matches

    def __delitem__(self, key):
        del(self.full_keys_to_values[key])
        for partial in utils.sub_lists(key, proper=False):
            if partial in self.partial_keys_to_values:
                del(self.partial_keys_to_values[partial])
