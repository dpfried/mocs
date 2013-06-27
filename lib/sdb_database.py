from sqlalchemy import Column, Integer, Boolean, UnicodeText, Date, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import engine, Session, ManagedSession, sliced_query, Base, generalize, stringify_terms
from status import set_status

### configuration ###
echo = False

def create_all():
    SDBBase.metadata.create_all(engine)

SDBBase = declarative_base(cls=Base, constructor=Base._constructor)

class GrantFilterable(object):
    @classmethod
    def join_on_documents(cls, query):
        return query.join(cls)

    @classmethod
    def filter_document_query(cls, query, names):
        joined = cls.join_on_documents(query)
        def _query_for_single_name(session, full_set, name):
            if session.query(cls).filter(cls.name == name).count() > 0:
                print 'found exact match for %s' % (name)
                return full_set.filter(cls.name == name)
            else:
                print 'generalizing to %s' % (generalize(name))
                return full_set.filter(cls.name.like(generalize(name)))

        names_split_stripped = filter(lambda s: s, [name.strip() for name in names.split(';')])
        print names_split_stripped
        with ManagedSession() as session:
            return reduce(lambda x, y: x.union(y),
                          [_query_for_single_name(session, joined, name)
                          for name in names_split_stripped
                           if name])

author_grant_table = Table('sdb_author_grant', SDBBase.metadata,
                              Column('author_id', Integer, ForeignKey('sdb_author.id'), primary_key=True),
                              Column('grant_id', Integer, ForeignKey('sdb_grant.id'), primary_key=True)
                              )

class Unique:
    def uuid(self):
        pass

### models start here ###
class Grant(SDBBase, Unique):
    __tablename__ = 'sdb_grant'
    id = Column(Integer, primary_key=True)
    sdb_id = Column(UnicodeText)
    award_number = Column(UnicodeText)
    date_started = Column(Date)
    date_expires = Column(Date)
    published_year = Column(Integer)
    title = Column(UnicodeText)
    abstract = Column(UnicodeText)
    clean = Column(Boolean)
    terms = Column(UnicodeText)

    authors = relationship('Author',
                           secondary=author_grant_table,
                           backref='grants')
    institution_id = Column(Integer, ForeignKey('sdb_institution.id'))
    institution = relationship('Institution', backref='grants')

    def __unicode__(self):
        return u'(%s, %s, %s, %s)' % (self.sdb_id, self.title, self.terms, self.clean)

    def terms_list(self):
        """ read the serialized terms list and return a list of tuples, which are this doc's terms """
        t_list = []
        if self.terms is not None:
            for p in self.terms.split(','):
                s = tuple(p.split())
                if s:
                    t_list.append(s)
        return t_list

    def uuid(self):
        return self.sdb_id

class Author(SDBBase, Unique):
    __tablename__ = 'sdb_author'
    id = Column(Integer, primary_key=True)
    first_name = Column(UnicodeText)
    middle_name = Column(UnicodeText)
    last_name = Column(UnicodeText)
    name = Column(UnicodeText)

    def set_name(self, **kwargs):
        first = kwargs.get('first_name')
        middle = kwargs.get('middle_name')
        last = kwargs.get('last_name')
        # concatenate all the names that we have
        if first or middle or last:
            names = filter(lambda x: x, [first, middle, last])
            self.name = ' '.join(names)

    def __unicode__(self):
        return u'%s' % self.name

    def uuid(self):
        return self.name

    @classmethod
    def join_on_documents(cls, query):
        return query.join(Author, Grant.authors)

    @classmethod
    def name_like_top(cls, name_like, n=10):
        with ManagedSession() as session:
            try:
                return session.query(Author, func.count(author_grant_table.c.document_id).label('doc_count'))\
                        .filter(Author.name.like(name_like)).join(author_grant_table).group_by(Author).order_by('doc_count DESC').slice(0, n).all()
            except:
                session.rollback()
                raise


class Institution(SDBBase, GrantFilterable, Unique):
    """Institutions can have multiple grants, backreferenced through Institution.grants (see Grant class)"""
    __tablename__ = 'sdb_institution'
    id = Column(Integer, primary_key=True)
    sdb_id = Column(UnicodeText)
    name = Column(UnicodeText)

    @classmethod
    def name_like_top(cls, name_like, n=10):
        with ManagedSession() as session:
            try:
                stmt = session.query(Grant.institution_id, func.count('*').label('doc_count'))\
                        .group_by(Grant.institution_id)\
                        .subquery()
                return session.query(Institution, stmt.c.doc_count)\
                        .filter(Institution.name.like(name_like))\
                        .outerjoin(stmt, Institution.id == stmt.c.institution_id)\
                        .order_by('doc_count DESC').slice(0, n).all()
            except:
                session.rollback()
                raise


    def __unicode__(self):
        return u'%s' % self.name

    def uuid(self):
        return self.sdb_id

def filter_query(query, dirty=False, starting_year=None, ending_year=None,
                 sample_size=None, model=None):
    filtered = query
    if not dirty:
        filtered = query.filter(Grant.clean == True)
    if ending_year is not None:
        filtered = filtered.filter(Grant.published_year <= ending_year)
    if starting_year is not None:
        filtered = filtered.filter(Grant.published_year >= starting_year)
    if model is not None:
        documents_in_set = filtered.count()
        model.documents_in_set = documents_in_set
        set_status('%d documents met filtering criteria' % documents_in_set)
    if sample_size is not None:
        filtered = filtered.order_by(func.rand()).limit(sample_size)
    if model is not None:
        documents_sampled = filtered.count()
        model.documents_sampled = documents_sampled
        set_status('%d documents were sampled' % documents_sampled)
    return filtered

def create_query(session, author=None, institution=None):
    """instersection of author and institution"""
    query = session.query(Grant)
    if author:
        query = Author.filter_document_query(query, author)
    if institution:
        query = Institution.filter_document_query(query, institution)
    return query


if __name__ == '__main__':
    engine.echo = True
    create_all()
