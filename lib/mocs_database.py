from sqlalchemy import Column, Integer, Boolean, UnicodeText, Table, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base, engine, generalize, ManagedSession

def create_all():
    MOCSBase.metadata.create_all(engine)

MOCSBase = declarative_base(cls=Base, constructor=Base._constructor)


class DocumentFilterable(object):
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


### models start here ###
# this table allows the many to many relationship between Documents and Authors
author_document_table = Table('author_document', MOCSBase.metadata,
                              Column('author_id', Integer, ForeignKey('author.id'), primary_key=True),
                              Column('document_id', Integer, ForeignKey('document.id'), primary_key=True)
                              )


class Document(MOCSBase):
    """primary class, represents a DBLP entry. Has multiple authors and up to one journal and up to one conference. Most important field is title, from which we extract phrases, and memoize in terms."""
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)

    title = Column(UnicodeText)
    year = Column(Integer)
    terms = Column(UnicodeText)
    clean = Column(Boolean)
    authors = relationship('Author',
                           secondary=author_document_table,
                           backref='documents')
    journal_id = Column(Integer, ForeignKey('journal.id'))
    journal = relationship('Journal', backref='documents')
    conference_id = Column(Integer, ForeignKey('conference.id'))
    conference = relationship('Conference', backref='documents')

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

class Author(MOCSBase,DocumentFilterable):
    """Authors can have multiple papers, backreferenced through Author.documents (see Document class)"""
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def join_on_documents(cls, query):
        return query.join(Author, Document.authors)

    @classmethod
    def name_like_top(cls, name_like, n=10):
        with ManagedSession() as session:
            try:
                return session.query(Author, func.count(author_document_table.c.document_id).label('doc_count'))\
                        .filter(Author.name.like(name_like)).join(author_document_table).group_by(Author).order_by('doc_count DESC').slice(0, n).all()
            except:
                session.rollback()
                raise

    def __unicode__(self):
        return u'%s' % self.name

class Journal(MOCSBase, DocumentFilterable):
    """Journals can have multiple papers, backreferenced through Journal.documents (see Document class)"""
    __tablename__ = 'journal'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def name_like_top(cls, name_like, n=10):
        with ManagedSession() as session:
            try:
                stmt = session.query(Document.journal_id, func.count('*').label('doc_count'))\
                        .group_by(Document.journal_id)\
                        .subquery()
                return session.query(Journal, stmt.c.doc_count)\
                        .filter(Journal.name.like(name_like))\
                        .outerjoin(stmt, Journal.id == stmt.c.journal_id)\
                        .order_by('doc_count DESC').slice(0, n).all()
            except:
                session.rollback()
                raise


    def __unicode__(self):
        return u'%s' % self.name


class Conference(MOCSBase, DocumentFilterable):
    """Conferences can have multiple papers, backreferenced through Conference.documents (see Document class)"""
    __tablename__ = 'conference'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)

    @classmethod
    def name_like_top(cls, name_like, n=10):
        with ManagedSession() as session:
            try:
                stmt = session.query(Document.conference_id, func.count('*').label('doc_count'))\
                        .group_by(Document.conference_id)\
                        .subquery()
                return session.query(Conference, stmt.c.doc_count)\
                        .filter(Conference.name.like(name_like))\
                        .outerjoin(stmt, Conference.id == stmt.c.conference_id)\
                        .order_by('doc_count DESC').slice(0, n).all()
            except:
                session.rollback()
                raise

    def __unicode__(self):
        return u'%s' % self.name

if __name__ == '__main__':
    engine.echo = True
    create_all()
