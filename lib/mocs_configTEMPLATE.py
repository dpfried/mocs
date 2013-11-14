import os.path
# replace this with the path to your sqlite file, or the connection string to a
# SQL database
SQL_CONNECTION = 'sqlite:///' + os.path.abspath('mocs.db')

GRAPHVIZ_PARAMS = {
    # set these if the graphviz binaries aren't in the system path, or to use
    # custom versions
    'sfdp':'sfdp',
    'gvmap':'gvmap',
    'gvpr':'gvpr',
    'neato':'neato',
    #
    'labels_path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'labels.gvpr')
}

# additional path to look for NLTK data in
NLTK_DATA_PATH = None
