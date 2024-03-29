DROP TABLE IF EXISTS songs CASCADE;
CREATE SEQUENCE songs_id_seq;
CREATE TABLE songs (
  id VARCHAR(100) PRIMARY KEY DEFAULT nextval('songs_id_seq'),
  name VARCHAR(100),
  album VARCHAR(100),
  artist VARCHAR(100),
  artwork_url VARCHAR(100),
  key VARCHAR(100) UNIQUE
);

DROP TABLE IF EXISTS playlists CASCADE;
CREATE SEQUENCE playlist_id_seq;
CREATE TABLE playlists (
  id INTEGER PRIMARY KEY DEFAULT nextval('playlist_id_seq'),
  uid INTEGER NOT NULL REFERENCES users (id),
  url VARCHAR(100),
  name VARCHAR(100),
  parent INTEGER REFERENCES playlists (id),
  create_date TIMESTAMP DEFAULT now(),
  key VARCHAR(100),
  description VARCHAR(100)
);

DROP TABLE IF EXISTS users CASCADE;
CREATE SEQUENCE user_id_seq;
CREATE TABLE users (
  id INTEGER PRIMARY KEY DEFAULT nextval('user_id_seq'),
  username VARCHAR(100) UNIQUE,
  key VARCHAR(100),
  icon VARCHAR(100),
  name VARCHAR(100)
);

DROP TABLE IF EXISTS activities CASCADE;
CREATE SEQUENCE activity_id_seq;
CREATE TABLE activities (
    id INTEGER PRIMARY KEY DEFAULT nextval('activity_id_seq'),
    uid INTEGER NOT NULL REFERENCES users (id),
    activity_date TIMESTAMP DEFAULT now(),
    description VARCHAR(255)
);

DROP TABLE IF EXISTS pullrequests CASCADE;
CREATE SEQUENCE pr_id_seq;
CREATE TABLE pullrequests (
    id INTEGER PRIMARY KEY DEFAULT nextval('pr_id_seq'),
    parent_uid INTEGER NOT NULL REFERENCES users (id),
    parent_pid INTEGER NOT NULL REFERENCES playlists (id),
    child_uid INTEGER NOT NULL REFERENCES users (id),
    child_pid INTEGER NOT NULL REFERENCES playlists (id),
    accepted BOOLEAN,
    accepted_on TIMESTAMP,
    requested_on TIMESTAMP
);
