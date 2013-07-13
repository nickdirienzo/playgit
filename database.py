import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://hacker@localhost/hacker', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    album = Column(String(100))
    artist = Column(String(100))
    artwork_url = Column(String(100))
    year = Column(Integer)
    genre = Column(String(100))

    def __init__(self, name, album=None, artist=None, artwork_url=None, year=None, genre=None):
        self.name = name
        self.album = album
        self.artist = artist
        self.artwork_url = artwork_url
        self.year = year
        self.genre = genre

    def __repr__(self):
        return '<Song %r>' % self.name

class Playlist(Base):
    __tablename__ = 'playlists'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String(100))
    parent = Column(Integer)
    create_date = Column(DateTime, default=datetime.datetime.now)
    path = Column(String(100))

    def __init__(self, uid, name, path=None, parent=None):
        self.uid = uid
        self.name = name

        if path is None:
            # TODO (pat) create/clone git repo for this playlist
            pass

        self.path = path
        self.parent = parent

    def __repr__(self):
        return '<Playlist %r %s>' % (self.name, self.path)

    def toDict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'name': self.name,
            'parent': self.parent,
            'create_date': self.create_date,
            'path': self.path
        }

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

def init_db():
    Base.metadata.create_all(bind=engine)
