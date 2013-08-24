from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,  scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import _declarative_constructor
from mocs_config import SQL_CONNECTION
from re import sub, compile

### configuration ###
echo = False

### setting up sqlalchemy stuff ###
engine = create_engine(SQL_CONNECTION, echo=echo, pool_recycle=3600)
Session = scoped_session(sessionmaker(bind=engine))

class ManagedSession:
    def __enter__(self):
        self._session = Session()
        return self._session

    def __exit__(self, type, value, traceback):
        self._session.close()

def stringify_terms(list_of_tuples):
    return ','.join(' '.join(tpl) for tpl in list_of_tuples)


### utilities ###
# as seen on http://stackoverflow.com/a/1383402
class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Base(object):
    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    # like in django
    @classmethod
    def get_or_create(cls, defaults={}, **kwargs):
        obj = cls.get_by(**kwargs)
        if not obj:
            kwargs.update(defaults)
            obj = cls(**kwargs)
        return obj

    def _constructor(self, **kwargs):
        _declarative_constructor(self, **kwargs)
        # add self to session
        # session.add(self)

Base = declarative_base(cls=Base, constructor=Base._constructor)
def sliced_query(query, slice_size=10000, session_to_write=None):
    """ takes a SQLAlchemy query and allows memory-efficient iteration over a large
    rowset by buffering. If a session object is passed to session_to_write, will
    commit any changes to that session upon iterating over the number of slices in
    slice_size """
    N = query.count()
    for lower_bound in range(0, N, slice_size):
        upper_bound = min(N, lower_bound + slice_size)
        for record in query.slice(lower_bound, upper_bound):
            yield record
        if session_to_write:
            session_to_write.commit()

if __name__ == '__main__':
    engine.echo = True
    create_all()

generalize_pattern = compile(r'[\s\.]+')
def generalize(query_string):
    generalized = sub(generalize_pattern, '%', query_string)
    if not generalized.startswith('%'):
        generalized = '%' + generalized
    if not generalized.endswith('%'):
        generalized = generalized + '%'
    return generalized
