import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql+psycopg2://hacker@localhost/hacker', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

from git import Git

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
    _git = None

    def __init__(self, uid, name, parent=None):
        self.uid = uid
        self.name = name
        self.parent = parent

    def __repr__(self):
        return '<Playlist %r %r>' % (self.name, self.path)

    def initGit(self, id):
        if self.parent:
            parentGit = Git(self.parent)
            self._git = parentGit.fork(id)
        else:
            self._git = Git(id)

    def git(self):
        if self._git is None:
            self._git = Git(self.id)
        return self._git

    def toDict(self, with_songs=False):
        info = {
            'id': self.id,
            'uid': self.uid,
            'name': self.name,
            'parent': self.parent,
            'create_date': self.create_date,
        }

        if with_songs:
            # Load in song info
            songs = self.git().getTrackIds()
            info['songs'] = songs

        return info

    def getLog(self):
        return self.git.log()

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    activity_date = Column(DateTime, default=datetime.datetime.now)
    description = Column(String(255))

    def __init__(self, uid, description):
        self.uid = uid
        self.description = description

    def __repr__(self):
        return '<Activity %r>' % self.id

    def toDict(self):
        return {
            'id': self.id,
            'user': User.query.filter(User.id == self.uid).first().toDict(),
            'activity_date': self.activity_date,
            'description': self.description,
        }

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    token = Column(String(100))
    icon = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))

    def __init__(self, username, token, icon, first_name, last_name):
        self.username = username
        self.token = token
        self.icon = icon
        self.first_name = first_name
        self.last_name = last_name

    def toDict(self):
        return {
            'username': self.username,
            'icon': self.icon,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

    def __repr__(self):
        return self.toDict()

def init_db():
    Base.metadata.create_all(bind=engine)
