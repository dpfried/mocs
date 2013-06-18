from sqlalchemy import Column, Integer, Boolean, UnicodeText, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import engine, Session, ManagedSession, sliced_query, Base, generalize

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

### models start here ###
class Grant(SDBBase):
    __tablename__ = 'sdb_grant'
    id = Column(Integer, primary_key=True)
    sdb_id = Column(Integer)
    award_number = Column(Integer)
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
    institution = relationship('sdb_institution', backref='grants')

    def __unicode__(self):
        return u'(%s, %s, %s, %s)' % (self.title, self.year, self.terms, self.clean)

    def terms_list(self):
        """ read the serialized terms list and return a list of tuples, which are this doc's terms """
        t_list = []
        if self.terms is not None:
            for p in self.terms.split(','):
                s = tuple(p.split())
                if s:
                    t_list.append(s)
        return t_list

class Author(SDBBase):
    __tablename__ = 'sdb_author'
    id = Column(Integer, primary_key=True)
    first_name = Column(UnicodeText)
    middle_name = Column(UnicodeText)
    last_name = Column(UnicodeText)
    name = Column(UnicodeText)

    def __init__(self, **kwargs):
        self(**kwargs)
        first = kwargs.get('first_name')
        middle = kwargs.get('middle_name')
        last = kwargs.get('last_name')
        # concatenate all the names that we have
        if first or middle or last:
            names = filter(lambda x: x, [first, middle, last])
            self.name = ' '.join(names)

    def __unicode__(self):
        return u'%s' % self.name

class Institution(SDBBase, GrantFilterable):
    """Institutions can have multiple grants, backreferenced through Institution.grants (see Grant class)"""
    __tablename__ = 'sdb_institution'
    id = Column(Integer, primary_key=True)
    sdb_id = Column(Integer)
    name = Column(UnicodeText)

    # @classmethod
    # def name_like_top(cls, name_like, n=10):
    #     with ManagedSession() as session:
    #         try:
    #             stmt = session.query(Document.journal_id, func.count('*').label('doc_count'))\
    #                     .group_by(Document.journal_id)\
    #                     .subquery()
    #             return session.query(Journal, stmt.c.doc_count)\
    #                     .filter(Journal.name.like(name_like))\
    #                     .outerjoin(stmt, Journal.id == stmt.c.journal_id)\
    #                     .order_by('doc_count DESC').slice(0, n).all()
    #         except:
    #             session.rollback()
    #             raise


    def __unicode__(self):
        return u'%s' % self.name

if __name__ == '__main__':
    engine.echo = True
    create_all()
