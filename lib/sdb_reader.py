from csv import DictReader

def read_sdb_file(filename):
    with open(filename) as f:
        reader = DictReader(f, delimiter=",")
        return list(reader)

