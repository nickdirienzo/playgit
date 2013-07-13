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

def transform_track_keys(track_keys):
    print 'TRACK KEYS', track_keys
    tracks = list()
    for track_key in track_keys:
        t = Song.query.filter(Song.key == track_key).first()
        track = dict()
        track['name'] = t.name
        track['album'] = t.album
        track['artist'] = t.artist
        track['artwork_url'] = t.artwork_url
        track['key'] = track_key
        tracks.append(track)
    return tracks

class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    album = Column(String(100))
    artist = Column(String(100))
    artwork_url = Column(String(100))
    key = Column(String(100))

    def __init__(self, name, album=None, artist=None, artwork_url=None, key=None):
        self.name = name
        self.album = album
        self.artist = artist
        self.artwork_url = artwork_url
        self.key = key

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
    key = Column(String(100))
    description = Column(String(100))

    def __init__(self, uid, name, parent=None, key=None, description=None):
        self.uid = uid
        self.name = name
        self.parent = parent
        self.key = key
        self.description = description

    def __repr__(self):
        return '<Playlist %r %r>' % (self.name, self.path)

    def initGit(self):
        if self.parent:
            parentGit = Git(self.parent)
            self._git = parentGit.fork(self.id)
        else:
            self._git = Git(self.id)

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
            'description': self.description,
            'key': self.key
        }

        if with_songs:
            # Load in song info
            songs = self.git().getTrackIds()
            info['songs'] = transform_track_keys(songs)

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
    icon = Column(String(100))
    name = Column(String(100))
    key = Column(String(100))

    def __init__(self, username, key, icon, name):
        self.username = username
        self.icon = icon
        self.name = name
        self.key = key

    def toDict(self):
        return {
            'username': self.username,
            'icon': self.icon,
            'name': self.name
        }

    def __repr__(self):
        return self.toDict()

def init_db():
    Base.metadata.create_all(bind=engine)
