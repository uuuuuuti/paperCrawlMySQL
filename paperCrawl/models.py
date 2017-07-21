from sqlalchemy import create_engine, Column, Integer, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from paperCrawl.settings import MYSQL_URI

Base = declarative_base()


def db_connect():
    return create_engine(MYSQL_URI, encoding='utf-8')


def create_table(engine):
    Base.metadata.create_all(engine)


class Paper(Base):
    __tablename__ = 'paper'

    id = Column(String(255), primary_key=True)
    title = Column(String(255))
    summary = Column(TEXT)
    journal_id = Column(String(255))
    journal_name = Column(String(255))
    pub_date = Column(String(255))
    author_ids = Column(TEXT)
    author_names = Column(TEXT)
    doi = Column(String(255))
    db_code = Column(String(255))
    db_name = Column(String(255))
    categorys = Column(String(255))
    org_names = Column(TEXT)
    org_ids = Column(TEXT)
    keywords = Column(String(255))
    funds = Column(String(255))
    quote_num = Column(Integer)
    quote2_num = Column(Integer)
    download_num = Column(Integer)
    url = Column(String(255))


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer,primary_key=True)
    name = Column(String(255))
    unit_id = Column(String(255))
    unit_name = Column(String(255))
    domains = Column(String(255)) #split with ,
    url = Column(String(255))

class Unit(Base):
    __tablename__ = 'unit'
    id = Column(String(255),primary_key=True)
    name = Column(String(255))
    location = Column(String(255))
    url = Column(String(255))


class Journal(Base):
    __tablename__ = 'journal'

    id = Column(String(255),primary_key= True)
    name = Column(String(255))
    en_name = Column(String(255))
    issn = Column(String(255))
    levels = Column(String(255))
    db_code = Column(String(255))
    impact_factor = Column(String(255))
    search_index = Column(String(255))
    papers_num = Column(String(255))
    quote_num = Column(String(255))
    pub_cycle = Column(String(255))

'''


class Proceeding(Base):
    __tablename__ = 'proceedings'

    id = Column(String(255),primary_key=True)


class Docmas(Base):
    __tablename__ = 'docmas'

    id = Column(String(255), primary_key=True)


class Conference(Base):
    __tablename__ = 'conference'

    id = Column(String(255), primary_key=True)


'''